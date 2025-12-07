"""
Constantes de l'application de comptabilité
Centralisation de tous les numéros de comptes et codes
"""
from decimal import Decimal


# ============================================================
# COMPTES COMPTABLES - Plan Comptable Général (PCG)
# ============================================================

class ComptesComptables:
    """Numéros de comptes du plan comptable"""

    # Classe 1 - Capitaux
    CAPITAL_SOCIAL = "101000"
    RESERVES = "106000"
    RESULTAT_EXERCICE = "120000"
    RESULTAT_BENEFICE = "120000"
    RESULTAT_PERTE = "129000"
    SUBVENTIONS = "131000"
    EMPRUNTS = "164000"

    # Classe 2 - Immobilisations
    IMMOBILISATIONS_INCORPORELLES = "205000"
    FRAIS_ETABLISSEMENT = "201000"
    LOGICIELS = "205100"
    IMMOBILISATIONS_CORPORELLES = "211000"
    TERRAINS = "211000"
    CONSTRUCTIONS = "213000"
    MATERIEL_BUREAU = "218300"
    MATERIEL_TRANSPORT = "218200"
    AMORTISSEMENT_IMMOBILISATIONS = "280000"

    # Classe 3 - Stocks
    STOCKS_MARCHANDISES = "370000"
    STOCKS_MATIERES = "310000"
    STOCKS_PRODUITS = "350000"

    # Classe 4 - Tiers
    FOURNISSEURS = "401000"
    FOURNISSEURS_FACTURES = "401000"
    FOURNISSEURS_EFFETS = "403000"
    CLIENTS = "411000"
    CLIENTS_FACTURES = "411000"
    CLIENTS_DOUTEUX = "416000"
    CLIENTS_EFFETS = "413000"

    # TVA
    TVA_COLLECTEE = "445710"
    TVA_COLLECTEE_20 = "445711"
    TVA_COLLECTEE_10 = "445712"
    TVA_COLLECTEE_55 = "445713"
    TVA_DEDUCTIBLE = "445660"
    TVA_DEDUCTIBLE_20 = "445661"
    TVA_DEDUCTIBLE_10 = "445662"
    TVA_A_DECAISSER = "445510"

    # Charges sociales et fiscales
    SECURITE_SOCIALE = "431000"
    URSSAF = "431100"
    SALAIRES_A_PAYER = "421000"
    ORGANISMES_SOCIAUX = "438000"

    # Classe 5 - Financiers
    BANQUE = "512000"
    BANQUE_PRINCIPALE = "512100"
    CAISSE = "530000"
    VALEURS_MOBILIERES = "503000"

    # Classe 6 - Charges
    ACHATS_MARCHANDISES = "607000"
    ACHATS_MATIERES = "601000"
    ACHATS_FOURNITURES = "606000"
    SERVICES_EXTERIEURS = "611000"
    LOYERS = "613000"
    ENTRETIEN = "615000"
    ASSURANCES = "616000"
    HONORAIRES = "622600"
    PUBLICITE = "623000"
    TRANSPORT = "624100"
    FRAIS_BANCAIRES = "627000"
    SALAIRES_BRUTS = "641000"
    CHARGES_SOCIALES = "645000"
    IMPOTS_TAXES = "635000"
    DOTATIONS_AMORTISSEMENTS = "681100"

    # Classe 7 - Produits
    VENTES_MARCHANDISES = "707000"
    VENTES_PRODUITS = "701000"
    PRESTATIONS_SERVICES = "706000"
    PRODUCTION_IMMOBILISEE = "721000"
    SUBVENTIONS_EXPLOITATION = "740000"
    PRODUITS_FINANCIERS = "760000"
    PRODUITS_EXCEPTIONNELS = "770000"


class TauxTVA:
    """Taux de TVA applicables"""
    TAUX_NORMAL = Decimal("0.20")  # 20%
    TAUX_INTERMEDIAIRE = Decimal("0.10")  # 10%
    TAUX_REDUIT = Decimal("0.055")  # 5.5%
    TAUX_SUPER_REDUIT = Decimal("0.021")  # 2.1%
    TAUX_ZERO = Decimal("0.00")  # 0%


