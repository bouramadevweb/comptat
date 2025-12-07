"""
Fabriques d'objets pour instancier DatabaseManager, DAO et services en un seul endroit.
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.persistence.dao import (
    SocieteDAO,
    ExerciceDAO,
    JournalDAO,
    CompteDAO,
    TiersDAO,
    EcritureDAO,
    BalanceDAO,
    ReportingDAO,
    ProcedureDAO,
)
from src.infrastructure.persistence.setup_repository import SetupRepository
from src.application.services import ComptabiliteService


def create_db_manager() -> DatabaseManager:
    """Retourne un DatabaseManager connecté."""
    db = DatabaseManager()
    db.connect()
    return db


def create_repositories(db: DatabaseManager):
    """Crée l'ensemble des DAO/repositories utilisés par l'application."""
    return {
        'societe_repo': SocieteDAO(db),
        'exercice_repo': ExerciceDAO(db),
        'journal_repo': JournalDAO(db),
        'compte_repo': CompteDAO(db),
        'tiers_repo': TiersDAO(db),
        'ecriture_repo': EcritureDAO(db),
        'balance_repo': BalanceDAO(db),
        'reporting_repo': ReportingDAO(db),
        'procedure_repo': ProcedureDAO(db),
        'setup_repo': SetupRepository(db),
    }


def create_service(db: DatabaseManager) -> ComptabiliteService:
    """Crée un ComptabiliteService avec toutes ses dépendances."""
    repos = create_repositories(db)
    return ComptabiliteService(
        db=db,
        societe_repo=repos['societe_repo'],
        exercice_repo=repos['exercice_repo'],
        journal_repo=repos['journal_repo'],
        compte_repo=repos['compte_repo'],
        tiers_repo=repos['tiers_repo'],
        ecriture_repo=repos['ecriture_repo'],
        balance_repo=repos['balance_repo'],
        reporting_repo=repos['reporting_repo'],
        procedure_repo=repos['procedure_repo'],
    )
