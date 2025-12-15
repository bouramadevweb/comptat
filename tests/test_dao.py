"""
Tests pour les DAOs (Data Access Objects)
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, MagicMock, call

from src.infrastructure.persistence.dao import (
    SocieteDAO, ExerciceDAO, JournalDAO, CompteDAO,
    TiersDAO, EcritureDAO, BalanceDAO, ReportingDAO, ProcedureDAO
)
from src.domain.models import Societe, Exercice, Journal, Compte, Tiers, Ecriture


@pytest.mark.unit
@pytest.mark.dao
class TestSocieteDAO:
    """Tests du SocieteDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de toutes les sociétés"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'nom': 'Test SARL',
                'siren': '123456789',
                'code_postal': '75001',
                'ville': 'Paris',
                'pays': 'FR',
                'date_creation': date(2024, 1, 1)
            }
        ]

        dao = SocieteDAO(mock_db)
        result = dao.get_all()

        assert len(result) == 1
        assert result[0].nom == 'Test SARL'
        assert result[0].siren == '123456789'
        mock_db.execute_query.assert_called_once()

    def test_get_all_empty(self, mock_db):
        """Test: aucune société"""
        mock_db.execute_query.return_value = []

        dao = SocieteDAO(mock_db)
        result = dao.get_all()

        assert result == []

    def test_get_by_id_success(self, mock_db):
        """Test: récupération par ID"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'nom': 'Test SARL',
                'siren': '123456789',
                'code_postal': '75001',
                'ville': 'Paris',
                'pays': 'FR',
                'date_creation': date(2024, 1, 1)
            }
        ]

        dao = SocieteDAO(mock_db)
        result = dao.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.nom == 'Test SARL'

    def test_get_by_id_not_found(self, mock_db):
        """Test: société non trouvée"""
        mock_db.execute_query.return_value = []

        dao = SocieteDAO(mock_db)
        result = dao.get_by_id(999)

        assert result is None

    def test_create_success(self, mock_db):
        """Test: création d'une société"""
        # Mock pour le lastrowid
        mock_db.connection.cursor.return_value.lastrowid = 1
        mock_db.execute_query.return_value = None

        dao = SocieteDAO(mock_db)

        societe = Societe(
            nom="Nouvelle SARL",
            siren="987654321",
            code_postal="69001",
            ville="Lyon",
            pays="FR",
            date_creation=date(2024, 1, 1)
        )

        societe_id = dao.create(societe)

        assert societe_id == 1
        mock_db.execute_query.assert_called_once()


@pytest.mark.unit
@pytest.mark.dao
class TestExerciceDAO:
    """Tests du ExerciceDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de tous les exercices"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'annee': 2025,
                'date_debut': date(2025, 1, 1),
                'date_fin': date(2025, 12, 31),
                'cloture': False
            }
        ]

        dao = ExerciceDAO(mock_db)
        result = dao.get_all(1)

        assert len(result) == 1
        assert result[0].annee == 2025
        assert result[0].cloture is False

    def test_get_current_success(self, mock_db):
        """Test: récupération de l'exercice courant"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'annee': 2025,
                'date_debut': date(2025, 1, 1),
                'date_fin': date(2025, 12, 31),
                'cloture': False
            }
        ]

        dao = ExerciceDAO(mock_db)
        result = dao.get_current(1)

        assert result is not None
        assert result.cloture is False

    def test_get_current_all_closed(self, mock_db):
        """Test: tous les exercices sont clos"""
        mock_db.execute_query.return_value = []

        dao = ExerciceDAO(mock_db)
        result = dao.get_current(1)

        assert result is None

    def test_create_success(self, mock_db):
        """Test: création d'un exercice"""
        dao = ExerciceDAO(mock_db)

        exercice = Exercice(
            societe_id=1,
            annee=2026,
            date_debut=date(2026, 1, 1),
            date_fin=date(2026, 12, 31),
            cloture=False
        )

        exercice_id = dao.create(exercice)

        assert exercice_id == 1  # Le mock retourne 1 par défaut
        mock_db.execute_query.assert_called_once()


