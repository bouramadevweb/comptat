"""
Interfaces de repositories pour découpler l'application de l'infrastructure.
Ces protocoles décrivent les opérations nécessaires aux services applicatifs.
"""
from typing import Protocol, List, Optional, Any
from src.domain.models import (
    Societe,
    Exercice,
    Journal,
    Compte,
    Tiers,
    Ecriture,
    Balance,
)
from decimal import Decimal


class DatabaseGateway(Protocol):
    """Contrat minimal pour exécuter des requêtes ou procédures stockées."""

    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: bool = True) -> Any:
        ...

    def call_procedure(self, proc_name: str, params: Optional[tuple] = None) -> Any:
        ...


class SocieteRepository(Protocol):
    def get_all(self) -> List[Societe]:
        ...

    def get_by_id(self, societe_id: int) -> Optional[Societe]:
        ...


class ExerciceRepository(Protocol):
    def get_all(self, societe_id: int) -> List[Exercice]:
        ...

    def get_by_id(self, exercice_id: int) -> Optional[Exercice]:
        ...

    def get_current(self, societe_id: int) -> Optional[Exercice]:
        ...


class JournalRepository(Protocol):
    def get_all(self, societe_id: int) -> List[Journal]:
        ...

    def get_by_code(self, societe_id: int, code: str) -> Optional[Journal]:
        ...


class CompteRepository(Protocol):
    def get_all(self, societe_id: int) -> List[Compte]:
        ...

    def get_by_numero(self, societe_id: int, numero: str) -> Optional[Compte]:
        ...

    def get_by_classe(self, societe_id: int, classe: str) -> List[Compte]:
        ...

    def search(self, societe_id: int, search_term: str) -> List[Compte]:
        ...


class TiersRepository(Protocol):
    def get_all(self, societe_id: int, type_tiers: Optional[str] = None) -> List[Tiers]:
        ...

    def get_by_id(self, tiers_id: int) -> Optional[Tiers]:
        ...

    def create(self, tiers: Tiers) -> int:
        ...


class EcritureRepository(Protocol):
    def get_all(self, exercice_id: int, journal_id: Optional[int] = None) -> List[Ecriture]:
        ...

    def get_by_id(self, ecriture_id: int) -> Optional[Ecriture]:
        ...

    def create(self, ecriture: Ecriture) -> int:
        ...

    def get_next_numero(self, exercice_id: int, journal_id: int) -> str:
        ...

    def get_grand_livre(self, societe_id: int, exercice_id: int, compte_numero: str) -> List[dict]:
        ...

    def get_mouvements_a_lettrer(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str,
        tiers_id: Optional[int] = None
    ) -> List[dict]:
        ...

    def get_aggregat_mouvements(self, mouvement_ids: List[int]) -> Optional[dict]:
        ...

    def get_last_lettrage_code(self) -> Optional[str]:
        ...

    def set_lettrage(self, mouvement_ids: List[int], code_lettrage: str) -> int:
        ...

    def delettrer_mouvements(self, code_lettrage: str) -> int:
        ...

    def get_mouvements_lettres(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str
    ) -> List[dict]:
        ...


class BalanceRepository(Protocol):
    def get_all(self, societe_id: int, exercice_id: int) -> List[Balance]:
        ...

    def calculer(self, societe_id: int, exercice_id: int):
        ...


class ReportingRepository(Protocol):
    """Requêtes de reporting / états financiers."""

    def get_compte_resultat(self, societe_id: int, exercice_id: int) -> List[dict]:
        ...

    def get_bilan(self, societe_id: int, exercice_id: int) -> List[dict]:
        ...

    def get_tva_recap(self, societe_id: int, exercice_id: int) -> List[dict]:
        ...


class ProcedureRepository(Protocol):
    """Appels aux procédures stockées."""

    def cloturer_exercice(self, societe_id: int, exercice_id: int):
        ...

    def exporter_fec(self, societe_id: int, exercice_id: int):
        ...

    def tester_comptabilite(self, societe_id: int, exercice_id: int):
        ...
