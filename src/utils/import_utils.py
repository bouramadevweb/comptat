"""
Utilitaires pour l'import de données (CSV, Excel)
"""
import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImportError(Exception):
    """Exception pour les erreurs d'import"""
    pass


class CSVImporter:
    """Classe pour importer des données depuis un fichier CSV"""

    def __init__(self, file_path: str, delimiter: str = ',', encoding: str = 'utf-8'):
        """
        Initialise l'importateur CSV

        Args:
            file_path: Chemin vers le fichier CSV
            delimiter: Délimiteur (default: ',')
            encoding: Encodage du fichier (default: 'utf-8')
        """
        self.file_path = Path(file_path)
        self.delimiter = delimiter
        self.encoding = encoding

        if not self.file_path.exists():
            raise ImportError(f"Fichier introuvable: {file_path}")

    def read_csv(self) -> List[Dict[str, str]]:
        """
        Lit le fichier CSV et retourne une liste de dictionnaires

        Returns:
            Liste de dictionnaires (une ligne = un dict)
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                rows = list(reader)
                logger.info(f"✅ {len(rows)} lignes lues depuis {self.file_path.name}")
                return rows
        except UnicodeDecodeError:
            # Retry avec encoding latin-1 si utf-8 échoue
            logger.warning(f"⚠️ Échec encodage UTF-8, essai avec latin-1")
            try:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    reader = csv.DictReader(f, delimiter=self.delimiter)
                    rows = list(reader)
                    logger.info(f"✅ {len(rows)} lignes lues (latin-1)")
                    return rows
            except Exception as e:
                raise ImportError(f"Erreur de lecture: {e}")
        except Exception as e:
            raise ImportError(f"Erreur de lecture CSV: {e}")

    def validate_headers(self, required_headers: List[str]) -> Tuple[bool, List[str]]:
        """
        Valide que le CSV contient les colonnes requises

        Args:
            required_headers: Liste des colonnes requises

        Returns:
            (True, []) si OK, (False, [colonnes_manquantes]) sinon
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                actual_headers = set(reader.fieldnames or [])

            missing = [h for h in required_headers if h not in actual_headers]

            if missing:
                logger.warning(f"⚠️ Colonnes manquantes: {missing}")
                return False, missing
            else:
                logger.info(f"✅ Toutes les colonnes requises sont présentes")
                return True, []

        except Exception as e:
            logger.error(f"❌ Erreur validation headers: {e}")
            return False, []