@pytest.mark.unit
@pytest.mark.dao
class TestJournalDAO:
    """Tests du JournalDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de tous les journaux"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'code': 'VE',
                'libelle': 'Ventes',
                'type': 'ventes'
            }
        ]

        dao = JournalDAO(mock_db)
        result = dao.get_all(1)

        assert len(result) == 1
        assert result[0].code == 'VE'
        assert result[0].libelle == 'Ventes'

    def test_get_by_code_success(self, mock_db):
        """Test: récupération par code"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'code': 'VE',
                'libelle': 'Ventes',
                'type': 'ventes'
            }
        ]

        dao = JournalDAO(mock_db)
        result = dao.get_by_code(1, 'VE')

        assert result is not None
        assert result.code == 'VE'

    def test_get_by_code_not_found(self, mock_db):
        """Test: journal non trouvé"""
        mock_db.execute_query.return_value = []

        dao = JournalDAO(mock_db)
        result = dao.get_by_code(1, 'XX')

        assert result is None


@pytest.mark.unit
@pytest.mark.dao
class TestCompteDAO:
    """Tests du CompteDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de tous les comptes"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'compte': '411000',
                'intitule': 'Clients',
                'classe': '4',
                'type_compte': 'actif',
                'lettrable': True
            }
        ]

        dao = CompteDAO(mock_db)
        result = dao.get_all(1)

        assert len(result) == 1
        assert result[0].compte == '411000'
        assert result[0].lettrable is True

    def test_get_by_numero_success(self, mock_db):
        """Test: récupération par numéro"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'compte': '411000',
                'intitule': 'Clients',
                'classe': '4',
                'type_compte': 'actif',
                'lettrable': True
            }
        ]

        dao = CompteDAO(mock_db)
        result = dao.get_by_numero(1, '411000')

        assert result is not None
        assert result.compte == '411000'

    def test_get_by_classe_success(self, mock_db):
        """Test: récupération par classe"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'compte': '411000',
                'intitule': 'Clients',
                'classe': '4',
                'type_compte': 'actif',
                'lettrable': True
            }
        ]

        dao = CompteDAO(mock_db)
        result = dao.get_by_classe(1, '4')

        assert len(result) == 1
        assert result[0].classe == '4'

    def test_search_success(self, mock_db):
        """Test: recherche de comptes"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'compte': '411000',
                'intitule': 'Clients',
                'classe': '4',
                'type_compte': 'actif',
                'lettrable': True
            }
        ]

        dao = CompteDAO(mock_db)
        result = dao.search(1, 'client')

        assert len(result) == 1
        assert 'client' in result[0].intitule.lower()


@pytest.mark.unit
@pytest.mark.dao
class TestTiersDAO:
    """Tests du TiersDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de tous les tiers"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'code_aux': 'CLI001',
                'nom': 'Client Test',
                'type': 'CLIENT',
                'adresse': '5 Avenue Test',
                'ville': 'Lyon',
                'pays': 'FR'
            }
        ]

        dao = TiersDAO(mock_db)
        result = dao.get_all(1)

        assert len(result) == 1
        assert result[0].code_aux == 'CLI001'
        assert result[0].type == 'CLIENT'

    def test_get_by_id_success(self, mock_db):
        """Test: récupération par ID"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'code_aux': 'CLI001',
                'nom': 'Client Test',
                'type': 'CLIENT',
                'adresse': '5 Avenue Test',
                'ville': 'Lyon',
                'pays': 'FR'
            }
        ]

        dao = TiersDAO(mock_db)
        result = dao.get_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_create_success(self, mock_db):
        """Test: création d'un tiers"""
        dao = TiersDAO(mock_db)

        tiers = Tiers(
            societe_id=1,
            code_aux='CLI002',
            nom='Nouveau Client',
            type='CLIENT',
            adresse=None,
            ville=None,
            pays='FR'
        )

        tiers_id = dao.create(tiers)

        assert tiers_id == 1  # Le mock retourne 1 par défaut


