"""
Validateurs pour l'application de comptabilité
Validation robuste de toutes les données entrantes
"""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Tuple, Optional, List
from src.infrastructure.configuration.constants import *


class ValidationResult:
    """Résultat d'une validation"""

    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message

    def __bool__(self):
        return self.is_valid

    def __str__(self):
        return self.message if not self.is_valid else "Valide"


class ComptabiliteValidator:
    """Validateur principal pour les données comptables"""

    @staticmethod
    def valider_montant(montant: any) -> ValidationResult:
        """
        Valide un montant comptable
        - Doit être un nombre positif ou nul
        - Ne doit pas dépasser la limite maximale
        """
        try:
            # Conversion en Decimal
            if isinstance(montant, str):
                montant = montant.replace(',', '.').strip()
            montant_decimal = Decimal(str(montant))

            # Vérifier que c'est positif
            if montant_decimal < Limites.MIN_MONTANT:
                return ValidationResult(False, ValidationMessages.MONTANT_NEGATIF)

            # Vérifier la limite max
            if montant_decimal > Limites.MAX_MONTANT:
                return ValidationResult(False, f"Le montant dépasse la limite maximale de {Limites.MAX_MONTANT}")

            return ValidationResult(True)

        except (InvalidOperation, ValueError, TypeError) as e:
            return ValidationResult(False, f"Montant invalide: {str(e)}")

    @staticmethod
    def valider_equilibre_ecriture(total_debit: Decimal, total_credit: Decimal) -> ValidationResult:
        """
        Valide l'équilibre d'une écriture comptable
        Débit = Crédit avec tolérance de 0.01
        """
        difference = abs(total_debit - total_credit)
        if difference > Limites.TOLERANCE_EQUILIBRE:
            return ValidationResult(
                False,
                f"Écriture déséquilibrée: Débit={total_debit:.2f} vs Crédit={total_credit:.2f} (diff: {difference:.2f})"
            )
        return ValidationResult(True)

    @staticmethod
    def valider_numero_compte(numero: str) -> ValidationResult:
        """
        Valide un numéro de compte
        - Doit contenir exactement 6 chiffres
        - Le premier chiffre doit être entre 1 et 7
        """
        if not numero:
            return ValidationResult(False, "Le numéro de compte est obligatoire")

        if not re.match(RegexPatterns.NUMERO_COMPTE, numero):
            return ValidationResult(False, "Le numéro de compte doit contenir exactement 6 chiffres")

        # Vérifier la classe (premier chiffre)
        classe = numero[0]
        if classe not in ['1', '2', '3', '4', '5', '6', '7']:
            return ValidationResult(False, f"Classe de compte invalide: {classe}")

        return ValidationResult(True)

    @staticmethod
    def valider_siren(siren: str) -> ValidationResult:
        """
        Valide un numéro SIREN
        - Doit contenir exactement 9 chiffres
        """
        if not siren:
            return ValidationResult(False, "Le SIREN est obligatoire")

        if not re.match(RegexPatterns.SIREN, siren):
            return ValidationResult(False, ValidationMessages.SIREN_INVALIDE)

        return ValidationResult(True)

    @staticmethod
    def valider_siret(siret: str) -> ValidationResult:
        """
        Valide un numéro SIRET
        - Doit contenir exactement 14 chiffres
        """
        if not siret:
            return ValidationResult(False, "Le SIRET est obligatoire")

        if not re.match(RegexPatterns.SIRET, siret):
            return ValidationResult(False, "Le numéro SIRET doit contenir 14 chiffres")

        return ValidationResult(True)

    @staticmethod
    def valider_code_postal(code_postal: str, pays: str = Pays.FRANCE) -> ValidationResult:
        """
        Valide un code postal
        Pour la France: 5 chiffres
        """
        if not code_postal:
            return ValidationResult(False, "Le code postal est obligatoire")

        if pays == Pays.FRANCE:
            if not re.match(RegexPatterns.CODE_POSTAL_FR, code_postal):
                return ValidationResult(False, "Le code postal français doit contenir 5 chiffres")

        return ValidationResult(True)

    @staticmethod
    def valider_email(email: str) -> ValidationResult:
        """Valide une adresse email"""
        if not email:
            return ValidationResult(False, "L'email est obligatoire")

        if not re.match(RegexPatterns.EMAIL, email):
            return ValidationResult(False, "Format d'email invalide")

        return ValidationResult(True)

    @staticmethod
    def valider_telephone(telephone: str, pays: str = Pays.FRANCE) -> ValidationResult:
        """
        Valide un numéro de téléphone
        Pour la France: 10 chiffres commençant par 0
        """
        if not telephone:
            return ValidationResult(False, "Le téléphone est obligatoire")

        if pays == Pays.FRANCE:
            if not re.match(RegexPatterns.TELEPHONE_FR, telephone):
                return ValidationResult(False, "Le numéro de téléphone français doit contenir 10 chiffres et commencer par 0")

        return ValidationResult(True)

    @staticmethod
    def valider_date(date_str: any, date_min: Optional[date] = None, date_max: Optional[date] = None) -> ValidationResult:
        """
        Valide une date
        - Peut vérifier qu'elle est dans une plage
        """
        try:
            # Si c'est déjà un objet date
            if isinstance(date_str, date):
                date_obj = date_str
            # Si c'est une string
            elif isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                return ValidationResult(False, "Format de date invalide")

            # Vérifier la plage si spécifiée
            if date_min and date_obj < date_min:
                return ValidationResult(False, f"La date doit être postérieure au {date_min}")

            if date_max and date_obj > date_max:
                return ValidationResult(False, f"La date doit être antérieure au {date_max}")

            return ValidationResult(True)

        except (ValueError, TypeError) as e:
            return ValidationResult(False, f"Date invalide: {str(e)}")

    @staticmethod
    def valider_date_dans_exercice(date_ecriture: date, date_debut_exercice: date, date_fin_exercice: date) -> ValidationResult:
        """
        Valide qu'une date d'écriture est bien dans l'exercice
        """
        if date_ecriture < date_debut_exercice or date_ecriture > date_fin_exercice:
            return ValidationResult(
                False,
                f"La date doit être comprise entre {date_debut_exercice} et {date_fin_exercice}"
            )
        return ValidationResult(True)

    @staticmethod
    def valider_exercice_annee(annee: int) -> ValidationResult:
        """
        Valide une année d'exercice
        """
        if annee < Limites.ANNEE_MIN or annee > Limites.ANNEE_MAX:
            return ValidationResult(
                False,
                f"L'année doit être comprise entre {Limites.ANNEE_MIN} et {Limites.ANNEE_MAX}"
            )
        return ValidationResult(True)

    @staticmethod
    def valider_taux_tva(taux: Decimal) -> ValidationResult:
        """
        Valide un taux de TVA
        - Doit être entre 0 et 1 (ou 0% et 100%)
        """
        try:
            taux_decimal = Decimal(str(taux))

            if taux_decimal < Decimal("0") or taux_decimal > Decimal("1"):
                return ValidationResult(False, "Le taux de TVA doit être entre 0 et 1 (0% à 100%)")

            return ValidationResult(True)

        except (InvalidOperation, ValueError) as e:
            return ValidationResult(False, f"Taux de TVA invalide: {str(e)}")

    @staticmethod
    def valider_taux_tva_standard(taux: Decimal) -> ValidationResult:
        """
        Valide qu'un taux de TVA correspond à un taux standard
        """
        taux_standards = [
            TauxTVA.TAUX_ZERO,
            TauxTVA.TAUX_SUPER_REDUIT,
            TauxTVA.TAUX_REDUIT,
            TauxTVA.TAUX_INTERMEDIAIRE,
            TauxTVA.TAUX_NORMAL
        ]

        taux_decimal = Decimal(str(taux))

        if taux_decimal not in taux_standards:
            taux_valides = ", ".join([f"{float(t)*100}%" for t in taux_standards])
            return ValidationResult(
                False,
                f"Taux de TVA non standard. Taux valides: {taux_valides}"
            )

        return ValidationResult(True)

    @staticmethod
    def valider_champ_obligatoire(valeur: any, nom_champ: str = "Ce champ") -> ValidationResult:
        """
        Valide qu'un champ obligatoire n'est pas vide
        """
        if valeur is None:
            return ValidationResult(False, f"{nom_champ} est obligatoire")

        if isinstance(valeur, str) and not valeur.strip():
            return ValidationResult(False, f"{nom_champ} est obligatoire")

        return ValidationResult(True)

    @staticmethod
    def valider_longueur(valeur: str, min_length: int = 0, max_length: int = 255, nom_champ: str = "Ce champ") -> ValidationResult:
        """
        Valide la longueur d'une chaîne
        """
        if not valeur:
            longueur = 0
        else:
            longueur = len(str(valeur))

        if longueur < min_length:
            return ValidationResult(False, f"{nom_champ} doit contenir au moins {min_length} caractères")

        if longueur > max_length:
            return ValidationResult(False, f"{nom_champ} ne peut pas dépasser {max_length} caractères")

        return ValidationResult(True)

    @staticmethod
    def valider_ecriture_complete(
        mouvements: List,
        date_ecriture: date,
        exercice_debut: date,
        exercice_fin: date,
        reference: str,
        libelle: str
    ) -> ValidationResult:
        """
        Valide une écriture comptable complète
        - Vérifie tous les champs obligatoires
        - Vérifie l'équilibre
        - Vérifie la date dans l'exercice
        """
        # Vérifier champs obligatoires
        result = ComptabiliteValidator.valider_champ_obligatoire(reference, "La référence")
        if not result:
            return result

        result = ComptabiliteValidator.valider_champ_obligatoire(libelle, "Le libellé")
        if not result:
            return result

        # Vérifier la date
        result = ComptabiliteValidator.valider_date_dans_exercice(date_ecriture, exercice_debut, exercice_fin)
        if not result:
            return result

        # Vérifier qu'il y a au moins 2 mouvements
        if not mouvements or len(mouvements) < 2:
            return ValidationResult(False, "Une écriture doit contenir au moins 2 lignes")

        # Vérifier le nombre maximum de lignes
        if len(mouvements) > Limites.MAX_LIGNES_ECRITURE:
            return ValidationResult(
                False,
                f"Une écriture ne peut pas contenir plus de {Limites.MAX_LIGNES_ECRITURE} lignes"
            )

        # Calculer totaux et vérifier équilibre
        total_debit = Decimal("0")
        total_credit = Decimal("0")

        for i, mvt in enumerate(mouvements):
            # Vérifier montants
            result = ComptabiliteValidator.valider_montant(mvt.debit)
            if not result:
                return ValidationResult(False, f"Ligne {i+1}: Débit invalide - {result.message}")

            result = ComptabiliteValidator.valider_montant(mvt.credit)
            if not result:
                return ValidationResult(False, f"Ligne {i+1}: Crédit invalide - {result.message}")

            # Vérifier qu'on n'a pas débit ET crédit sur la même ligne
            if mvt.debit > 0 and mvt.credit > 0:
                return ValidationResult(False, f"Ligne {i+1}: Une ligne ne peut pas avoir débit ET crédit simultanément")

            # Vérifier qu'il y a au moins un montant
            if mvt.debit == 0 and mvt.credit == 0:
                return ValidationResult(False, f"Ligne {i+1}: La ligne doit avoir un débit ou un crédit")

            total_debit += mvt.debit
            total_credit += mvt.credit

        # Vérifier l'équilibre
        result = ComptabiliteValidator.valider_equilibre_ecriture(total_debit, total_credit)
        if not result:
            return result

        return ValidationResult(True, "Écriture valide")


