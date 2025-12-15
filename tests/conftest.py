"""
Configuration pytest - Fixtures communes pour tous les tests
"""
import pytest
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import Mock, MagicMock
from faker import Faker

# Import des modèles
from src.domain.models import (
    Societe, Exercice, Journal, Compte, Tiers, Ecriture, Mouvement, Balance
)

fake = Faker('fr_FR')


# ==================== FIXTURES DATABASE ====================

@pytest.fixture
def mock_db():
    """Mock de DatabaseManager"""
    db = Mock()
    db.execute_query = Mock(return_value=[])
    db.call_procedure = Mock(return_value=[])

    # Mock du cursor pour le context manager
    cursor_mock = Mock()
    cursor_mock.lastrowid = 1
    cursor_mock.execute = Mock()
    cursor_mock.fetchall = Mock(return_value=[])
    cursor_mock.fetchone = Mock(return_value=None)
    cursor_mock.__enter__ = Mock(return_value=cursor_mock)
    cursor_mock.__exit__ = Mock(return_value=False)

    db.get_cursor = Mock(return_value=cursor_mock)

    # Mock connection pour les DAOs qui utilisent db.connection.cursor()
    connection_mock = Mock()
    connection_cursor = Mock()
    connection_cursor.lastrowid = 1
    connection_mock.cursor = Mock(return_value=connection_cursor)
    db.connection = connection_mock

    return db


@pytest.fixture
def mock_connection():
    """Mock de connexion DB"""
    conn = Mock()
    cursor = Mock()
    cursor.fetchall = Mock(return_value=[])
    cursor.fetchone = Mock(return_value=None)
    cursor.lastrowid = 1
    conn.cursor = Mock(return_value=cursor)
    return conn


# ==================== FIXTURES MODELS ====================

@pytest.fixture
def sample_societe():
    """Fixture Societe"""
    return Societe(
        id=1,
        nom="Test SARL",
        siren="123456789",
        code_postal="75001",
        ville="Paris",
        pays="FR",
        date_creation=date(2024, 1, 1)
    )


@pytest.fixture
def sample_exercice(sample_societe):
    """Fixture Exercice"""
    return Exercice(
        id=1,
        societe_id=sample_societe.id,
        annee=2025,
        date_debut=date(2025, 1, 1),
        date_fin=date(2025, 12, 31),
        cloture=False
    )


@pytest.fixture
def sample_journal(sample_societe):
    """Fixture Journal"""
    return Journal(
        id=1,
        societe_id=sample_societe.id,
        code="VE",
        libelle="Ventes",
        type="ventes"
    )


@pytest.fixture
def sample_compte(sample_societe):
    """Fixture Compte"""
    return Compte(
        id=1,
        societe_id=sample_societe.id,
        compte="411000",
        intitule="Clients",
        classe="4",
        type_compte="actif",
        lettrable=True
    )


@pytest.fixture
def sample_tiers(sample_societe):
    """Fixture Tiers"""
    return Tiers(
        id=1,
        societe_id=sample_societe.id,
        code_aux="CLI001",
        nom="Client Test",
        type="CLIENT",
        adresse="5 Avenue Test",
        ville="Lyon",
        pays="FR"
    )


@pytest.fixture
def sample_ecriture(sample_exercice, sample_journal):
    """Fixture Ecriture"""
    return Ecriture(
        id=1,
        societe_id=1,
        exercice_id=sample_exercice.id,
        journal_id=sample_journal.id,
        numero="VE001",
        date_ecriture=date(2025, 1, 15),
        reference_piece="FACT001",
        libelle="Vente marchandises",
        validee=True,
        mouvements=[]
    )


@pytest.fixture
def sample_mouvement(sample_ecriture, sample_compte):
    """Fixture Mouvement"""
    return Mouvement(
        id=1,
        ecriture_id=sample_ecriture.id,
        compte_id=sample_compte.id,
        libelle="Client XYZ",
        debit=Decimal("120.00"),
        credit=Decimal("0.00"),
        lettrage_code=None
    )