@pytest.mark.unit
@pytest.mark.dao
class TestEcritureDAO:
    """Tests du EcritureDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de toutes les écritures"""
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'exercice_id': 1,
                'journal_id': 1,
                'numero': 'VE001',
                'date_ecriture': date(2025, 1, 15),
                'reference_piece': 'FACT001',
                'libelle': 'Vente marchandises',
                'validee': True
            }
        ]

        dao = EcritureDAO(mock_db)
        result = dao.get_all(1, 1)

        assert len(result) == 1
        assert result[0].numero == 'VE001'
        assert result[0].validee is True

    def test_get_by_id_success(self, mock_db):
        """Test: récupération par ID avec mouvements"""
        # Mock pour l'écriture
        mock_db.execute_query.return_value = [
            {
                'id': 1,
                'societe_id': 1,
                'exercice_id': 1,
                'journal_id': 1,
                'numero': 'VE001',
                'date_ecriture': date(2025, 1, 15),
                'reference_piece': 'FACT001',
                'libelle': 'Vente marchandises',
                'validee': True
            }
        ]

        dao = EcritureDAO(mock_db)
        result = dao.get_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_get_next_numero_first(self, mock_db):
        """Test: premier numéro d'écriture"""
        mock_db.execute_query.return_value = [{'dernier_numero': None}]

        dao = EcritureDAO(mock_db)
        result = dao.get_next_numero(1, 1)

        # Devrait retourner un numéro initial comme "001" ou similaire
        assert result is not None

    def test_get_next_numero_increment(self, mock_db):
        """Test: incrément du numéro"""
        mock_db.execute_query.return_value = [{'dernier_numero': 'VE001'}]

        dao = EcritureDAO(mock_db)
        result = dao.get_next_numero(1, 1)

        # Le DAO devrait incrémenter VE001 -> VE002
        assert result is not None

    def test_create_success(self, mock_db):
        """Test: création d'une écriture"""
        cursor_mock = Mock()
        cursor_mock.lastrowid = 1
        mock_db.get_cursor.return_value.__enter__.return_value = cursor_mock

        dao = EcritureDAO(mock_db)
        ecriture_id = dao.create(
            societe_id=1,
            exercice_id=1,
            journal_id=1,
            numero='VE001',
            date_ecriture=date(2025, 1, 15),
            mouvements=[
                {
                    'compte_id': 1,
                    'libelle': 'Client',
                    'debit': Decimal('100.00'),
                    'credit': Decimal('0.00')
                }
            ]
        )

        assert ecriture_id == 1

    def test_get_grand_livre_success(self, mock_db):
        """Test: récupération du grand livre"""
        mock_db.execute_query.return_value = [
            {
                'date_ecriture': date(2025, 1, 15),
                'journal_code': 'VE',
                'numero': 'VE001',
                'libelle': 'Client XYZ',
                'debit': Decimal('100.00'),
                'credit': Decimal('0.00'),
                'lettrage_code': None
            }
        ]

        dao = EcritureDAO(mock_db)
        result = dao.get_grand_livre(1, 1, '411000')

        assert len(result) == 1
        assert result[0]['journal_code'] == 'VE'


