"""
Tests pour les validateurs
"""
import pytest
from decimal import Decimal
from datetime import date
from src.infrastructure.validation.validators import ComptabiliteValidator
from src.infrastructure.configuration.constants import Limites


@pytest.mark.unit
@pytest.mark.validators
class TestComptabiliteValidator:
    """Tests du validateur principal"""

    # ==================== TESTS MONTANT ====================

    def test_valider_montant_positif_valide(self):
        """Test: montant positif valide"""
        result = ComptabiliteValidator.valider_montant(100.50)
        assert result.is_valid is True

    def test_valider_montant_zero_valide(self):
        """Test: montant zéro est valide"""
        result = ComptabiliteValidator.valider_montant(0)
        assert result.is_valid is True

    def test_valider_montant_negatif_invalide(self):
        """Test: montant négatif est invalide"""
        result = ComptabiliteValidator.valider_montant(-50)
        assert result.is_valid is False
        assert "négatif" in result.message.lower()

    def test_valider_montant_trop_grand_invalide(self):
        """Test: montant dépassant la limite est invalide"""
        result = ComptabiliteValidator.valider_montant(Decimal("99999999999"))
        assert result.is_valid is False
        assert "limite" in result.message.lower()

    def test_valider_montant_decimal_valide(self):
        """Test: Decimal est accepté"""
        result = ComptabiliteValidator.valider_montant(Decimal("123.45"))
        assert result.is_valid is True

    def test_valider_montant_string_valide(self):
        """Test: string avec nombre valide"""
        result = ComptabiliteValidator.valider_montant("100.50")
        assert result.is_valid is True

    def test_valider_montant_string_virgule_valide(self):
        """Test: string avec virgule comme séparateur"""
        result = ComptabiliteValidator.valider_montant("100,50")
        assert result.is_valid is True

    def test_valider_montant_invalide_format(self):
        """Test: format invalide"""
        result = ComptabiliteValidator.valider_montant("abc")
        assert result.is_valid is False

    # ==================== TESTS ÉQUILIBRE ====================

    def test_valider_equilibre_ecriture_equilibree(self):
        """Test: écriture équilibrée"""
        result = ComptabiliteValidator.valider_equilibre_ecriture(
            Decimal("100.00"),
            Decimal("100.00")
        )
        assert result.is_valid is True

    def test_valider_equilibre_ecriture_desequilibree(self):
        """Test: écriture déséquilibrée"""
        result = ComptabiliteValidator.valider_equilibre_ecriture(
            Decimal("100.00"),
            Decimal("50.00")
        )
        assert result.is_valid is False
        assert "déséquilibré" in result.message.lower()

    def test_valider_equilibre_avec_tolerance(self):
        """Test: différence dans la tolérance est OK"""
        result = ComptabiliteValidator.valider_equilibre_ecriture(
            Decimal("100.00"),
            Decimal("100.005")  # Différence de 0.005 < 0.01
        )
        assert result.is_valid is True

    def test_valider_equilibre_hors_tolerance(self):
        """Test: différence hors tolérance est invalide"""
        result = ComptabiliteValidator.valider_equilibre_ecriture(
            Decimal("100.00"),
            Decimal("100.02")  # Différence de 0.02 > 0.01
        )
        assert result.is_valid is False

    # ==================== TESTS NUMÉRO COMPTE ====================

    def test_valider_numero_compte_valide(self):
        """Test: numéro de compte valide (6 chiffres, classe 1-7)"""
        for compte in ["101000", "411000", "607000", "201000"]:
            result = ComptabiliteValidator.valider_numero_compte(compte)
            assert result.is_valid is True, f"Le compte {compte} devrait être valide"

    def test_valider_numero_compte_classe_invalide(self):
        """Test: numéro de compte avec classe invalide (8, 9, 0)"""
        for compte in ["801000", "901000", "001000"]:
            result = ComptabiliteValidator.valider_numero_compte(compte)
            assert result.is_valid is False, f"Le compte {compte} ne devrait pas être valide"

    def test_valider_numero_compte_trop_court(self):
        """Test: numéro de compte trop court"""
        result = ComptabiliteValidator.valider_numero_compte("411")
        assert result.is_valid is False

    def test_valider_numero_compte_trop_long(self):
        """Test: numéro de compte trop long"""
        result = ComptabiliteValidator.valider_numero_compte("4110000")
        assert result.is_valid is False

    def test_valider_numero_compte_vide(self):
        """Test: numéro de compte vide"""
        result = ComptabiliteValidator.valider_numero_compte("")
        assert result.is_valid is False

    def test_valider_numero_compte_non_numerique(self):
        """Test: numéro de compte non numérique"""
        result = ComptabiliteValidator.valider_numero_compte("ABC123")
        assert result.is_valid is False

    # ==================== TESTS SIREN ====================

    def test_valider_siren_valide(self):
        """Test: SIREN valide (9 chiffres)"""
        result = ComptabiliteValidator.valider_siren("123456789")
        assert result.is_valid is True

    def test_valider_siren_trop_court(self):
        """Test: SIREN trop court"""
        result = ComptabiliteValidator.valider_siren("12345678")
        assert result.is_valid is False

    def test_valider_siren_trop_long(self):
        """Test: SIREN trop long"""
        result = ComptabiliteValidator.valider_siren("1234567890")
        assert result.is_valid is False

    def test_valider_siren_non_numerique(self):
        """Test: SIREN non numérique"""
        result = ComptabiliteValidator.valider_siren("ABC123456")
        assert result.is_valid is False

    def test_valider_siren_vide(self):
        """Test: SIREN vide"""
        result = ComptabiliteValidator.valider_siren("")
        assert result.is_valid is False

    # ==================== TESTS DATE EXERCICE ====================

    def test_valider_dates_exercice_valide(self):
        """Test: dates d'exercice valides (12 mois)"""
        result = ComptabiliteValidator.valider_dates_exercice(
            date(2025, 1, 1),
            date(2025, 12, 31)
        )
        assert result.is_valid is True

    def test_valider_dates_exercice_debut_apres_fin(self):
        """Test: date début après date fin"""
        result = ComptabiliteValidator.valider_dates_exercice(
            date(2025, 12, 31),
            date(2025, 1, 1)
        )
        assert result.is_valid is False

    def test_valider_dates_exercice_trop_court(self):
        """Test: exercice trop court (< 28 jours)"""
        result = ComptabiliteValidator.valider_dates_exercice(
            date(2025, 1, 1),
            date(2025, 1, 15)  # 14 jours
        )
        assert result.is_valid is False

    def test_valider_dates_exercice_trop_long(self):
        """Test: exercice trop long (> 18 mois)"""
        result = ComptabiliteValidator.valider_dates_exercice(
            date(2025, 1, 1),
            date(2026, 8, 1)  # 19 mois
        )
        assert result.is_valid is False

    # ==================== TESTS CODE JOURNAL ====================

    def test_valider_code_journal_valide(self):
        """Test: code journal valide (2-5 caractères alphanumériques)"""
        for code in ["VE", "AC", "BQ", "OD", "VENTE"]:
            result = ComptabiliteValidator.valider_code_journal(code)
            assert result.is_valid is True, f"Le code {code} devrait être valide"

    def test_valider_code_journal_trop_court(self):
        """Test: code journal trop court"""
        result = ComptabiliteValidator.valider_code_journal("V")
        assert result.is_valid is False

    def test_valider_code_journal_trop_long(self):
        """Test: code journal trop long"""
        result = ComptabiliteValidator.valider_code_journal("VENTES")
        assert result.is_valid is False

    def test_valider_code_journal_caracteres_invalides(self):
        """Test: code journal avec caractères spéciaux"""
        result = ComptabiliteValidator.valider_code_journal("VE-1")
        assert result.is_valid is False

    def test_valider_code_journal_vide(self):
        """Test: code journal vide"""
        result = ComptabiliteValidator.valider_code_journal("")
        assert result.is_valid is False

    # ==================== TESTS CODE TVA ====================

    def test_valider_code_tva_valide(self):
        """Test: code TVA valide"""
        for code in ["445710", "445660", "445711", "445661"]:
            result = ComptabiliteValidator.valider_code_tva(code)
            assert result.is_valid is True, f"Le code TVA {code} devrait être valide"

    def test_valider_code_tva_invalide(self):
        """Test: code TVA invalide (ne commence pas par 4457 ou 4456)"""
        result = ComptabiliteValidator.valider_code_tva("411000")
        assert result.is_valid is False

    def test_valider_code_tva_trop_court(self):
        """Test: code TVA trop court"""
        result = ComptabiliteValidator.valider_code_tva("4457")
        assert result.is_valid is False