class EcritureCSVImporter(CSVImporter):
    """Importateur spécialisé pour les écritures comptables"""

    REQUIRED_HEADERS = [
        'date',           # Date de l'écriture (YYYY-MM-DD)
        'journal',        # Code journal (VE, AC, BQ, OD)
        'numero_piece',   # Numéro de pièce
        'libelle',        # Libellé
        'compte',         # Numéro de compte
        'debit',          # Montant débit
        'credit'          # Montant crédit
    ]

    OPTIONAL_HEADERS = [
        'tiers',          # Code tiers (optionnel)
    ]

    def validate(self) -> Tuple[bool, str]:
        """
        Valide le fichier CSV

        Returns:
            (True, 'OK') si valide, (False, 'message erreur') sinon
        """
        # Vérifier les headers
        is_valid, missing = self.validate_headers(self.REQUIRED_HEADERS)

        if not is_valid:
            return False, f"Colonnes manquantes: {', '.join(missing)}"

        # Lire et valider quelques lignes
        try:
            rows = self.read_csv()

            if not rows:
                return False, "Fichier vide"

            # Valider la première ligne
            first_row = rows[0]

            # Vérifier le format de date
            try:
                datetime.strptime(first_row['date'], '%Y-%m-%d')
            except ValueError:
                return False, f"Format de date invalide (attendu: YYYY-MM-DD): {first_row['date']}"

            # Vérifier les montants
            try:
                debit = self._parse_decimal(first_row['debit'])
                credit = self._parse_decimal(first_row['credit'])
            except (ValueError, InvalidOperation):
                return False, f"Montants invalides (ligne 1)"

            return True, f"✅ Fichier valide ({len(rows)} lignes)"

        except Exception as e:
            return False, f"Erreur de validation: {e}"

    def import_ecritures(self, service, societe_id: int, exercice_id: int) -> Tuple[int, int, List[str]]:
        """
        Importe les écritures dans la base

        Args:
            service: Service comptable
            societe_id: ID de la société
            exercice_id: ID de l'exercice

        Returns:
            (nb_success, nb_errors, messages_erreur)
        """
        rows = self.read_csv()

        nb_success = 0
        nb_errors = 0
        errors = []

        # Grouper les lignes par écriture (même date + même numéro de pièce)
        ecritures_grouped = {}

        for idx, row in enumerate(rows, start=1):
            try:
                key = (row['date'], row['numero_piece'], row['journal'])

                if key not in ecritures_grouped:
                    ecritures_grouped[key] = {
                        'date': row['date'],
                        'numero_piece': row['numero_piece'],
                        'journal': row['journal'],
                        'libelle': row['libelle'],
                        'mouvements': []
                    }

                # Ajouter le mouvement
                ecritures_grouped[key]['mouvements'].append({
                    'compte': row['compte'],
                    'debit': self._parse_decimal(row['debit']),
                    'credit': self._parse_decimal(row['credit']),
                    'tiers': row.get('tiers', ''),
                    'libelle': row.get('libelle_mouvement', row['libelle'])
                })

            except Exception as e:
                nb_errors += 1
                errors.append(f"Ligne {idx}: {str(e)}")
                logger.error(f"❌ Erreur ligne {idx}: {e}")

        # Créer les écritures
        for key, ecriture_data in ecritures_grouped.items():
            try:
                # Récupérer le journal
                journaux = service.get_journaux(societe_id)
                journal = next((j for j in journaux if j.code == ecriture_data['journal']), None)

                if not journal:
                    raise ImportError(f"Journal introuvable: {ecriture_data['journal']}")

                # Créer l'écriture
                from src.domain.models import Ecriture, Mouvement

                mouvements = []
                for mvt_data in ecriture_data['mouvements']:
                    # Récupérer le compte
                    compte = service.compte_dao.get_by_numero(societe_id, mvt_data['compte'])
                    if not compte:
                        raise ImportError(f"Compte introuvable: {mvt_data['compte']}")

                    # Récupérer le tiers si spécifié
                    tiers_id = None
                    if mvt_data['tiers']:
                        tiers_list = service.get_tiers(societe_id)
                        tiers = next((t for t in tiers_list if t.code_aux == mvt_data['tiers']), None)
                        if tiers:
                            tiers_id = tiers.id

                    mouvements.append(Mouvement(
                        compte_id=compte.id,
                        tiers_id=tiers_id,
                        libelle=mvt_data['libelle'],
                        debit=mvt_data['debit'],
                        credit=mvt_data['credit']
                    ))

                ecriture = Ecriture(
                    societe_id=societe_id,
                    exercice_id=exercice_id,
                    journal_id=journal.id,
                    date_ecriture=datetime.strptime(ecriture_data['date'], '%Y-%m-%d').date(),
                    reference_piece=ecriture_data['numero_piece'],
                    libelle=ecriture_data['libelle'],
                    mouvements=mouvements
                )

                # Enregistrer
                success, message, ecriture_id = service.create_ecriture(ecriture)

                if success:
                    nb_success += 1
                    logger.info(f"✅ Écriture créée: {ecriture_data['numero_piece']}")
                else:
                    nb_errors += 1
                    errors.append(f"Écriture {ecriture_data['numero_piece']}: {message}")
                    logger.error(f"❌ {message}")

            except Exception as e:
                nb_errors += 1
                errors.append(f"Écriture {ecriture_data['numero_piece']}: {str(e)}")
                logger.error(f"❌ Erreur création écriture: {e}")

        return nb_success, nb_errors, errors

    def _parse_decimal(self, value: str) -> Decimal:
        """
        Parse une valeur en Decimal

        Args:
            value: Valeur string (peut contenir espaces, virgules)

        Returns:
            Decimal
        """
        if not value or value.strip() == '':
            return Decimal('0')

        # Nettoyer: enlever espaces, remplacer virgule par point
        cleaned = value.strip().replace(' ', '').replace(',', '.')

        try:
            return Decimal(cleaned)
        except (ValueError, InvalidOperation) as e:
            raise ImportError(f"Montant invalide: '{value}'") from e


def create_sample_csv(file_path: str):
    """
    Crée un fichier CSV exemple pour l'import d'écritures

    Args:
        file_path: Chemin où créer le fichier
    """
    sample_data = [
        {
            'date': '2025-01-15',
            'journal': 'VE',
            'numero_piece': 'FACT-001',
            'libelle': 'Vente marchandises Client A',
            'compte': '411000',
            'debit': '1200.00',
            'credit': '0',
            'tiers': 'CLT0001'
        },
        {
            'date': '2025-01-15',
            'journal': 'VE',
            'numero_piece': 'FACT-001',
            'libelle': 'Vente marchandises Client A',
            'compte': '707000',
            'debit': '0',
            'credit': '1000.00',
            'tiers': ''
        },
        {
            'date': '2025-01-15',
            'journal': 'VE',
            'numero_piece': 'FACT-001',
            'libelle': 'TVA 20%',
            'compte': '445710',
            'debit': '0',
            'credit': '200.00',
            'tiers': ''
        },
    ]

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_data)

    logger.info(f"✅ Fichier exemple créé: {file_path}")