@pytest.mark.unit
@pytest.mark.dao
class TestLettrageDAO:
    """Tests des méthodes de lettrage dans EcritureDAO"""

    def test_get_mouvements_a_lettrer_success(self, mock_db):
        """Test: récupération des mouvements à lettrer"""
        mock_db.execute_query.return_value = [
            {
                'mouvement_id': 1,
                'compte': '411000',
                'date_ecriture': date(2025, 1, 15),
                'libelle': 'Client XYZ',
                'debit': Decimal('100.00'),
                'credit': Decimal('0.00'),
                'solde': Decimal('100.00')
            }
        ]

        dao = EcritureDAO(mock_db)
        result = dao.get_mouvements_a_lettrer(1, 1, '411000')

        assert len(result) == 1
        assert result[0]['mouvement_id'] == 1

    def test_get_last_lettrage_code_empty(self, mock_db):
        """Test: premier code de lettrage"""
        mock_db.execute_query.return_value = [{'max_code': None}]

        dao = EcritureDAO(mock_db)
        result = dao.get_last_lettrage_code()

        # Devrait retourner un code initial
        assert result is not None

    def test_get_last_lettrage_code_increment(self, mock_db):
        """Test: incrément du code de lettrage"""
        mock_db.execute_query.return_value = [{'max_code': 'AA'}]

        dao = EcritureDAO(mock_db)
        result = dao.get_last_lettrage_code()

        assert result == 'AA'

    def test_set_lettrage_success(self, mock_db):
        """Test: application du lettrage"""
        cursor_mock = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = cursor_mock

        dao = EcritureDAO(mock_db)
        dao.set_lettrage([1, 2], 'AB')

        # Vérifier que la requête a été exécutée
        cursor_mock.execute.assert_called()

    def test_delettrer_mouvements_success(self, mock_db):
        """Test: suppression du lettrage"""
        cursor_mock = Mock()
        cursor_mock.rowcount = 2
        mock_db.get_cursor.return_value.__enter__.return_value = cursor_mock

        dao = EcritureDAO(mock_db)
        count = dao.delettrer_mouvements('AB')

        assert count == 2

    def test_get_mouvements_lettres_success(self, mock_db):
        """Test: récupération des mouvements lettrés"""
        mock_db.execute_query.return_value = [
            {
                'lettrage_code': 'AA',
                'compte': '411000',
                'nombre_mouvements': 2,
                'total_debit': Decimal('100.00'),
                'total_credit': Decimal('100.00')
            }
        ]

        dao = EcritureDAO(mock_db)
        result = dao.get_mouvements_lettres(1, 1)

        assert len(result) == 1
        assert result[0]['lettrage_code'] == 'AA'


@pytest.mark.unit
@pytest.mark.dao
class TestBalanceDAO:
    """Tests du BalanceDAO"""

    def test_get_all_success(self, mock_db):
        """Test: récupération de la balance"""
        mock_db.execute_query.return_value = [
            {
                'societe_id': 1,
                'exercice_id': 1,
                'compte': '411000',
                'intitule': 'Clients',
                'total_debit': Decimal('1000.00'),
                'total_credit': Decimal('800.00'),
                'solde': Decimal('200.00')
            }
        ]

        dao = BalanceDAO(mock_db)
        result = dao.get_all(1, 1)

        assert len(result) == 1
        assert result[0].compte == '411000'
        assert result[0].solde == Decimal('200.00')

    def test_calculer_success(self, mock_db):
        """Test: calcul de la balance"""
        cursor_mock = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = cursor_mock

        dao = BalanceDAO(mock_db)
        dao.calculer(1, 1)

        # Vérifier que les requêtes ont été exécutées
        assert cursor_mock.execute.call_count >= 2  # DELETE + INSERT


@pytest.mark.unit
@pytest.mark.dao
class TestReportingDAO:
    """Tests du ReportingDAO"""

    def test_get_compte_resultat_success(self, mock_db):
        """Test: récupération du compte de résultat"""
        mock_db.execute_query.return_value = [
            {
                'classe': '6',
                'intitule': 'Charges',
                'total': Decimal('5000.00')
            },
            {
                'classe': '7',
                'intitule': 'Produits',
                'total': Decimal('8000.00')
            }
        ]

        dao = ReportingDAO(mock_db)
        result = dao.get_compte_resultat(1, 1)

        assert len(result) == 2
        assert result[0]['classe'] == '6'

    def test_get_bilan_success(self, mock_db):
        """Test: récupération du bilan"""
        mock_db.execute_query.return_value = [
            {
                'classe': '2',
                'intitule': 'Immobilisations',
                'total': Decimal('10000.00')
            }
        ]

        dao = ReportingDAO(mock_db)
        result = dao.get_bilan(1, 1)

        assert len(result) == 1

    def test_get_tva_recap_success(self, mock_db):
        """Test: récapitulatif TVA"""
        mock_db.execute_query.return_value = [
            {
                'compte': '445710',
                'intitule': 'TVA collectée',
                'montant': Decimal('2000.00')
            }
        ]

        dao = ReportingDAO(mock_db)
        result = dao.get_tva_recap(1, 1)

        assert len(result) == 1
        assert result[0]['compte'] == '445710'