class TypesJournal:
    """Types de journaux comptables"""
    VENTE = "VENTE"
    ACHAT = "ACHAT"
    BANQUE = "BANQUE"
    CAISSE = "CAISSE"
    OD = "OD"  # Opérations Diverses
    AN = "AN"  # A-Nouveaux


class CodeJournal:
    """Codes des journaux"""
    VT = "VT"  # Ventes
    AC = "AC"  # Achats
    BQ = "BQ"  # Banque
    CA = "CA"  # Caisse
    OD = "OD"  # Opérations Diverses
    AN = "AN"  # A-Nouveaux


class TypeTiers:
    """Types de tiers"""
    CLIENT = "CLIENT"
    FOURNISSEUR = "FOURNISSEUR"
    SALARIE = "SALARIE"
    ORGANISME = "ORGANISME"
    AUTRE = "AUTRE"


class TypeCompte:
    """Types de comptes"""
    ACTIF = "actif"
    PASSIF = "passif"
    CHARGE = "charge"
    PRODUIT = "produit"
    TVA = "tva"


class ClasseCompte:
    """Classes de comptes PCG"""
    CAPITAUX = "1"
    IMMOBILISATIONS = "2"
    STOCKS = "3"
    TIERS = "4"
    FINANCIERS = "5"
    CHARGES = "6"
    PRODUITS = "7"


class ModePaiement:
    """Modes de paiement"""
    VIREMENT = "VIREMENT"
    CHEQUE = "CHEQUE"
    ESPECES = "ESPECES"
    CARTE_BANCAIRE = "CARTE_BANCAIRE"
    PRELEVEMENT = "PRELEVEMENT"
    TRAITE = "TRAITE"
    AUTRE = "AUTRE"


class Pays:
    """Codes pays"""
    FRANCE = "FR"
    BELGIQUE = "BE"
    SUISSE = "CH"
    LUXEMBOURG = "LU"
    ALLEMAGNE = "DE"
    ESPAGNE = "ES"
    ITALIE = "IT"


class StatusExercice:
    """Status d'exercice comptable"""
    OUVERT = False
    CLOTURE = True


class ValidationMessages:
    """Messages de validation"""
    ECRITURE_DESEQUILIBREE = "L'écriture est déséquilibrée. Débit et Crédit doivent être égaux."
    COMPTE_INEXISTANT = "Le compte comptable n'existe pas."
    EXERCICE_CLOTURE = "L'exercice est clôturé. Modification impossible."
    MONTANT_NEGATIF = "Le montant ne peut pas être négatif."
    DATE_INVALIDE = "La date est invalide ou hors de l'exercice."
    CHAMP_OBLIGATOIRE = "Ce champ est obligatoire."
    SIREN_INVALIDE = "Le numéro SIREN doit contenir 9 chiffres."
    TVA_INVALIDE = "Le taux de TVA est invalide."
    JOURNAL_INEXISTANT = "Le journal n'existe pas."
    TIERS_INEXISTANT = "Le tiers n'existe pas."


class Limites:
    """Limites et contraintes de l'application"""
    MAX_MONTANT = Decimal("999999999.99")
    MIN_MONTANT = Decimal("0.00")
    TOLERANCE_EQUILIBRE = Decimal("0.01")  # Tolérance pour l'équilibre des écritures
    MAX_LIGNES_ECRITURE = 100
    ANNEE_MIN = 2000
    ANNEE_MAX = 2099
    SIREN_LENGTH = 9
    SIRET_LENGTH = 14


class ExportFormats:
    """Formats d'export"""
    FEC = "FEC"  # Fichier des Écritures Comptables
    EXCEL = "EXCEL"
    PDF = "PDF"
    CSV = "CSV"
    JSON = "JSON"