class SocieteValidator:
    """Validateur pour les sociétés"""

    @staticmethod
    def valider_societe(nom: str, siren: Optional[str] = None, code_postal: Optional[str] = None, pays: str = Pays.FRANCE) -> ValidationResult:
        """Valide les données d'une société"""

        # Nom obligatoire
        result = ComptabiliteValidator.valider_champ_obligatoire(nom, "Le nom de la société")
        if not result:
            return result

        result = ComptabiliteValidator.valider_longueur(nom, 2, 255, "Le nom de la société")
        if not result:
            return result

        # SIREN si fourni
        if siren:
            result = ComptabiliteValidator.valider_siren(siren)
            if not result:
                return result

        # Code postal si fourni
        if code_postal:
            result = ComptabiliteValidator.valider_code_postal(code_postal, pays)
            if not result:
                return result

        return ValidationResult(True)


class TiersValidator:
    """Validateur pour les tiers"""

    @staticmethod
    def valider_tiers(nom: str, type_tiers: str, code_aux: Optional[str] = None) -> ValidationResult:
        """Valide les données d'un tiers"""

        # Nom obligatoire
        result = ComptabiliteValidator.valider_champ_obligatoire(nom, "Le nom du tiers")
        if not result:
            return result

        result = ComptabiliteValidator.valider_longueur(nom, 2, 255, "Le nom du tiers")
        if not result:
            return result

        # Type obligatoire
        result = ComptabiliteValidator.valider_champ_obligatoire(type_tiers, "Le type de tiers")
        if not result:
            return result

        # Type valide
        types_valides = [TypeTiers.CLIENT, TypeTiers.FOURNISSEUR, TypeTiers.SALARIE, TypeTiers.ORGANISME, TypeTiers.AUTRE]
        if type_tiers not in types_valides:
            return ValidationResult(False, f"Type de tiers invalide. Valeurs autorisées: {', '.join(types_valides)}")

        # Code auxiliaire si fourni
        if code_aux:
            result = ComptabiliteValidator.valider_longueur(code_aux, 1, 20, "Le code auxiliaire")
            if not result:
                return result

        return ValidationResult(True)


# ============================================================
# Fonctions utilitaires de validation rapide
# ============================================================

def valider_et_convertir_montant(montant: any) -> Tuple[bool, Optional[Decimal], str]:
    """
    Valide et convertit un montant
    Retourne: (succès, montant_converti, message_erreur)
    """
    result = ComptabiliteValidator.valider_montant(montant)
    if result:
        try:
            if isinstance(montant, str):
                montant = montant.replace(',', '.').strip()
            return True, Decimal(str(montant)), ""
        except:
            return False, None, "Erreur de conversion"
    else:
        return False, None, result.message


def valider_et_convertir_date(date_str: any) -> Tuple[bool, Optional[date], str]:
    """
    Valide et convertit une date
    Retourne: (succès, date_convertie, message_erreur)
    """
    result = ComptabiliteValidator.valider_date(date_str)
    if result:
        try:
            if isinstance(date_str, date):
                return True, date_str, ""
            else:
                date_obj = datetime.strptime(str(date_str), "%Y-%m-%d").date()
                return True, date_obj, ""
        except:
            return False, None, "Erreur de conversion"
    else:
        return False, None, result.message