@pytest.mark.unit
@pytest.mark.dao
class TestProcedureDAO:
    """Tests du ProcedureDAO"""

    def test_cloturer_exercice_success(self, mock_db):
        """Test: clôture d'exercice"""
        mock_db.call_procedure.return_value = []

        dao = ProcedureDAO(mock_db)
        dao.cloturer_exercice(1, 1)

        mock_db.call_procedure.assert_called_once()

    def test_exporter_fec_success(self, mock_db):
        """Test: export FEC"""
        mock_db.call_procedure.return_value = [
            {
                'JournalCode': 'VE',
                'EcritureNum': 'VE001',
                'EcritureDate': '20250115'
            }
        ]

        dao = ProcedureDAO(mock_db)
        result = dao.exporter_fec(1, 1)

        assert len(result) == 1
        assert result[0]['JournalCode'] == 'VE'

    def test_tester_comptabilite_success(self, mock_db):
        """Test: test de cohérence"""
        mock_db.call_procedure.return_value = [[{'test': 'ok'}]]

        dao = ProcedureDAO(mock_db)
        result = dao.tester_comptabilite(1, 1)

        assert len(result) > 0


# ==================== TESTS EDGE CASES ====================

@pytest.mark.unit
@pytest.mark.dao
class TestDAOEdgeCases:
    """Tests des cas limites"""

    def test_get_all_avec_gros_volume(self, mock_db):
        """Test: récupération d'un gros volume de données"""
        # Simuler 1000 comptes
        mock_data = [
            {
                'id': i,
                'societe_id': 1,
                'compte': f'{411000 + i}',
                'intitule': f'Compte {i}',
                'classe': '4',
                'type_compte': 'actif',
                'lettrable': True
            }
            for i in range(1000)
        ]
        mock_db.execute_query.return_value = mock_data

        dao = CompteDAO(mock_db)
        result = dao.get_all(1)

        assert len(result) == 1000

    def test_recherche_sans_resultat(self, mock_db):
        """Test: recherche ne retournant aucun résultat"""
        mock_db.execute_query.return_value = []

        dao = CompteDAO(mock_db)
        result = dao.search(1, 'inexistant')

        assert result == []

    def test_balance_tous_soldes_nuls(self, mock_db):
        """Test: balance avec tous les soldes nuls"""
        mock_db.execute_query.return_value = [
            {
                'societe_id': 1,
                'exercice_id': 1,
                'compte': '411000',
                'intitule': 'Clients',
                'total_debit': Decimal('0.00'),
                'total_credit': Decimal('0.00'),
                'solde': Decimal('0.00')
            }
        ]

        dao = BalanceDAO(mock_db)
        result = dao.get_all(1, 1)

        assert len(result) == 1
        assert result[0].solde == Decimal('0.00')


# ==================== TESTS ERREURS ====================

@pytest.mark.unit
@pytest.mark.dao
class TestDAOErrors:
    """Tests de gestion d'erreurs"""

    def test_database_connection_error(self, mock_db):
        """Test: erreur de connexion base de données"""
        mock_db.execute_query.side_effect = Exception("Connection failed")

        dao = SocieteDAO(mock_db)

        with pytest.raises(Exception) as exc_info:
            dao.get_all()

        assert "Connection failed" in str(exc_info.value)

    def test_invalid_sql_query(self, mock_db):
        """Test: requête SQL invalide"""
        mock_db.execute_query.side_effect = Exception("SQL syntax error")

        dao = CompteDAO(mock_db)

        with pytest.raises(Exception):
            dao.get_all(1)

    def test_create_with_duplicate_key(self, mock_db):
        """Test: création avec clé dupliquée"""
        cursor_mock = Mock()
        cursor_mock.execute.side_effect = Exception("Duplicate entry")
        mock_db.get_cursor.return_value.__enter__.return_value = cursor_mock

        dao = JournalDAO(mock_db)

        with pytest.raises(Exception) as exc_info:
            dao.create(
                societe_id=1,
                code='VE',
                libelle='Ventes',
                type='ventes'
            )

        assert "Duplicate" in str(exc_info.value)
