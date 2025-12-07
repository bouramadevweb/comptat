"""
Tests pour les services applicatifs
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, call

from src.application.services import ComptabiliteService
from src.domain.models import Societe, Exercice, Journal, Compte, Ecriture, Mouvement


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceSociete:
    """Tests des méthodes liées aux sociétés"""

    def test_get_societes_success(self, comptabilite_service, mock_societe_dao, sample_societe):
        """Test: récupération de toutes les sociétés"""
        mock_societe_dao.get_all.return_value = [sample_societe]

        result = comptabilite_service.get_societes()

        assert len(result) == 1
        assert result[0].nom == "Test SARL"
        mock_societe_dao.get_all.assert_called_once()

    def test_get_societes_empty(self, comptabilite_service, mock_societe_dao):
        """Test: aucune société"""
        mock_societe_dao.get_all.return_value = []

        result = comptabilite_service.get_societes()

        assert result == []

    def test_get_societe_by_id_success(self, comptabilite_service, mock_societe_dao, sample_societe):
        """Test: récupération d'une société par ID"""
        mock_societe_dao.get_by_id.return_value = sample_societe

        result = comptabilite_service.get_societe_by_id(1)

        assert result.nom == "Test SARL"
        assert result.siren == "123456789"
        mock_societe_dao.get_by_id.assert_called_once_with(1)

    def test_get_societe_by_id_not_found(self, comptabilite_service, mock_societe_dao):
        """Test: société inexistante"""
        mock_societe_dao.get_by_id.return_value = None

        result = comptabilite_service.get_societe_by_id(999)

        assert result is None


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceExercice:
    """Tests des méthodes liées aux exercices"""

    def test_get_exercices_success(self, comptabilite_service, mock_exercice_dao, sample_exercice):
        """Test: récupération des exercices"""
        mock_exercice_dao.get_all.return_value = [sample_exercice]

        result = comptabilite_service.get_exercices(1)

        assert len(result) == 1
        assert result[0].annee == 2025
        mock_exercice_dao.get_all.assert_called_once_with(1)

    def test_get_current_exercice_success(self, comptabilite_service, mock_exercice_dao, sample_exercice):
        """Test: récupération de l'exercice courant"""
        mock_exercice_dao.get_current.return_value = sample_exercice

        result = comptabilite_service.get_current_exercice(1)

        assert result.annee == 2025
        assert result.cloture is False
        mock_exercice_dao.get_current.assert_called_once_with(1)

    def test_get_current_exercice_not_found(self, comptabilite_service, mock_exercice_dao):
        """Test: aucun exercice courant"""
        mock_exercice_dao.get_current.return_value = None

        result = comptabilite_service.get_current_exercice(1)

        assert result is None


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceJournal:
    """Tests des méthodes liées aux journaux"""

    def test_get_journaux_success(self, comptabilite_service, mock_journal_dao, sample_journal):
        """Test: récupération des journaux"""
        mock_journal_dao.get_all.return_value = [sample_journal]

        result = comptabilite_service.get_journaux(1)

        assert len(result) == 1
        assert result[0].code == "VE"
        assert result[0].libelle == "Ventes"
        mock_journal_dao.get_all.assert_called_once_with(1)

    def test_get_journal_by_code_success(self, comptabilite_service, mock_journal_dao, sample_journal):
        """Test: récupération d'un journal par code"""
        mock_journal_dao.get_by_code.return_value = sample_journal

        result = comptabilite_service.get_journal_by_code(1, "VE")

        assert result.code == "VE"
        mock_journal_dao.get_by_code.assert_called_once_with(1, "VE")


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceCompte:
    """Tests des méthodes liées aux comptes"""

    def test_get_comptes_success(self, comptabilite_service, mock_compte_dao, sample_compte):
        """Test: récupération de tous les comptes"""
        mock_compte_dao.get_all.return_value = [sample_compte]

        result = comptabilite_service.get_comptes(1)

        assert len(result) == 1
        assert result[0].compte == "411000"
        mock_compte_dao.get_all.assert_called_once_with(1)

    def test_get_compte_by_numero_success(self, comptabilite_service, mock_compte_dao, sample_compte):
        """Test: récupération d'un compte par numéro"""
        mock_compte_dao.get_by_numero.return_value = sample_compte

        result = comptabilite_service.get_compte_by_numero(1, "411000")

        assert result.compte == "411000"
        assert result.intitule == "Clients"
        mock_compte_dao.get_by_numero.assert_called_once_with(1, "411000")

    def test_get_comptes_by_classe_success(self, comptabilite_service, mock_compte_dao, sample_compte):
        """Test: récupération des comptes par classe"""
        mock_compte_dao.get_by_classe.return_value = [sample_compte]

        result = comptabilite_service.get_comptes_by_classe(1, "4")

        assert len(result) == 1
        assert result[0].classe == "4"
        mock_compte_dao.get_by_classe.assert_called_once_with(1, "4")

    def test_search_comptes_success(self, comptabilite_service, mock_compte_dao, sample_compte):
        """Test: recherche de comptes"""
        mock_compte_dao.search.return_value = [sample_compte]

        result = comptabilite_service.search_comptes(1, "client")

        assert len(result) == 1
        mock_compte_dao.search.assert_called_once_with(1, "client")


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceTiers:
    """Tests des méthodes liées aux tiers"""

    def test_get_tiers_success(self, comptabilite_service, mock_tiers_dao, sample_tiers):
        """Test: récupération de tous les tiers"""
        mock_tiers_dao.get_all.return_value = [sample_tiers]

        result = comptabilite_service.get_tiers(1)

        assert len(result) == 1
        assert result[0].code_aux == "CLI001"
        mock_tiers_dao.get_all.assert_called_once_with(1)

    def test_create_tiers_success(self, comptabilite_service, mock_tiers_dao):
        """Test: création d'un tiers"""
        mock_tiers_dao.create.return_value = 1

        success, message = comptabilite_service.create_tiers(
            societe_id=1,
            code_aux="CLI002",
            nom="Nouveau Client",
            type="CLIENT"
        )

        assert success is True
        assert "succès" in message.lower()
        mock_tiers_dao.create.assert_called_once()


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceEcriture:
    """Tests des méthodes liées aux écritures"""

    def test_get_ecritures_success(self, comptabilite_service, mock_ecriture_dao, sample_ecriture):
        """Test: récupération des écritures"""
        mock_ecriture_dao.get_all.return_value = [sample_ecriture]

        result = comptabilite_service.get_ecritures(1, 1)

        assert len(result) == 1
        assert result[0].numero == "VE001"
        mock_ecriture_dao.get_all.assert_called_once_with(1, 1)

    def test_get_next_numero_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: obtenir le prochain numéro d'écriture"""
        mock_ecriture_dao.get_next_numero.return_value = "VE002"

        result = comptabilite_service.get_next_numero(1, 1)

        assert result == "VE002"
        mock_ecriture_dao.get_next_numero.assert_called_once_with(1, 1)

    def test_create_ecriture_validation_error_montant_negatif(self, comptabilite_service):
        """Test: création échoue avec montant négatif"""
        mouvements = [
            {"compte_id": 1, "libelle": "Test", "debit": -100, "credit": 0}
        ]

        success, message = comptabilite_service.create_ecriture(
            societe_id=1,
            exercice_id=1,
            journal_id=1,
            numero="VE001",
            date_ecriture=date(2025, 1, 15),
            mouvements=mouvements
        )

        assert success is False
        assert "montant" in message.lower()

    def test_create_ecriture_validation_error_desequilibre(self, comptabilite_service):
        """Test: création échoue avec écriture déséquilibrée"""
        mouvements = [
            {"compte_id": 1, "libelle": "Débit", "debit": 100, "credit": 0},
            {"compte_id": 2, "libelle": "Crédit", "debit": 0, "credit": 50}  # Déséquilibré
        ]

        success, message = comptabilite_service.create_ecriture(
            societe_id=1,
            exercice_id=1,
            journal_id=1,
            numero="VE001",
            date_ecriture=date(2025, 1, 15),
            mouvements=mouvements
        )

        assert success is False
        assert "équilibr" in message.lower()

    def test_create_ecriture_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: création réussie d'une écriture équilibrée"""
        mock_ecriture_dao.create.return_value = 1

        mouvements = [
            {"compte_id": 1, "libelle": "Client", "debit": 100, "credit": 0},
            {"compte_id": 2, "libelle": "Vente", "debit": 0, "credit": 100}
        ]

        success, message = comptabilite_service.create_ecriture(
            societe_id=1,
            exercice_id=1,
            journal_id=1,
            numero="VE001",
            date_ecriture=date(2025, 1, 15),
            mouvements=mouvements,
            reference_piece="FACT001",
            libelle="Vente"
        )

        assert success is True
        assert "succès" in message.lower()
        mock_ecriture_dao.create.assert_called_once()


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceLettrage:
    """Tests des méthodes de lettrage"""

    def test_get_mouvements_a_lettrer_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: récupération des mouvements à lettrer"""
        mock_data = [
            {
                'mouvement_id': 1,
                'compte': '411000',
                'date_ecriture': date(2025, 1, 15),
                'libelle': 'Client XYZ',
                'debit': Decimal('100.00'),
                'credit': Decimal('0.00')
            }
        ]
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = mock_data

        result = comptabilite_service.get_mouvements_a_lettrer(1, 1, "411000")

        assert len(result) == 1
        assert result[0]['compte'] == '411000'
        mock_ecriture_dao.get_mouvements_a_lettrer.assert_called_once_with(1, 1, "411000")

    def test_lettrer_mouvements_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage de mouvements réussi"""
        mock_ecriture_dao.get_last_lettrage_code.return_value = "AA"
        mock_ecriture_dao.set_lettrage.return_value = None

        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        assert success is True
        assert "succès" in message.lower()
        mock_ecriture_dao.get_last_lettrage_code.assert_called_once()
        mock_ecriture_dao.set_lettrage.assert_called()

    def test_lettrer_mouvements_empty_list(self, comptabilite_service):
        """Test: lettrage avec liste vide"""
        success, message = comptabilite_service.lettrer_mouvements([])

        assert success is False
        assert "mouvement" in message.lower()

    def test_delettrer_mouvements_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: délettrage de mouvements"""
        mock_ecriture_dao.delettrer_mouvements.return_value = 2

        success, message = comptabilite_service.delettrer_mouvements("AB")

        assert success is True
        assert "2" in message
        mock_ecriture_dao.delettrer_mouvements.assert_called_once_with("AB")

    def test_get_mouvements_lettres_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: récupération des mouvements lettrés"""
        mock_data = [
            {
                'lettrage_code': 'AA',
                'compte': '411000',
                'nombre_mouvements': 2,
                'total_debit': Decimal('100.00'),
                'total_credit': Decimal('100.00')
            }
        ]
        mock_ecriture_dao.get_mouvements_lettres.return_value = mock_data

        result = comptabilite_service.get_mouvements_lettres(1, 1)

        assert len(result) == 1
        assert result[0]['lettrage_code'] == 'AA'
        mock_ecriture_dao.get_mouvements_lettres.assert_called_once_with(1, 1)


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceBalance:
    """Tests des méthodes liées à la balance"""

    def test_get_balance_success(self, comptabilite_service, mock_balance_dao, sample_balance):
        """Test: récupération de la balance"""
        mock_balance_dao.get_all.return_value = [sample_balance]

        result = comptabilite_service.get_balance(1, 1)

        assert len(result) == 1
        assert result[0].compte == "411000"
        assert result[0].solde == Decimal("200.00")
        mock_balance_dao.get_all.assert_called_once_with(1, 1)

    def test_calculer_balance_success(self, comptabilite_service, mock_balance_dao):
        """Test: calcul de la balance"""
        mock_balance_dao.calculer.return_value = None

        success, message = comptabilite_service.calculer_balance(1, 1)

        assert success is True
        assert "succès" in message.lower()
        mock_balance_dao.calculer.assert_called_once_with(1, 1)


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceReporting:
    """Tests des méthodes de reporting"""

    def test_get_compte_resultat_success(self, comptabilite_service, mock_reporting_dao):
        """Test: récupération du compte de résultat"""
        mock_data = [
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
        mock_reporting_dao.get_compte_resultat.return_value = mock_data

        result = comptabilite_service.get_compte_resultat(1, 1)

        assert len(result) == 2
        assert result[0]['classe'] == '6'
        assert result[1]['classe'] == '7'
        mock_reporting_dao.get_compte_resultat.assert_called_once_with(1, 1)

    def test_get_bilan_success(self, comptabilite_service, mock_reporting_dao):
        """Test: récupération du bilan"""
        mock_data = [
            {
                'classe': '2',
                'intitule': 'Immobilisations',
                'total': Decimal('10000.00')
            },
            {
                'classe': '4',
                'intitule': 'Créances',
                'total': Decimal('5000.00')
            }
        ]
        mock_reporting_dao.get_bilan.return_value = mock_data

        result = comptabilite_service.get_bilan(1, 1)

        assert len(result) == 2
        mock_reporting_dao.get_bilan.assert_called_once_with(1, 1)

    def test_get_tva_recap_success(self, comptabilite_service, mock_reporting_dao):
        """Test: récupération du récapitulatif TVA"""
        mock_data = [
            {
                'compte': '445710',
                'intitule': 'TVA collectée',
                'montant': Decimal('2000.00')
            },
            {
                'compte': '445660',
                'intitule': 'TVA déductible',
                'montant': Decimal('1000.00')
            }
        ]
        mock_reporting_dao.get_tva_recap.return_value = mock_data

        result = comptabilite_service.get_tva_recap(1, 1)

        assert len(result) == 2
        assert result[0]['compte'] == '445710'
        mock_reporting_dao.get_tva_recap.assert_called_once_with(1, 1)


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceGrandLivre:
    """Tests du grand livre"""

    def test_get_grand_livre_success(self, comptabilite_service, mock_ecriture_dao):
        """Test: récupération du grand livre"""
        mock_data = [
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
        mock_ecriture_dao.get_grand_livre.return_value = mock_data

        result = comptabilite_service.get_grand_livre(1, 1, "411000")

        assert len(result) == 1
        assert result[0]['journal_code'] == 'VE'
        mock_ecriture_dao.get_grand_livre.assert_called_once_with(1, 1, "411000")


@pytest.mark.unit
@pytest.mark.services
class TestComptabiliteServiceProcedures:
    """Tests des procédures stockées"""

    def test_cloturer_exercice_success(self, comptabilite_service, mock_procedure_dao):
        """Test: clôture d'exercice"""
        mock_procedure_dao.cloturer_exercice.return_value = None

        success, message = comptabilite_service.cloturer_exercice(1, 1)

        assert success is True
        assert "succès" in message.lower()
        mock_procedure_dao.cloturer_exercice.assert_called_once_with(1, 1)

    def test_exporter_fec_success(self, comptabilite_service, mock_procedure_dao):
        """Test: export FEC"""
        mock_data = [
            {
                'JournalCode': 'VE',
                'EcritureNum': 'VE001',
                'EcritureDate': '20250115'
            }
        ]
        mock_procedure_dao.exporter_fec.return_value = mock_data

        result = comptabilite_service.exporter_fec(1, 1)

        assert len(result) == 1
        assert result[0]['JournalCode'] == 'VE'
        mock_procedure_dao.exporter_fec.assert_called_once_with(1, 1)

    def test_tester_comptabilite_success(self, comptabilite_service, mock_procedure_dao):
        """Test: test de cohérence comptable"""
        mock_data = [[{'test': 'ok', 'resultat': 'OK'}]]
        mock_procedure_dao.tester_comptabilite.return_value = mock_data

        result = comptabilite_service.tester_comptabilite(1, 1)

        assert len(result) > 0
        mock_procedure_dao.tester_comptabilite.assert_called_once_with(1, 1)


# ==================== TESTS EDGE CASES ====================

@pytest.mark.unit
@pytest.mark.services
class TestServiceEdgeCases:
    """Tests des cas limites"""

    def test_create_ecriture_avec_tolerance_equilibre(self, comptabilite_service, mock_ecriture_dao):
        """Test: écriture avec différence dans la tolérance"""
        mock_ecriture_dao.create.return_value = 1

        mouvements = [
            {"compte_id": 1, "libelle": "Débit", "debit": 100.00, "credit": 0},
            {"compte_id": 2, "libelle": "Crédit", "debit": 0, "credit": 100.005}  # Diff 0.005 < 0.01
        ]

        success, message = comptabilite_service.create_ecriture(
            societe_id=1,
            exercice_id=1,
            journal_id=1,
            numero="VE001",
            date_ecriture=date(2025, 1, 15),
            mouvements=mouvements
        )

        assert success is True

    def test_lettrage_code_increment(self, comptabilite_service, mock_ecriture_dao):
        """Test: incrémentation du code de lettrage"""
        # Premier lettrage: AA -> AB
        mock_ecriture_dao.get_last_lettrage_code.return_value = "AA"
        mock_ecriture_dao.set_lettrage.return_value = None

        success1, _ = comptabilite_service.lettrer_mouvements([1, 2])
        assert success1 is True

        # Second lettrage: AB -> AC
        mock_ecriture_dao.get_last_lettrage_code.return_value = "AB"
        success2, _ = comptabilite_service.lettrer_mouvements([3, 4])
        assert success2 is True

    def test_balance_avec_solde_nul(self, comptabilite_service, mock_balance_dao):
        """Test: balance avec des comptes à solde nul"""
        from src.domain.models import Balance

        balances = [
            Balance(
                societe_id=1,
                exercice_id=1,
                compte="411000",
                intitule="Clients",
                total_debit=Decimal("1000.00"),
                total_credit=Decimal("1000.00"),
                solde=Decimal("0.00")
            )
        ]
        mock_balance_dao.get_all.return_value = balances

        result = comptabilite_service.get_balance(1, 1)

        assert len(result) == 1
        assert result[0].solde == Decimal("0.00")


# ==================== TESTS ERREURS ====================

@pytest.mark.unit
@pytest.mark.services
class TestServiceErrors:
    """Tests de gestion d'erreurs"""

    def test_create_ecriture_exception_handling(self, comptabilite_service, mock_ecriture_dao):
        """Test: gestion d'exception lors de la création"""
        mock_ecriture_dao.create.side_effect = Exception("Database error")

        mouvements = [
            {"compte_id": 1, "libelle": "Débit", "debit": 100, "credit": 0},
            {"compte_id": 2, "libelle": "Crédit", "debit": 0, "credit": 100}
        ]

        success, message = comptabilite_service.create_ecriture(
            societe_id=1,
            exercice_id=1,
            journal_id=1,
            numero="VE001",
            date_ecriture=date(2025, 1, 15),
            mouvements=mouvements
        )

        assert success is False
        assert "erreur" in message.lower()

    def test_lettrer_mouvements_exception(self, comptabilite_service, mock_ecriture_dao):
        """Test: gestion d'exception lors du lettrage"""
        mock_ecriture_dao.get_last_lettrage_code.side_effect = Exception("Database error")

        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        assert success is False
        assert "erreur" in message.lower()

    def test_calculer_balance_exception(self, comptabilite_service, mock_balance_dao):
        """Test: gestion d'exception lors du calcul de balance"""
        mock_balance_dao.calculer.side_effect = Exception("Database error")

        success, message = comptabilite_service.calculer_balance(1, 1)
        

        assert success is False
        assert "erreur" in message.lower()
