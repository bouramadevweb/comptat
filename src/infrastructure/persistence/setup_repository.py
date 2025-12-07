"""
Repository d'initialisation (créations en masse pour une nouvelle société).
Centralise les INSERT SQL afin que les scripts n'appellent plus directement la DB.
"""
from datetime import date
from typing import List, Tuple
from src.infrastructure.persistence.database import DatabaseManager


class SetupRepository:
    """Opérations de création initiale (société, exercice, journaux, comptes, TVA, tiers)."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_societe(self, nom: str, siren: str, adresse: str, code_postal: str, ville: str) -> int:
        query = """
            INSERT INTO SOCIETES (nom, pays, siren, code_postal, ville, date_creation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db.execute_query(
            query,
            (nom, 'FR', siren, code_postal, ville, date.today()),
            fetch=False
        )
        result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        return result[0]['id']

    def create_exercice(self, societe_id: int, annee: int) -> int:
        query = """
            INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
            VALUES (%s, %s, %s, %s, FALSE)
        """
        self.db.execute_query(
            query,
            (societe_id, annee, date(annee, 1, 1), date(annee, 12, 31)),
            fetch=False
        )
        result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        return result[0]['id']

    def create_journaux(self, societe_id: int, journaux: List[Tuple[str, str, str]]):
        query = """
            INSERT INTO JOURNAUX (societe_id, code, libelle, type, compteur)
            VALUES (%s, %s, %s, %s, 0)
        """
        for code, libelle, type_journal in journaux:
            self.db.execute_query(query, (societe_id, code, libelle, type_journal), fetch=False)

    def insert_comptes(self, societe_id: int, comptes: List[Tuple[str, str, str, str, bool]]):
        """
        comptes: liste de tuples (compte, intitule, classe, type_compte, lettrable)
        """
        query = """
            INSERT INTO COMPTES (societe_id, compte, intitule, classe, type_compte, lettrable)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for compte, intitule, classe, type_compte, lettrable in comptes:
            self.db.execute_query(
                query,
                (societe_id, compte, intitule, classe, type_compte, lettrable),
                fetch=False
            )

    def get_compte_id(self, societe_id: int, numero: str):
        query = "SELECT id FROM COMPTES WHERE societe_id = %s AND compte = %s"
        result = self.db.execute_query(query, (societe_id, numero))
        return result[0]['id'] if result else None

    def create_tva(self, societe_id: int, taux: List[Tuple[str, str, float]], compte_collecte_id: int, compte_deductible_id: int):
        query = """
            INSERT INTO TAXES (societe_id, code, nom, taux, compte_collecte_id, compte_deductible_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for code, nom, taux_value in taux:
            self.db.execute_query(
                query,
                (societe_id, code, nom, taux_value, compte_collecte_id, compte_deductible_id),
                fetch=False
            )

    def create_tiers(self, societe_id: int, tiers: List[Tuple[str, str, str, str, str]]):
        """
        tiers: liste (code_aux, nom, type_tiers, adresse, ville)
        """
        query = """
            INSERT INTO TIERS (societe_id, code_aux, nom, type, adresse, ville, pays)
            VALUES (%s, %s, %s, %s, %s, %s, 'FR')
        """
        for code_aux, nom, type_tiers, adresse, ville in tiers:
            self.db.execute_query(
                query,
                (societe_id, code_aux, nom, type_tiers, adresse, ville),
                fetch=False
            )
