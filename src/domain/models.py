"""
Modèles de données pour la comptabilité
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


@dataclass
class Societe:
    """Représente une société"""
    id: Optional[int] = None
    nom: str = ""
    pays: str = "FR"
    siren: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    date_creation: Optional[date] = None


@dataclass
class Exercice:
    """Représente un exercice comptable"""
    id: Optional[int] = None
    societe_id: int = 0
    annee: int = 0
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    cloture: bool = False


@dataclass
class Journal:
    """Représente un journal comptable"""
    id: Optional[int] = None
    societe_id: int = 0
    code: str = ""
    libelle: str = ""
    type: str = ""  # VENTE, ACHAT, BANQUE, OD
    compteur: int = 0


@dataclass
class Compte:
    """Représente un compte du plan comptable"""
    id: Optional[int] = None
    societe_id: int = 0
    compte: str = ""
    intitule: str = ""
    classe: str = ""
    type_compte: str = ""
    lettrable: bool = False
    compte_parent_id: Optional[int] = None


@dataclass
class Tiers:
    """Représente un tiers (client ou fournisseur)"""
    id: Optional[int] = None
    societe_id: int = 0
    code_aux: str = ""
    nom: str = ""
    type: str = ""  # CLIENT, FOURNISSEUR
    adresse: Optional[str] = None
    ville: Optional[str] = None
    pays: str = "FR"


@dataclass
class Taxe:
    """Représente un paramétrage de TVA"""
    id: Optional[int] = None
    societe_id: int = 0
    code: str = ""
    nom: str = ""
    taux: Decimal = Decimal('0')
    compte_collecte_id: Optional[int] = None
    compte_deductible_id: Optional[int] = None


@dataclass
class Ecriture:
    """Représente une écriture comptable (en-tête)"""
    id: Optional[int] = None
    societe_id: int = 0
    exercice_id: int = 0
    journal_id: int = 0
    numero: str = ""
    date_ecriture: Optional[date] = None
    reference_piece: Optional[str] = None
    libelle: Optional[str] = None
    validee: bool = False
    date_validation: Optional[date] = None
    mouvements: List['Mouvement'] = field(default_factory=list)


@dataclass
class Mouvement:
    """Représente une ligne d'écriture"""
    id: Optional[int] = None
    ecriture_id: Optional[int] = None
    compte_id: int = 0
    compte_numero: str = ""  # Pour affichage
    tiers_id: Optional[int] = None
    libelle: Optional[str] = None
    debit: Decimal = Decimal('0')
    credit: Decimal = Decimal('0')
    lettrage_code: Optional[str] = None


@dataclass
class Paiement:
    """Représente un paiement"""
    id: Optional[int] = None
    societe_id: int = 0
    tiers_id: int = 0
    date_paiement: Optional[date] = None
    montant: Decimal = Decimal('0')
    mode_paiement: str = "VIREMENT"
    reference: Optional[str] = None
    commentaire: Optional[str] = None


@dataclass
class Balance:
    """Représente une ligne de balance"""
    id: Optional[int] = None
    societe_id: int = 0
    exercice_id: int = 0
    compte_id: int = 0
    compte: str = ""
    intitule: str = ""
    classe: str = ""
    total_debit: Decimal = Decimal('0')
    total_credit: Decimal = Decimal('0')
    solde: Decimal = Decimal('0')
    date_calcul: Optional[datetime] = None


@dataclass
class LigneFEC:
    """Représente une ligne du FEC"""
    journal_code: str = ""
    journal_lib: str = ""
    ecriture_num: str = ""
    ecriture_date: str = ""
    compte_num: str = ""
    compte_lib: str = ""
    comp_aux_num: str = ""
    comp_aux_lib: str = ""
    piece_ref: str = ""
    piece_date: str = ""
    ecriture_lib: str = ""
    debit: str = "0.00"
    credit: str = "0.00"
    ecriture_let: str = ""
    date_let: str = ""
    valid_date: str = ""
    montant_devise: str = ""
    idevise: str = ""


# ==================== AUTHENTIFICATION & AUTORISATION ====================

@dataclass
class Role:
    """Représente un rôle utilisateur"""
    id: Optional[int] = None
    code: str = ""  # ADMIN, COMPTABLE, LECTEUR
    nom: str = ""
    description: Optional[str] = None
    # Permissions
    peut_creer: bool = False
    peut_modifier: bool = False
    peut_supprimer: bool = False
    peut_valider: bool = False
    peut_cloturer: bool = False
    peut_gerer_users: bool = False


@dataclass
class User:
    """Représente un utilisateur"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""  # Hash bcrypt du mot de passe
    nom: Optional[str] = None
    prenom: Optional[str] = None
    role_id: int = 0
    role: Optional[Role] = None
    actif: bool = True
    date_creation: Optional[datetime] = None
    date_derniere_connexion: Optional[datetime] = None
    tentatives_connexion: int = 0
    compte_bloque: bool = False


@dataclass
class Session:
    """Représente une session utilisateur"""
    id: Optional[int] = None
    user_id: int = 0
    token: str = ""  # JWT token
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    date_creation: Optional[datetime] = None
    date_expiration: Optional[datetime] = None
    revoked: bool = False


@dataclass
class AuditLog:
    """Journal d'audit pour tracer toutes les actions"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    username: str = ""
    action: str = ""  # CREATE, UPDATE, DELETE, VALIDATE, CLOSE, LOGIN, LOGOUT
    entity_type: str = ""  # ECRITURE, SOCIETE, EXERCICE, USER, etc.
    entity_id: Optional[int] = None
    details: Optional[str] = None  # JSON avec détails de l'action
    ip_address: Optional[str] = None
    date_action: Optional[datetime] = None
    success: bool = True
    error_message: Optional[str] = None
