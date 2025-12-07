"""
Services - Logique métier de l'application
VERSION AMÉLIORÉE avec validation, constantes et gestion d'erreurs robuste
"""
from typing import List, Optional, Tuple, Dict
from decimal import Decimal
from datetime import date
from src.domain.models import *
from src.domain.repositories import (
    DatabaseGateway,
    SocieteRepository,
    ExerciceRepository,
    JournalRepository,
    CompteRepository,
    TiersRepository,
    EcritureRepository,
    BalanceRepository,
    ReportingRepository,
    ProcedureRepository,
)
from src.infrastructure.configuration.constants import *
from src.infrastructure.validation.validators import *
import logging

logger = logging.getLogger(__name__)


class ComptabiliteService:
    """Service principal de gestion comptable"""
    
    def __init__(
        self,
        db: DatabaseGateway,
        societe_repo: SocieteRepository,
        exercice_repo: ExerciceRepository,
        journal_repo: JournalRepository,
        compte_repo: CompteRepository,
        tiers_repo: TiersRepository,
        ecriture_repo: EcritureRepository,
        balance_repo: BalanceRepository,
        reporting_repo: ReportingRepository,
        procedure_repo: ProcedureRepository,
    ):
        self.db = db
        self.societe_dao = societe_repo
        self.exercice_dao = exercice_repo
        self.journal_dao = journal_repo
        self.compte_dao = compte_repo
        self.tiers_dao = tiers_repo
        self.ecriture_dao = ecriture_repo
        self.balance_dao = balance_repo
        self.reporting_dao = reporting_repo
        self.procedure_dao = procedure_repo
    
    # ========== GESTION DES SOCIÉTÉS ==========
    
    def get_societes(self) -> List[Societe]:
        """Récupère toutes les sociétés"""
        return self.societe_dao.get_all()
    
    def get_societe(self, societe_id: int) -> Optional[Societe]:
        """Récupère une société par son ID"""
        return self.societe_dao.get_by_id(societe_id)
    
    # ========== GESTION DES EXERCICES ==========
    
    def get_exercices(self, societe_id: int) -> List[Exercice]:
        """Récupère tous les exercices d'une société"""
        return self.exercice_dao.get_all(societe_id)
    
    def get_exercice_courant(self, societe_id: int) -> Optional[Exercice]:
        """Récupère l'exercice en cours"""
        return self.exercice_dao.get_current(societe_id)
    
    # ========== GESTION DES JOURNAUX ==========
    
    def get_journaux(self, societe_id: int) -> List[Journal]:
        """Récupère tous les journaux"""
        return self.journal_dao.get_all(societe_id)
    
    # ========== GESTION DES COMPTES ==========
    
    def get_comptes(self, societe_id: int) -> List[Compte]:
        """Récupère tous les comptes"""
        return self.compte_dao.get_all(societe_id)
    
    def get_comptes_by_classe(self, societe_id: int, classe: str) -> List[Compte]:
        """Récupère les comptes d'une classe"""
        return self.compte_dao.get_by_classe(societe_id, classe)
    
    def search_comptes(self, societe_id: int, search_term: str) -> List[Compte]:
        """Recherche des comptes"""
        return self.compte_dao.search(societe_id, search_term)
    
    # ========== GESTION DES TIERS ==========
    
    def get_tiers(self, societe_id: int, type_tiers: Optional[str] = None) -> List[Tiers]:
        """Récupère les tiers (tous, clients ou fournisseurs)"""
        return self.tiers_dao.get_all(societe_id, type_tiers)

    def get_tiers_by_id(self, tiers_id: int) -> Optional[Tiers]:
        """Récupère un tiers par son ID"""
        return self.tiers_dao.get_by_id(tiers_id)

    def create_tiers(self, tiers: Tiers) -> int:
        """Crée un nouveau tiers"""
        return self.tiers_dao.create(tiers)

    def update_tiers(self, tiers: Tiers) -> Tuple[bool, str]:
        """
        Met à jour un tiers existant
        Retourne: (succès, message)
        """
        try:
            if not tiers.id:
                return False, "❌ ID du tiers manquant"

            # Vérifier que le tiers existe
            existing = self.tiers_dao.get_by_id(tiers.id)
            if not existing:
                return False, f"❌ Tiers {tiers.id} introuvable"

            # Mettre à jour
            success = self.tiers_dao.update(tiers)
            if success:
                return True, f"✅ Tiers {tiers.nom} mis à jour avec succès"
            else:
                return False, "❌ Erreur lors de la mise à jour"

        except Exception as e:
            logger.error(f"❌ Erreur update_tiers: {e}")
            return False, f"❌ Erreur: {str(e)}"

    def delete_tiers(self, tiers_id: int) -> Tuple[bool, str]:
        """
        Supprime un tiers (si non utilisé dans des écritures)
        Retourne: (succès, message)
        """
        try:
            # Vérifier que le tiers existe
            tiers = self.tiers_dao.get_by_id(tiers_id)
            if not tiers:
                return False, f"❌ Tiers {tiers_id} introuvable"

            # Tenter la suppression
            success = self.tiers_dao.delete(tiers_id)
            if success:
                return True, f"✅ Tiers {tiers.nom} supprimé avec succès"
            else:
                return False, "❌ Impossible de supprimer ce tiers (utilisé dans des écritures)"

        except Exception as e:
            logger.error(f"❌ Erreur delete_tiers: {e}")
            return False, f"❌ Erreur: {str(e)}"
    
    # ========== GESTION DES ÉCRITURES ==========
    
    def get_ecritures(self, exercice_id: int, journal_id: Optional[int] = None) -> List[Ecriture]:
        """Récupère les écritures d'un exercice"""
        return self.ecriture_dao.get_all(exercice_id, journal_id)
    
    def get_ecriture(self, ecriture_id: int) -> Optional[Ecriture]:
        """Récupère une écriture complète"""
        return self.ecriture_dao.get_by_id(ecriture_id)
    
    def create_ecriture(self, ecriture: Ecriture) -> Tuple[bool, str, Optional[int]]:
        """
        Crée une nouvelle écriture avec validation complète
        Retourne: (succès, message, ecriture_id)
        """
        try:
            # Récupérer l'exercice pour les dates
            exercice = self.exercice_dao.get_by_id(ecriture.exercice_id)
            if not exercice:
                return False, "❌ Exercice introuvable", None

            # Vérifier que l'exercice n'est pas clôturé
            if exercice.cloture:
                return False, "❌ L'exercice est clôturé, modification impossible", None

            # Validation complète de l'écriture
            validation = ComptabiliteValidator.valider_ecriture_complete(
                mouvements=ecriture.mouvements,
                date_ecriture=ecriture.date_ecriture,
                exercice_debut=exercice.date_debut,
                exercice_fin=exercice.date_fin,
                reference=ecriture.reference_piece or "",
                libelle=ecriture.libelle or ""
            )

            if not validation:
                return False, f"❌ Validation échouée : {validation.message}", None

            # Génération du numéro si vide
            if not ecriture.numero:
                ecriture.numero = self.ecriture_dao.get_next_numero(
                    ecriture.exercice_id,
                    ecriture.journal_id
                )

            # Créer l'écriture
            ecriture_id = self.ecriture_dao.create(ecriture)
            logger.info(f"✅ Écriture {ecriture.numero} créée avec succès (ID: {ecriture_id})")
            return True, f"✅ Écriture {ecriture.numero} créée avec succès", ecriture_id

        except Exception as e:
            logger.error(f"❌ Erreur inattendue : {e}", exc_info=True)
            return False, f"❌ Erreur inattendue : {str(e)}", None
    
    def creer_ecriture_vente(
        self,
        societe_id: int,
        exercice_id: int,
        journal_id: int,
        date_ecriture: date,
        client_id: int,
        montant_ht: Decimal,
        taux_tva: Decimal,
        reference: str,
        libelle: str
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Crée une écriture de vente complète (client, vente, TVA) avec validation
        """
        try:
            # Validation des montants
            validation = ComptabiliteValidator.valider_montant(montant_ht)
            if not validation:
                return False, f"❌ Montant HT invalide : {validation.message}", None

            # Validation du taux de TVA
            validation = ComptabiliteValidator.valider_taux_tva(taux_tva)
            if not validation:
                return False, f"❌ Taux de TVA invalide : {validation.message}", None

            # Calculs
            montant_tva = montant_ht * taux_tva
            montant_ttc = montant_ht + montant_tva

            # Utilisation des constantes pour les comptes
            compte_tva_numero = get_compte_tva_collectee(taux_tva)
            libelle_tva = get_libelle_tva(taux_tva, collectee=True)

            # Recherche des comptes
            compte_client = self.compte_dao.get_by_numero(societe_id, ComptesComptables.CLIENTS)
            compte_vente = self.compte_dao.get_by_numero(societe_id, ComptesComptables.VENTES_MARCHANDISES)
            compte_tva = self.compte_dao.get_by_numero(societe_id, compte_tva_numero)
            if not compte_tva:
                # Fallback sur le compte générique si le compte spécifique n'existe pas
                compte_tva = self.compte_dao.get_by_numero(societe_id, ComptesComptables.TVA_COLLECTEE)

            if not all([compte_client, compte_vente, compte_tva]):
                return False, f"❌ Comptes manquants (Client, Vente ou TVA)", None
        
            # Créer l'écriture
            ecriture = Ecriture(
                societe_id=societe_id,
                exercice_id=exercice_id,
                journal_id=journal_id,
                numero="",  # Sera généré
                date_ecriture=date_ecriture,
                reference_piece=reference,
                libelle=libelle,
                validee=True,
                date_validation=date_ecriture,
                mouvements=[
                    Mouvement(
                        compte_id=compte_client.id,
                        tiers_id=client_id,
                        libelle="Client",
                        debit=montant_ttc,
                        credit=Decimal('0')
                    ),
                    Mouvement(
                        compte_id=compte_vente.id,
                        tiers_id=None,
                        libelle="Vente de marchandises",
                        debit=Decimal('0'),
                        credit=montant_ht
                    ),
                    Mouvement(
                        compte_id=compte_tva.id,
                        tiers_id=None,
                        libelle=libelle_tva,
                        debit=Decimal('0'),
                        credit=montant_tva
                    )
                ]
            )

            return self.create_ecriture(ecriture)

        except Exception as e:
            logger.error(f"❌ Erreur création écriture vente : {e}", exc_info=True)
            return False, f"❌ Erreur : {str(e)}", None
    
    def creer_ecriture_achat(
        self,
        societe_id: int,
        exercice_id: int,
        journal_id: int,
        date_ecriture: date,
        fournisseur_id: int,
        montant_ht: Decimal,
        taux_tva: Decimal,
        reference: str,
        libelle: str
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Crée une écriture d'achat complète (achat, TVA, fournisseur) avec validation
        """
        try:
            # Validation des montants
            validation = ComptabiliteValidator.valider_montant(montant_ht)
            if not validation:
                return False, f"❌ Montant HT invalide : {validation.message}", None

            # Validation du taux de TVA
            validation = ComptabiliteValidator.valider_taux_tva(taux_tva)
            if not validation:
                return False, f"❌ Taux de TVA invalide : {validation.message}", None

            # Calculs
            montant_tva = montant_ht * taux_tva
            montant_ttc = montant_ht + montant_tva

            # Utilisation des constantes pour les comptes
            compte_tva_numero = get_compte_tva_deductible(taux_tva)
            libelle_tva = get_libelle_tva(taux_tva, collectee=False)

            # Recherche des comptes
            compte_achat = self.compte_dao.get_by_numero(societe_id, ComptesComptables.ACHATS_FOURNITURES)
            compte_tva = self.compte_dao.get_by_numero(societe_id, compte_tva_numero)
            if not compte_tva:
                # Fallback sur le compte générique si le compte spécifique n'existe pas
                compte_tva = self.compte_dao.get_by_numero(societe_id, ComptesComptables.TVA_DEDUCTIBLE)
            compte_fournisseur = self.compte_dao.get_by_numero(societe_id, ComptesComptables.FOURNISSEURS)

            if not all([compte_achat, compte_tva, compte_fournisseur]):
                return False, f"❌ Comptes manquants (Achat, TVA ou Fournisseur)", None
        
            ecriture = Ecriture(
                societe_id=societe_id,
                exercice_id=exercice_id,
                journal_id=journal_id,
                numero="",
                date_ecriture=date_ecriture,
                reference_piece=reference,
                libelle=libelle,
                validee=True,
                date_validation=date_ecriture,
                mouvements=[
                    Mouvement(
                        compte_id=compte_achat.id,
                        tiers_id=None,
                        libelle="Achat de marchandises",
                        debit=montant_ht,
                        credit=Decimal('0')
                    ),
                    Mouvement(
                        compte_id=compte_tva.id,
                        tiers_id=None,
                        libelle=libelle_tva,
                        debit=montant_tva,
                        credit=Decimal('0')
                    ),
                    Mouvement(
                        compte_id=compte_fournisseur.id,
                        tiers_id=fournisseur_id,
                        libelle="Fournisseur",
                        debit=Decimal('0'),
                        credit=montant_ttc
                    )
                ]
            )

            return self.create_ecriture(ecriture)

        except Exception as e:
            logger.error(f"❌ Erreur création écriture achat : {e}", exc_info=True)
            return False, f"❌ Erreur : {str(e)}", None
    
    # ========== GESTION DE LA BALANCE ==========
    
    def calculer_balance(self, societe_id: int, exercice_id: int):
        """Recalcule la balance"""
        self.balance_dao.calculer(societe_id, exercice_id)
    
    def get_balance(self, societe_id: int, exercice_id: int) -> List[Balance]:
        """Récupère la balance"""
        return self.balance_dao.get_all(societe_id, exercice_id)
    
    # ========== RAPPORTS ==========
    
    def get_compte_resultat(self, societe_id: int, exercice_id: int) -> dict:
        """Calcule le compte de résultat"""
        rows = self.reporting_dao.get_compte_resultat(societe_id, exercice_id)
        
        charges = []
        produits = []
        total_charges = Decimal('0')
        total_produits = Decimal('0')
        
        for row in rows:
            if row['categorie'] == 'CHARGES':
                charges.append(row)
                total_charges += Decimal(str(row['solde']))
            elif row['categorie'] == 'PRODUITS':
                produits.append(row)
                total_produits += Decimal(str(row['solde']))
        
        resultat = total_produits - total_charges
        
        return {
            'charges': charges,
            'produits': produits,
            'total_charges': total_charges,
            'total_produits': total_produits,
            'resultat': resultat
        }
    
    def get_bilan(self, societe_id: int, exercice_id: int) -> dict:
        """
        Génère le bilan - VERSION CORRIGÉE
        
        ⚠️ IMPORTANT: Classification basée sur le TYPE de compte, pas sur le solde!
        
        Logique:
        - Un compte 401xxx (Fournisseur, type='passif') va TOUJOURS au passif,
          même s'il a un solde débiteur (avance de paiement)
        - Un compte 411xxx (Client, type='actif') va TOUJOURS à l'actif,
          même s'il a un solde créditeur (acompte reçu)
        
        Args:
            societe_id: ID de la société
            exercice_id: ID de l'exercice
            
        Returns:
            dict: {
                'actif': [...],      # Comptes de TYPE 'actif'
                'passif': [...],     # Comptes de TYPE 'passif'
                'total_actif': Decimal,
                'total_passif': Decimal
            }
        """
        results = self.reporting_dao.get_bilan(societe_id, exercice_id)
        
        actif = []
        passif = []
        total_actif = Decimal('0')
        total_passif = Decimal('0')
        
        for row in results:
            ligne = {
                'compte': row['compte'],
                'intitule': row['intitule'],
                'type_compte': row['type_compte'],
                'classe': row['classe'],
                'solde': Decimal(str(row['solde']))
            }
            
            montant_absolu = abs(ligne['solde'])
            
            # ✅ CLASSIFICATION BASÉE SUR LE TYPE DE COMPTE (et non sur le solde!)
            if row['type_compte'] == 'actif':
                # Comptes d'ACTIF (classes 2, 3, et partie de 4 et 5)
                actif.append(ligne)
                total_actif += montant_absolu
                
            elif row['type_compte'] == 'passif':
                # Comptes de PASSIF (classe 1, et partie de 4 et 5)
                passif.append(ligne)
                total_passif += montant_absolu
                
            # Note: Les comptes de type 'charge', 'produit', et 'tva' ne vont pas dans le bilan
            # Ils sont traités respectivement dans le compte de résultat et le récap TVA
        
        return {
            'actif': actif,
            'passif': passif,
            'total_actif': total_actif,
            'total_passif': total_passif
        }
    
    def get_tva_recap(self, societe_id: int, exercice_id: int) -> dict:
        """Récapitulatif TVA"""
        rows = self.reporting_dao.get_tva_recap(societe_id, exercice_id)
        
        tva_collectee = Decimal('0')
        tva_deductible = Decimal('0')
        
        for row in rows:
            solde = abs(Decimal(str(row['solde'])))
            if row['type_tva'] == 'TVA Collectée':
                tva_collectee += solde
            elif row['type_tva'] == 'TVA Déductible':
                tva_deductible += solde
        
        tva_a_payer = tva_collectee - tva_deductible
        
        return {
            'lignes': rows,
            'tva_collectee': tva_collectee,
            'tva_deductible': tva_deductible,
            'tva_a_payer': tva_a_payer
        }
    
    def get_grand_livre(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str
    ) -> List[Dict]:
        """
        Récupère les mouvements d'un compte pour le Grand Livre.
        Encapsule la requête SQL pour éviter que l'UI n'accède directement à l'infrastructure.
        """
        return self.ecriture_dao.get_grand_livre(societe_id, exercice_id, compte_numero)
    
    # ========== PROCÉDURES COMPTABLES ==========
    
    def cloturer_exercice(self, societe_id: int, exercice_id: int) -> Tuple[bool, str]:
        """Clôture un exercice comptable"""
        try:
            self.procedure_dao.cloturer_exercice(societe_id, exercice_id)
            return True, "✅ Exercice clôturé avec succès"
        except Exception as e:
            logger.error(f"❌ Erreur clôture : {e}")
            return False, f"❌ Erreur clôture : {str(e)}"
    
    def exporter_fec(self, societe_id: int, exercice_id: int) -> Tuple[bool, str]:
        """Exporte le FEC"""
        try:
            self.procedure_dao.exporter_fec(societe_id, exercice_id)
            
            # Récupérer le nom du fichier
            societe = self.societe_dao.get_by_id(societe_id)
            exercice = self.exercice_dao.get_by_id(exercice_id)
            filename = f"/tmp/FEC_{societe.siren}_{exercice.annee}.txt"
            
            return True, f"✅ FEC exporté : {filename}"
        except Exception as e:
            logger.error(f"❌ Erreur export FEC : {e}")
            return False, f"❌ Erreur export FEC : {str(e)}"
    
    def tester_comptabilite(self, societe_id: int, exercice_id: int) -> dict:
        """Effectue les tests de cohérence comptable"""
        try:
            results = self.procedure_dao.tester_comptabilite(societe_id, exercice_id)
            if results and results[0]:
                return results[0][0]
            return {}
        except Exception as e:
            logger.error(f"❌ Erreur test comptabilité : {e}")
            return {
                'erreur': str(e),
                'message': 'Impossible d\'exécuter les tests de cohérence'
            }

    # ========== LETTRAGE DES COMPTES ==========

    def get_mouvements_a_lettrer(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str,
        tiers_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Récupère les mouvements non lettrés d'un compte
        Args:
            societe_id: ID de la société
            exercice_id: ID de l'exercice
            compte_numero: Numéro du compte
            tiers_id: ID du tiers (optionnel, pour filtrer)
        Returns:
            Liste des mouvements non lettrés
        """
        try:
            results = self.ecriture_dao.get_mouvements_a_lettrer(
                societe_id,
                exercice_id,
                compte_numero,
                tiers_id
            )
            return results if results else []
        except Exception as e:
            logger.error(f"❌ Erreur récupération mouvements à lettrer : {e}")
            return []

    def lettrer_mouvements(
        self,
        mouvement_ids: List[int],
        code_lettrage: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Lettre plusieurs mouvements ensemble
        Args:
            mouvement_ids: Liste des IDs de mouvements à lettrer
            code_lettrage: Code de lettrage (généré automatiquement si None)
        Returns:
            (succès, message)
        """
        try:
            if len(mouvement_ids) < 2:
                return False, "❌ Au moins 2 mouvements sont nécessaires pour le lettrage"

            # Vérifier l'équilibre des mouvements
            result = self.ecriture_dao.get_aggregat_mouvements(mouvement_ids)

            if not result:
                return False, "❌ Mouvements introuvables"

            solde = Decimal(str(result[0]['solde']))

            if abs(solde) > Limites.TOLERANCE_EQUILIBRE:
                return False, f"❌ Les mouvements ne s'équilibrent pas (solde: {solde})"

            # Générer un code de lettrage si non fourni
            if not code_lettrage:
                last_code = self.ecriture_dao.get_last_lettrage_code()
                code_lettrage = self._next_lettrage_code(last_code) if last_code else "AA"

            # Lettrer les mouvements
            self.ecriture_dao.set_lettrage(mouvement_ids, code_lettrage)

            logger.info(f"✅ {len(mouvement_ids)} mouvements lettrés avec le code {code_lettrage}")
            return True, f"✅ Lettrage effectué avec le code {code_lettrage}"

        except Exception as e:
            logger.error(f"❌ Erreur lettrage : {e}")
            return False, f"❌ Erreur : {str(e)}"

    def delettrer_mouvements(
        self,
        code_lettrage: str
    ) -> Tuple[bool, str]:
        """
        Délètre des mouvements (supprime le lettrage)
        Args:
            code_lettrage: Code de lettrage à supprimer
        Returns:
            (succès, message)
        """
        try:
            nb_updated = self.ecriture_dao.delettrer_mouvements(code_lettrage)

            if nb_updated > 0:
                logger.info(f"✅ {nb_updated} mouvements délettrés (code {code_lettrage})")
                return True, f"✅ {nb_updated} mouvements délettrés"
            else:
                return False, f"❌ Aucun mouvement avec le code {code_lettrage}"

        except Exception as e:
            logger.error(f"❌ Erreur délettrage : {e}")
            return False, f"❌ Erreur : {str(e)}"

    def get_mouvements_lettres(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str
    ) -> Dict[str, List[Dict]]:
        """
        Récupère les mouvements lettrés groupés par code de lettrage
        Returns:
            Dictionnaire {code_lettrage: [mouvements]}
        """
        try:
            results = self.ecriture_dao.get_mouvements_lettres(societe_id, exercice_id, compte_numero)

            grouped = {}
            for row in results:
                code = row['lettrage']
                if code not in grouped:
                    grouped[code] = []
                grouped[code].append(row)

            return grouped

        except Exception as e:
            logger.error(f"❌ Erreur récupération mouvements lettrés : {e}")
            return {}

    def _next_lettrage_code(self, current_code: str) -> str:
        """
        Génère le code de lettrage suivant (AA -> AB -> ... -> ZZ)
        """
        if not current_code or len(current_code) != 2:
            return "AA"

        first, second = current_code

        # Incrémenter
        if second == 'Z':
            if first == 'Z':
                # On a atteint ZZ, recommencer ou ajouter un chiffre
                return "AA1"
            else:
                return chr(ord(first) + 1) + 'A'
        else:
            return first + chr(ord(second) + 1)

    def lettrage_automatique(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str,
        tiers_id: Optional[int] = None
    ) -> Tuple[int, str]:
        """
        Effectue un lettrage automatique des mouvements
        Lettre automatiquement les mouvements qui s'équilibrent parfaitement
        Returns:
            (nombre_lettrages_effectués, message)
        """
        try:
            mouvements = self.get_mouvements_a_lettrer(
                societe_id, exercice_id, compte_numero, tiers_id
            )

            if not mouvements:
                return 0, "ℹ️ Aucun mouvement à lettrer"

            nb_lettrages = 0

            # Algorithme simple : chercher les paires qui s'équilibrent
            i = 0
            while i < len(mouvements):
                mvt1 = mouvements[i]
                solde1 = Decimal(str(mvt1['solde']))

                # Chercher un mouvement qui équilibre
                for j in range(i + 1, len(mouvements)):
                    mvt2 = mouvements[j]
                    solde2 = Decimal(str(mvt2['solde']))

                    if abs(solde1 + solde2) < Limites.TOLERANCE_EQUILIBRE:
                        # Lettrer ces deux mouvements
                        success, msg = self.lettrer_mouvements(
                            [mvt1['mouvement_id'], mvt2['mouvement_id']]
                        )

                        if success:
                            nb_lettrages += 1
                            # Retirer ces mouvements de la liste
                            mouvements.pop(j)
                            mouvements.pop(i)
                            i -= 1
                            break

                i += 1

            if nb_lettrages > 0:
                return nb_lettrages, f"✅ {nb_lettrages} lettrages automatiques effectués"
            else:
                return 0, "ℹ️ Aucun lettrage automatique trouvé"

        except Exception as e:
            logger.error(f"❌ Erreur lettrage automatique : {e}")
            return 0, f"❌ Erreur : {str(e)}"