# ==================== TESTS EDGE CASES ====================

@pytest.mark.unit
@pytest.mark.validators
class TestValidatorEdgeCases:
    """Tests des cas limites"""

    def test_montant_limite_exacte(self):
        """Test: montant à la limite exacte"""
        result = ComptabiliteValidator.valider_montant(Limites.MAX_MONTANT)
        assert result.is_valid is True

    def test_montant_juste_au_dessus_limite(self):
        """Test: montant juste au-dessus de la limite"""
        result = ComptabiliteValidator.valider_montant(
            Limites.MAX_MONTANT + Decimal("0.01")
        )
        assert result.is_valid is False

    def test_equilibre_tolerance_exacte(self):
        """Test: différence exactement à la tolérance"""
        result = ComptabiliteValidator.valider_equilibre_ecriture(
            Decimal("100.00"),
            Decimal("100.01")  # Différence = 0.01 = tolérance
        )
        assert result.is_valid is True

    def test_numero_compte_limites_classes(self):
        """Test: numéros de compte aux limites des classes"""
        for compte in ["100000", "799999"]:
            result = ComptabiliteValidator.valider_numero_compte(compte)
            assert result.is_valid is True

    def test_dates_exercice_exactement_12_mois(self):
        """Test: exercice de exactement 12 mois"""
        result = ComptabiliteValidator.valider_dates_exercice(
            date(2025, 1, 1),
            date(2025, 12, 31)
        )
        assert result.is_valid is True

    def test_dates_exercice_exactement_18_mois(self):
        """Test: exercice de exactement 18 mois (limite max)"""
        result = ComptabiliteValidator.valider_dates_exercice(
            date(2025, 1, 1),
            date(2026, 6, 30)  # 18 mois
        )
        assert result.is_valid is True


# ==================== TESTS PERFORMANCE ====================

@pytest.mark.unit
@pytest.mark.validators
class TestValidatorPerformance:
    """Tests de performance des validateurs"""

    def test_valider_1000_montants(self):
        """Test: validation de 1000 montants"""
        import time
        start = time.time()

        for i in range(1000):
            ComptabiliteValidator.valider_montant(i * 10.5)

        duration = time.time() - start
        assert duration < 1.0, "La validation de 1000 montants devrait prendre < 1s"

    def test_valider_1000_comptes(self):
        """Test: validation de 1000 numéros de compte"""
        import time
        start = time.time()

        for i in range(1000):
            ComptabiliteValidator.valider_numero_compte(f"{100000 + i}")

        duration = time.time() - start
        assert duration < 1.0, "La validation de 1000 comptes devrait prendre < 1s"
