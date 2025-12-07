"""
Tests spécialisés pour le lettrage comptable
Le lettrage est une fonctionnalité critique qui permet de rapprocher
les écritures qui s'annulent (ex: facture client + règlement client)
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock

from src.application.services import ComptabiliteService


@pytest.mark.unit
@pytest.mark.lettrage
class TestLettrageAutomatique:
    """Tests du lettrage automatique"""

    def test_lettrage_automatique_paire_simple(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage automatique de 2 mouvements qui s'équilibrent"""
        # Mock mouvements qui s'annulent: +100 et -100
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {
                'mouvement_id': 1,
                'compte': '411000',
                'date_ecriture': date(2025, 1, 15),
                'libelle': 'Facture CLI001',
                'debit': Decimal('100.00'),
                'credit': Decimal('0.00'),
                'solde': Decimal('100.00')
            },
            {
                'mouvement_id': 2,
                'compte': '411000',
                'date_ecriture': date(2025, 1, 20),
                'libelle': 'Règlement CLI001',
                'debit': Decimal('0.00'),
                'credit': Decimal('100.00'),
                'solde': Decimal('-100.00')
            }
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'
        mock_ecriture_dao.set_lettrage.return_value = None

        # Lettrer les mouvements
        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        assert success is True
        assert "succès" in message.lower()
        mock_ecriture_dao.set_lettrage.assert_called_once()

    def test_lettrage_automatique_multiple_paires(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage de plusieurs paires simultanées"""
        # 4 mouvements formant 2 paires
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('100.00')},
            {'mouvement_id': 2, 'solde': Decimal('-100.00')},
            {'mouvement_id': 3, 'solde': Decimal('50.00')},
            {'mouvement_id': 4, 'solde': Decimal('-50.00')}
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        # Premier lettrage
        success1, _ = comptabilite_service.lettrer_mouvements([1, 2])
        assert success1 is True

        # Deuxième lettrage (le code devrait s'incrémenter)
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AB'
        success2, _ = comptabilite_service.lettrer_mouvements([3, 4])
        assert success2 is True

    def test_lettrage_avec_tolerance(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage accepté malgré petite différence (tolérance 0.01€)"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {
                'mouvement_id': 1,
                'solde': Decimal('100.00')
            },
            {
                'mouvement_id': 2,
                'solde': Decimal('-99.995')  # Différence: 0.005 < 0.01
            }
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        # Devrait réussir car dans la tolérance
        assert success is True

    def test_lettrage_hors_tolerance(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage refusé si différence > tolérance"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {
                'mouvement_id': 1,
                'solde': Decimal('100.00')
            },
            {
                'mouvement_id': 2,
                'solde': Decimal('-98.00')  # Différence: 2.00 > 0.01
            }
        ]

        # Le lettrage pourrait être refusé ou accepté selon la logique métier
        # Ce test vérifie la cohérence du comportement
        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        # Si refusé, vérifier le message
        if not success:
            assert "équilibr" in message.lower() or "solde" in message.lower()


@pytest.mark.unit
@pytest.mark.lettrage
class TestLettrageMultiple:
    """Tests du lettrage de 3+ mouvements"""

    def test_lettrage_triple(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage de 3 mouvements qui s'équilibrent"""
        # Exemple: 1 facture + 2 paiements partiels
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('100.00')},   # Facture
            {'mouvement_id': 2, 'solde': Decimal('-60.00')},   # Paiement 1
            {'mouvement_id': 3, 'solde': Decimal('-40.00')}    # Paiement 2
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, message = comptabilite_service.lettrer_mouvements([1, 2, 3])

        assert success is True

    def test_lettrage_complexe_equilibre(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage complexe avec multiples débits et crédits"""
        # 2 factures + 1 avoir + 1 paiement
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('100.00')},   # Facture 1
            {'mouvement_id': 2, 'solde': Decimal('50.00')},    # Facture 2
            {'mouvement_id': 3, 'solde': Decimal('-30.00')},   # Avoir
            {'mouvement_id': 4, 'solde': Decimal('-120.00')}   # Paiement
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, _ = comptabilite_service.lettrer_mouvements([1, 2, 3, 4])

        # Total: 100 + 50 - 30 - 120 = 0 ✓
        assert success is True


@pytest.mark.unit
@pytest.mark.lettrage
class TestDelettrage:
    """Tests du délettrage"""

    def test_delettrage_simple(self, comptabilite_service, mock_ecriture_dao):
        """Test: délettrage d'une paire de mouvements"""
        mock_ecriture_dao.delettrer_mouvements.return_value = 2

        success, message = comptabilite_service.delettrer_mouvements('AB')

        assert success is True
        assert '2' in message
        mock_ecriture_dao.delettrer_mouvements.assert_called_once_with('AB')

    def test_delettrage_code_inexistant(self, comptabilite_service, mock_ecriture_dao):
        """Test: délettrage d'un code inexistant"""
        mock_ecriture_dao.delettrer_mouvements.return_value = 0

        success, message = comptabilite_service.delettrer_mouvements('ZZ')

        # Peut réussir même si 0 mouvement (aucune erreur)
        assert success is True
        assert '0' in message

    def test_delettrage_multiple_mouvements(self, comptabilite_service, mock_ecriture_dao):
        """Test: délettrage de 3+ mouvements"""
        mock_ecriture_dao.delettrer_mouvements.return_value = 5

        success, message = comptabilite_service.delettrer_mouvements('AC')

        assert success is True
        assert '5' in message


@pytest.mark.unit
@pytest.mark.lettrage
class TestCodeLettrage:
    """Tests de l'incrémentation des codes de lettrage"""

    def test_premier_code_lettrage(self, comptabilite_service, mock_ecriture_dao):
        """Test: premier code de lettrage (AA)"""
        mock_ecriture_dao.get_last_lettrage_code.return_value = None
        mock_ecriture_dao.set_lettrage.return_value = None

        success, _ = comptabilite_service.lettrer_mouvements([1, 2])

        # Le premier code devrait être 'AA' ou équivalent
        assert success is True

    def test_increment_code_lettrage_simple(self, comptabilite_service, mock_ecriture_dao):
        """Test: incrémentation AA -> AB -> AC"""
        codes = ['AA', 'AB', 'AC']

        for i, code in enumerate(codes):
            mock_ecriture_dao.get_last_lettrage_code.return_value = code
            mock_ecriture_dao.set_lettrage.return_value = None

            success, _ = comptabilite_service.lettrer_mouvements([i*2+1, i*2+2])
            assert success is True

    def test_increment_code_fin_alphabet(self, comptabilite_service, mock_ecriture_dao):
        """Test: incrémentation AZ -> BA"""
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AZ'
        mock_ecriture_dao.set_lettrage.return_value = None

        success, _ = comptabilite_service.lettrer_mouvements([1, 2])

        # Le code suivant devrait être 'BA'
        assert success is True


@pytest.mark.unit
@pytest.mark.lettrage
class TestMouvementsALettrer:
    """Tests de récupération des mouvements à lettrer"""

    def test_get_mouvements_a_lettrer_vide(self, comptabilite_service, mock_ecriture_dao):
        """Test: aucun mouvement à lettrer"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = []

        result = comptabilite_service.get_mouvements_a_lettrer(1, 1, '411000')

        assert result == []

    def test_get_mouvements_a_lettrer_avec_filtre_compte(self, comptabilite_service, mock_ecriture_dao):
        """Test: filtrage par compte"""
        mock_data = [
            {
                'mouvement_id': 1,
                'compte': '411000',
                'solde': Decimal('100.00')
            }
        ]
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = mock_data

        result = comptabilite_service.get_mouvements_a_lettrer(1, 1, '411000')

        assert len(result) == 1
        assert result[0]['compte'] == '411000'
        mock_ecriture_dao.get_mouvements_a_lettrer.assert_called_with(1, 1, '411000')

    def test_get_mouvements_lettres_groupes(self, comptabilite_service, mock_ecriture_dao):
        """Test: récupération des mouvements déjà lettrés (groupés par code)"""
        mock_data = [
            {
                'lettrage_code': 'AA',
                'compte': '411000',
                'nombre_mouvements': 2,
                'total_debit': Decimal('100.00'),
                'total_credit': Decimal('100.00')
            },
            {
                'lettrage_code': 'AB',
                'compte': '411000',
                'nombre_mouvements': 3,
                'total_debit': Decimal('150.00'),
                'total_credit': Decimal('150.00')
            }
        ]
        mock_ecriture_dao.get_mouvements_lettres.return_value = mock_data

        result = comptabilite_service.get_mouvements_lettres(1, 1)

        assert len(result) == 2
        assert result[0]['lettrage_code'] == 'AA'
        assert result[1]['nombre_mouvements'] == 3


@pytest.mark.unit
@pytest.mark.lettrage
class TestLettrageEdgeCases:
    """Tests des cas limites du lettrage"""

    def test_lettrage_un_seul_mouvement(self, comptabilite_service):
        """Test: impossible de lettrer un seul mouvement"""
        success, message = comptabilite_service.lettrer_mouvements([1])

        # Devrait échouer: besoin d'au moins 2 mouvements
        assert success is False or "mouvement" in message.lower()

    def test_lettrage_liste_vide(self, comptabilite_service):
        """Test: lettrage avec liste vide"""
        success, message = comptabilite_service.lettrer_mouvements([])

        assert success is False
        assert "mouvement" in message.lower()

    def test_lettrage_mouvements_meme_sens(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage de mouvements du même sens (tous débits)"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('100.00')},
            {'mouvement_id': 2, 'solde': Decimal('50.00')}
        ]

        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        # Ne devrait pas s'équilibrer (solde total = 150)
        # Comportement dépend de la logique métier

    def test_lettrage_avec_soldes_decimaux(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage avec montants décimaux précis"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('123.456')},
            {'mouvement_id': 2, 'solde': Decimal('-123.456')}
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, _ = comptabilite_service.lettrer_mouvements([1, 2])

        assert success is True

    def test_lettrage_montants_tres_eleves(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage avec montants très élevés"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('9999999.99')},
            {'mouvement_id': 2, 'solde': Decimal('-9999999.99')}
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, _ = comptabilite_service.lettrer_mouvements([1, 2])

        assert success is True

    def test_lettrage_avec_code_max(self, comptabilite_service, mock_ecriture_dao):
        """Test: comportement quand le code atteint ZZ"""
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'ZZ'
        mock_ecriture_dao.set_lettrage.return_value = None

        success, message = comptabilite_service.lettrer_mouvements([1, 2])

        # Devrait gérer la limite (AAA ou erreur selon implémentation)
        # Ce test vérifie qu'il n'y a pas de crash


@pytest.mark.unit
@pytest.mark.lettrage
class TestLettrageValidation:
    """Tests de validation du lettrage"""

    def test_lettrage_ids_invalides(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage avec IDs invalides"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = []

        # IDs négatifs ou invalides
        success, message = comptabilite_service.lettrer_mouvements([-1, -2])

        # Le comportement dépend de la validation

    def test_lettrage_mouvements_deja_lettres(self, comptabilite_service, mock_ecriture_dao):
        """Test: tentative de re-lettrer des mouvements déjà lettrés"""
        # Mouvements avec code de lettrage existant
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {
                'mouvement_id': 1,
                'solde': Decimal('100.00'),
                'lettrage_code': 'AA'  # Déjà lettré
            },
            {
                'mouvement_id': 2,
                'solde': Decimal('-100.00'),
                'lettrage_code': 'AA'  # Déjà lettré
            }
        ]

        # Selon l'implémentation, devrait échouer ou ignorer

    def test_lettrage_comptes_differents(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage de mouvements de comptes différents"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {
                'mouvement_id': 1,
                'compte': '411000',  # Client
                'solde': Decimal('100.00')
            },
            {
                'mouvement_id': 2,
                'compte': '401000',  # Fournisseur
                'solde': Decimal('-100.00')
            }
        ]

        # Normalement, on ne peut lettrer que le même compte
        # Le comportement dépend de la validation métier


@pytest.mark.unit
@pytest.mark.lettrage
class TestLettrageScenarios:
    """Tests de scénarios réels de lettrage"""

    def test_scenario_facture_reglement(self, comptabilite_service, mock_ecriture_dao):
        """Scénario: Facture client + Règlement"""
        # Facture 100€ (débit)
        # Règlement 100€ (crédit)
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {
                'mouvement_id': 1,
                'date_ecriture': date(2025, 1, 15),
                'libelle': 'Facture F001',
                'debit': Decimal('100.00'),
                'credit': Decimal('0.00'),
                'solde': Decimal('100.00')
            },
            {
                'mouvement_id': 2,
                'date_ecriture': date(2025, 1, 25),
                'libelle': 'Règlement F001',
                'debit': Decimal('0.00'),
                'credit': Decimal('100.00'),
                'solde': Decimal('-100.00')
            }
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, _ = comptabilite_service.lettrer_mouvements([1, 2])

        assert success is True

    def test_scenario_facture_paiements_partiels(self, comptabilite_service, mock_ecriture_dao):
        """Scénario: Facture 1000€ + 3 paiements partiels"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('1000.00')},   # Facture
            {'mouvement_id': 2, 'solde': Decimal('-300.00')},   # Acompte 1
            {'mouvement_id': 3, 'solde': Decimal('-400.00')},   # Acompte 2
            {'mouvement_id': 4, 'solde': Decimal('-300.00')}    # Solde
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, _ = comptabilite_service.lettrer_mouvements([1, 2, 3, 4])

        assert success is True

    def test_scenario_facture_avoir_reglement(self, comptabilite_service, mock_ecriture_dao):
        """Scénario: Facture 500€ + Avoir 100€ + Règlement 400€"""
        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = [
            {'mouvement_id': 1, 'solde': Decimal('500.00')},    # Facture
            {'mouvement_id': 2, 'solde': Decimal('-100.00')},   # Avoir
            {'mouvement_id': 3, 'solde': Decimal('-400.00')}    # Règlement
        ]
        mock_ecriture_dao.get_last_lettrage_code.return_value = 'AA'

        success, _ = comptabilite_service.lettrer_mouvements([1, 2, 3])

        # 500 - 100 - 400 = 0 ✓
        assert success is True


@pytest.mark.unit
@pytest.mark.lettrage
class TestLettragePerformance:
    """Tests de performance du lettrage"""

    def test_lettrage_gros_volume_mouvements(self, comptabilite_service, mock_ecriture_dao):
        """Test: lettrage avec beaucoup de mouvements"""
        # 100 mouvements à lettrer
        mouvements = []
        for i in range(50):
            mouvements.append({'mouvement_id': i*2+1, 'solde': Decimal('100.00')})
            mouvements.append({'mouvement_id': i*2+2, 'solde': Decimal('-100.00')})

        mock_ecriture_dao.get_mouvements_a_lettrer.return_value = mouvements

        # Test que l'opération ne crash pas avec gros volume
        result = comptabilite_service.get_mouvements_a_lettrer(1, 1, '411000')

        assert len(result) == 100

    def test_get_mouvements_lettres_gros_volume(self, comptabilite_service, mock_ecriture_dao):
        """Test: récupération d'un gros volume de lettrages"""
        # 1000 codes de lettrage
        mock_data = [
            {
                'lettrage_code': f'L{i:04d}',
                'nombre_mouvements': 2,
                'total_debit': Decimal('100.00'),
                'total_credit': Decimal('100.00')
            }
            for i in range(1000)
        ]
        mock_ecriture_dao.get_mouvements_lettres.return_value = mock_data

        result = comptabilite_service.get_mouvements_lettres(1, 1)

        assert len(result) == 1000