class SQLTableNames:
    """Noms des tables SQL"""
    SOCIETES = "SOCIETES"
    EXERCICES = "EXERCICES"
    JOURNAUX = "JOURNAUX"
    COMPTES = "COMPTES"
    TIERS = "TIERS"
    ECRITURES = "ECRITURES"
    MOUVEMENTS = "MOUVEMENTS"
    BALANCE = "BALANCE"
    TAXES = "TAXES"
    PAIEMENTS = "PAIEMENTS"


class ProceduresStockees:
    """Noms des procédures stockées"""
    CALCULER_BALANCE = "Calculer_Balance"
    CLOTURER_EXERCICE = "Cloturer_Exercice"
    EXPORTER_FEC = "Exporter_FEC_Exercice"
    TESTER_COMPTABILITE = "Tester_Comptabilite_Avancee"
    AUTO_AUDIT_CLOTURE = "AutoAudit_Cloture"


class RegexPatterns:
    """Patterns de validation"""
    SIREN = r"^\d{9}$"
    SIRET = r"^\d{14}$"
    CODE_POSTAL_FR = r"^\d{5}$"
    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    TELEPHONE_FR = r"^0[1-9]\d{8}$"
    NUMERO_COMPTE = r"^\d{6}$"


class Messages:
    """Messages utilisateur"""
    SUCCES_CREATION = "Création réussie"
    SUCCES_MODIFICATION = "Modification réussie"
    SUCCES_SUPPRESSION = "Suppression réussie"
    ERREUR_CREATION = "Erreur lors de la création"
    ERREUR_MODIFICATION = "Erreur lors de la modification"
    ERREUR_SUPPRESSION = "Erreur lors de la suppression"
    ERREUR_CONNEXION_BDD = "Erreur de connexion à la base de données"
    CONFIRMATION_SUPPRESSION = "Êtes-vous sûr de vouloir supprimer cet élément ?"
    CONFIRMATION_CLOTURE = "Êtes-vous sûr de vouloir clôturer cet exercice ? Cette action est irréversible."


# ============================================================
# Fonctions utilitaires pour les constantes
# ============================================================

def get_compte_tva_collectee(taux: Decimal) -> str:
    """Retourne le compte de TVA collectée selon le taux"""
    if taux == TauxTVA.TAUX_NORMAL:
        return ComptesComptables.TVA_COLLECTEE_20
    elif taux == TauxTVA.TAUX_INTERMEDIAIRE:
        return ComptesComptables.TVA_COLLECTEE_10
    elif taux == TauxTVA.TAUX_REDUIT:
        return ComptesComptables.TVA_COLLECTEE_55
    else:
        return ComptesComptables.TVA_COLLECTEE


def get_compte_tva_deductible(taux: Decimal) -> str:
    """Retourne le compte de TVA déductible selon le taux"""
    if taux == TauxTVA.TAUX_NORMAL:
        return ComptesComptables.TVA_DEDUCTIBLE_20
    elif taux == TauxTVA.TAUX_INTERMEDIAIRE:
        return ComptesComptables.TVA_DEDUCTIBLE_10
    else:
        return ComptesComptables.TVA_DEDUCTIBLE


def get_libelle_tva(taux: Decimal, collectee: bool = True) -> str:
    """Retourne le libellé de TVA"""
    type_tva = "collectée" if collectee else "déductible"
    taux_pct = float(taux * 100)
    return f"TVA {type_tva} {taux_pct:.1f}%"


def est_compte_bilan(numero_compte: str) -> bool:
    """Vérifie si un compte est un compte de bilan (classes 1 à 5)"""
    if not numero_compte:
        return False
    return numero_compte[0] in [ClasseCompte.CAPITAUX, ClasseCompte.IMMOBILISATIONS,
                                  ClasseCompte.STOCKS, ClasseCompte.TIERS,
                                  ClasseCompte.FINANCIERS]


def est_compte_gestion(numero_compte: str) -> bool:
    """Vérifie si un compte est un compte de gestion (classes 6 et 7)"""
    if not numero_compte:
        return False
    return numero_compte[0] in [ClasseCompte.CHARGES, ClasseCompte.PRODUITS]