@pytest.fixture
def sample_balance(sample_societe, sample_exercice, sample_compte):
    """Fixture Balance"""
    return Balance(
        societe_id=sample_societe.id,
        exercice_id=sample_exercice.id,
        compte_id=sample_compte.id,
        compte=sample_compte.compte,
        intitule=sample_compte.intitule,
        classe=sample_compte.classe,
        total_debit=Decimal("1000.00"),
        total_credit=Decimal("800.00"),
        solde=Decimal("200.00")
    )


# ==================== FIXTURES DAOs ====================

@pytest.fixture
def mock_societe_dao():
    """Mock SocieteDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.get_by_id = Mock(return_value=None)
    return dao


@pytest.fixture
def mock_exercice_dao():
    """Mock ExerciceDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.get_by_id = Mock(return_value=None)
    dao.get_current = Mock(return_value=None)
    return dao


@pytest.fixture
def mock_journal_dao():
    """Mock JournalDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.get_by_code = Mock(return_value=None)
    return dao


@pytest.fixture
def mock_compte_dao():
    """Mock CompteDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.get_by_numero = Mock(return_value=None)
    dao.get_by_classe = Mock(return_value=[])
    dao.search = Mock(return_value=[])
    return dao


@pytest.fixture
def mock_tiers_dao():
    """Mock TiersDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.get_by_id = Mock(return_value=None)
    dao.create = Mock(return_value=1)
    return dao


@pytest.fixture
def mock_ecriture_dao():
    """Mock EcritureDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.get_by_id = Mock(return_value=None)
    dao.create = Mock(return_value=1)
    dao.get_next_numero = Mock(return_value="VE001")
    dao.get_grand_livre = Mock(return_value=[])
    dao.get_mouvements_a_lettrer = Mock(return_value=[])
    dao.get_mouvements_lettres = Mock(return_value=[])
    dao.get_aggregat_mouvements = Mock(return_value=[])
    dao.get_last_lettrage_code = Mock(return_value="AA")
    dao.set_lettrage = Mock()
    dao.delettrer_mouvements = Mock(return_value=2)
    return dao


@pytest.fixture
def mock_balance_dao():
    """Mock BalanceDAO"""
    dao = Mock()
    dao.get_all = Mock(return_value=[])
    dao.calculer = Mock()
    return dao


@pytest.fixture
def mock_reporting_dao():
    """Mock ReportingDAO"""
    dao = Mock()
    dao.get_compte_resultat = Mock(return_value=[])
    dao.get_bilan = Mock(return_value=[])
    dao.get_tva_recap = Mock(return_value=[])
    return dao


@pytest.fixture
def mock_procedure_dao():
    """Mock ProcedureDAO"""
    dao = Mock()
    dao.cloturer_exercice = Mock()
    dao.exporter_fec = Mock()
    dao.tester_comptabilite = Mock(return_value=[[{}]])
    return dao


# ==================== FIXTURES SERVICE ====================

@pytest.fixture
def comptabilite_service(
    mock_db,
    mock_societe_dao,
    mock_exercice_dao,
    mock_journal_dao,
    mock_compte_dao,
    mock_tiers_dao,
    mock_ecriture_dao,
    mock_balance_dao,
    mock_reporting_dao,
    mock_procedure_dao
):
    """Fixture ComptabiliteService avec tous les mocks"""
    from src.application.services import ComptabiliteService

    return ComptabiliteService(
        db=mock_db,
        societe_repo=mock_societe_dao,
        exercice_repo=mock_exercice_dao,
        journal_repo=mock_journal_dao,
        compte_repo=mock_compte_dao,
        tiers_repo=mock_tiers_dao,
        ecriture_repo=mock_ecriture_dao,
        balance_repo=mock_balance_dao,
        reporting_repo=mock_reporting_dao,
        procedure_repo=mock_procedure_dao
    )


# ==================== UTILITIES ====================

@pytest.fixture
def faker_instance():
    """Instance Faker pour générer des données"""
    return Faker('fr_FR')
