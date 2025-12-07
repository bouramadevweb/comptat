"""
DAO - Data Access Objects pour les opérations CRUD
"""
from typing import List, Optional
from decimal import Decimal
from src.infrastructure.persistence.database import DatabaseManager
from src.domain.models import *
import logging

logger = logging.getLogger(__name__)


class BaseDAO:
    """Classe de base pour tous les DAO"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager


class SocieteDAO(BaseDAO):
    """DAO pour la gestion des sociétés"""
    
    def get_all(self) -> List[Societe]:
        """Récupère toutes les sociétés"""
        query = "SELECT * FROM SOCIETES ORDER BY nom"
        rows = self.db.execute_query(query)
        return [Societe(**row) for row in rows]
    
    def get_by_id(self, societe_id: int) -> Optional[Societe]:
        """Récupère une société par son ID"""
        query = "SELECT * FROM SOCIETES WHERE id = %s"
        rows = self.db.execute_query(query, (societe_id,))
        return Societe(**rows[0]) if rows else None
    
    def create(self, societe: Societe) -> int:
        """Crée une nouvelle société"""
        query = """
            INSERT INTO SOCIETES (nom, pays, siren, code_postal, ville, date_creation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db.execute_query(
            query,
            (societe.nom, societe.pays, societe.siren, societe.code_postal,
             societe.ville, societe.date_creation),
            fetch=False
        )
        return self.db.connection.cursor().lastrowid


class ExerciceDAO(BaseDAO):
    """DAO pour la gestion des exercices comptables"""
    
    def get_all(self, societe_id: int) -> List[Exercice]:
        """Récupère tous les exercices d'une société"""
        query = """
            SELECT * FROM EXERCICES 
            WHERE societe_id = %s 
            ORDER BY annee DESC
        """
        rows = self.db.execute_query(query, (societe_id,))
        return [Exercice(**row) for row in rows]
    
    def get_by_id(self, exercice_id: int) -> Optional[Exercice]:
        """Récupère un exercice par son ID"""
        query = "SELECT * FROM EXERCICES WHERE id = %s"
        rows = self.db.execute_query(query, (exercice_id,))
        return Exercice(**rows[0]) if rows else None
    
    def get_current(self, societe_id: int) -> Optional[Exercice]:
        """Récupère l'exercice en cours (non clôturé)"""
        query = """
            SELECT * FROM EXERCICES 
            WHERE societe_id = %s AND cloture = FALSE 
            ORDER BY annee DESC 
            LIMIT 1
        """
        rows = self.db.execute_query(query, (societe_id,))
        return Exercice(**rows[0]) if rows else None
    
    def create(self, exercice: Exercice) -> int:
        """Crée un nouvel exercice"""
        query = """
            INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(
            query,
            (exercice.societe_id, exercice.annee, exercice.date_debut,
             exercice.date_fin, exercice.cloture),
            fetch=False
        )
        return self.db.connection.cursor().lastrowid


class JournalDAO(BaseDAO):
    """DAO pour la gestion des journaux"""
    
    def get_all(self, societe_id: int) -> List[Journal]:
        """Récupère tous les journaux d'une société"""
        query = "SELECT * FROM JOURNAUX WHERE societe_id = %s ORDER BY code"
        rows = self.db.execute_query(query, (societe_id,))
        return [Journal(**row) for row in rows]
    
    def get_by_code(self, societe_id: int, code: str) -> Optional[Journal]:
        """Récupère un journal par son code"""
        query = "SELECT * FROM JOURNAUX WHERE societe_id = %s AND code = %s"
        rows = self.db.execute_query(query, (societe_id, code))
        return Journal(**rows[0]) if rows else None


class CompteDAO(BaseDAO):
    """DAO pour la gestion des comptes"""
    
    def get_all(self, societe_id: int) -> List[Compte]:
        """Récupère tous les comptes d'une société"""
        query = "SELECT * FROM COMPTES WHERE societe_id = %s ORDER BY compte"
        rows = self.db.execute_query(query, (societe_id,))
        return [Compte(**row) for row in rows]
    
    def get_by_numero(self, societe_id: int, numero: str) -> Optional[Compte]:
        """Récupère un compte par son numéro"""
        query = "SELECT * FROM COMPTES WHERE societe_id = %s AND compte = %s"
        rows = self.db.execute_query(query, (societe_id, numero))
        return Compte(**rows[0]) if rows else None
    
    def get_by_classe(self, societe_id: int, classe: str) -> List[Compte]:
        """Récupère les comptes d'une classe donnée"""
        query = "SELECT * FROM COMPTES WHERE societe_id = %s AND classe = %s ORDER BY compte"
        rows = self.db.execute_query(query, (societe_id, classe))
        return [Compte(**row) for row in rows]
    
    def search(self, societe_id: int, search_term: str) -> List[Compte]:
        """Recherche des comptes par numéro ou intitulé"""
        query = """
            SELECT * FROM COMPTES 
            WHERE societe_id = %s 
            AND (compte LIKE %s OR intitule LIKE %s)
            ORDER BY compte
            LIMIT 50
        """
        search = f"%{search_term}%"
        rows = self.db.execute_query(query, (societe_id, search, search))
        return [Compte(**row) for row in rows]


class TiersDAO(BaseDAO):
    """DAO pour la gestion des tiers"""
    
    def get_all(self, societe_id: int, type_tiers: Optional[str] = None) -> List[Tiers]:
        """Récupère tous les tiers d'une société"""
        if type_tiers:
            query = "SELECT * FROM TIERS WHERE societe_id = %s AND type = %s ORDER BY nom"
            rows = self.db.execute_query(query, (societe_id, type_tiers))
        else:
            query = "SELECT * FROM TIERS WHERE societe_id = %s ORDER BY nom"
            rows = self.db.execute_query(query, (societe_id,))
        return [Tiers(**row) for row in rows]
    
    def get_by_id(self, tiers_id: int) -> Optional[Tiers]:
        """Récupère un tiers par son ID"""
        query = "SELECT * FROM TIERS WHERE id = %s"
        rows = self.db.execute_query(query, (tiers_id,))
        return Tiers(**rows[0]) if rows else None
    
    def create(self, tiers: Tiers) -> int:
        """Crée un nouveau tiers"""
        query = """
            INSERT INTO TIERS (societe_id, code_aux, nom, type, adresse, ville, pays)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (tiers.societe_id, tiers.code_aux, tiers.nom, tiers.type,
                 tiers.adresse, tiers.ville, tiers.pays)
            )
            return cursor.lastrowid

    def update(self, tiers: Tiers) -> bool:
        """Met à jour un tiers existant"""
        query = """
            UPDATE TIERS
            SET code_aux = %s, nom = %s, type = %s, adresse = %s, ville = %s, pays = %s
            WHERE id = %s
        """
        try:
            self.db.execute_query(
                query,
                (tiers.code_aux, tiers.nom, tiers.type, tiers.adresse,
                 tiers.ville, tiers.pays, tiers.id),
                fetch=False
            )
            logger.info(f"✅ Tiers {tiers.id} mis à jour")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour tiers {tiers.id}: {e}")
            return False

    def delete(self, tiers_id: int) -> bool:
        """Supprime un tiers (si non utilisé dans des écritures)"""
        # Vérifier si le tiers est utilisé dans des mouvements
        check_query = "SELECT COUNT(*) as nb FROM MOUVEMENTS WHERE tiers_id = %s"
        result = self.db.execute_query(check_query, (tiers_id,))

        if result and result[0]['nb'] > 0:
            logger.warning(f"⚠️ Impossible de supprimer le tiers {tiers_id}: utilisé dans {result[0]['nb']} mouvement(s)")
            return False

        try:
            query = "DELETE FROM TIERS WHERE id = %s"
            self.db.execute_query(query, (tiers_id,), fetch=False)
            logger.info(f"✅ Tiers {tiers_id} supprimé")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur suppression tiers {tiers_id}: {e}")
            return False


class EcritureDAO(BaseDAO):
    """DAO pour la gestion des écritures comptables"""
    
    def get_all(self, exercice_id: int, journal_id: Optional[int] = None) -> List[Ecriture]:
        """Récupère toutes les écritures d'un exercice"""
        if journal_id:
            query = """
                SELECT * FROM ECRITURES 
                WHERE exercice_id = %s AND journal_id = %s 
                ORDER BY date_ecriture DESC, numero DESC
            """
            rows = self.db.execute_query(query, (exercice_id, journal_id))
        else:
            query = """
                SELECT * FROM ECRITURES 
                WHERE exercice_id = %s 
                ORDER BY date_ecriture DESC, numero DESC
            """
            rows = self.db.execute_query(query, (exercice_id,))
        return [Ecriture(**row) for row in rows]
    
    def get_by_id(self, ecriture_id: int) -> Optional[Ecriture]:
        """Récupère une écriture avec ses mouvements"""
        query = "SELECT * FROM ECRITURES WHERE id = %s"
        rows = self.db.execute_query(query, (ecriture_id,))
        if not rows:
            return None
        
        ecriture = Ecriture(**rows[0])
        
        # Récupérer les mouvements
        query_mvts = """
            SELECT m.*, c.compte as compte_numero 
            FROM MOUVEMENTS m
            JOIN COMPTES c ON c.id = m.compte_id
            WHERE m.ecriture_id = %s
            ORDER BY m.id
        """
        mvts = self.db.execute_query(query_mvts, (ecriture_id,))
        ecriture.mouvements = [Mouvement(**mvt) for mvt in mvts]
        
        return ecriture
    
    def create(self, ecriture: Ecriture) -> int:
        """Crée une nouvelle écriture avec ses mouvements"""
        # Créer l'en-tête
        query = """
            INSERT INTO ECRITURES 
            (societe_id, exercice_id, journal_id, numero, date_ecriture, 
             reference_piece, libelle, validee, date_validation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with self.db.get_cursor(dictionary=False) as cursor:
            cursor.execute(query, (
                ecriture.societe_id, ecriture.exercice_id, ecriture.journal_id,
                ecriture.numero, ecriture.date_ecriture, ecriture.reference_piece,
                ecriture.libelle, ecriture.validee, ecriture.date_validation
            ))
            ecriture_id = cursor.lastrowid
            
            # Créer les mouvements
            if ecriture.mouvements:
                query_mvt = """
                    INSERT INTO MOUVEMENTS 
                    (ecriture_id, compte_id, tiers_id, libelle, debit, credit, lettrage_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = [
                    (ecriture_id, mvt.compte_id, mvt.tiers_id, mvt.libelle,
                     mvt.debit, mvt.credit, mvt.lettrage_code)
                    for mvt in ecriture.mouvements
                ]
                cursor.executemany(query_mvt, params)
        
        return ecriture_id
    
    def get_next_numero(self, exercice_id: int, journal_id: int) -> str:
        """Génère le prochain numéro d'écriture"""
        query = """
            SELECT j.code, ex.annee, MAX(CAST(SUBSTRING(e.numero, -5) AS UNSIGNED)) as max_num
            FROM JOURNAUX j
            JOIN EXERCICES ex ON ex.societe_id = j.societe_id
            LEFT JOIN ECRITURES e ON e.journal_id = j.id AND e.exercice_id = ex.id
            WHERE j.id = %s AND ex.id = %s
            GROUP BY j.code, ex.annee
        """
        rows = self.db.execute_query(query, (journal_id, exercice_id))
        if rows and rows[0]['max_num']:
            next_num = int(rows[0]['max_num']) + 1
            code = rows[0]['code']
            annee = rows[0]['annee']
        else:
            # Récupérer le code et l'année séparément
            query2 = """
                SELECT j.code, ex.annee
                FROM JOURNAUX j, EXERCICES ex
                WHERE j.id = %s AND ex.id = %s
            """
            rows2 = self.db.execute_query(query2, (journal_id, exercice_id))
            code = rows2[0]['code']
            annee = rows2[0]['annee']
            next_num = 1
        
        return f"{code}-{annee}-{next_num:05d}"

    def get_grand_livre(self, societe_id: int, exercice_id: int, compte_numero: str) -> List[dict]:
        """Récupère les mouvements d'un compte pour le Grand Livre"""
        query = """
            SELECT
                e.date_ecriture,
                j.code as journal_code,
                e.numero as ecriture_numero,
                e.reference_piece,
                m.libelle,
                m.debit,
                m.credit,
                m.lettrage_code,
                c.compte
            FROM MOUVEMENTS m
            JOIN ECRITURES e ON e.id = m.ecriture_id
            JOIN JOURNAUX j ON j.id = e.journal_id
            JOIN COMPTES c ON c.id = m.compte_id
            WHERE e.societe_id = %s
            AND e.exercice_id = %s
            AND c.compte = %s
            AND e.validee = 1
            ORDER BY e.date_ecriture, e.numero
        """
        return self.db.execute_query(query, (societe_id, exercice_id, compte_numero))

    def get_mouvements_a_lettrer(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str,
        tiers_id: Optional[int] = None
    ) -> List[dict]:
        """Récupère les mouvements non lettrés d'un compte"""
        query = """
            SELECT
                m.id as mouvement_id,
                e.numero as ecriture_numero,
                e.date_ecriture as date,
                e.reference_piece as reference,
                m.libelle as libelle,
                m.debit as debit,
                m.credit as credit,
                (m.debit - m.credit) as solde,
                m.lettrage_code as lettrage,
                t.code_aux as tiers_code,
                t.nom as tiers_nom
            FROM MOUVEMENTS m
            JOIN ECRITURES e ON e.id = m.ecriture_id
            JOIN COMPTES c ON c.id = m.compte_id
            LEFT JOIN TIERS t ON t.id = m.tiers_id
            WHERE e.societe_id = %s
            AND e.exercice_id = %s
            AND c.compte = %s
            AND (m.lettrage_code IS NULL OR m.lettrage_code = '')
            AND e.validee = 1
        """
        params = [societe_id, exercice_id, compte_numero]
        if tiers_id:
            query += " AND m.tiers_id = %s"
            params.append(tiers_id)
        query += " ORDER BY e.date_ecriture, e.numero"
        return self.db.execute_query(query, tuple(params))

    def get_aggregat_mouvements(self, mouvement_ids: List[int]) -> Optional[dict]:
        """Retourne les agrégats débit/crédit/solde pour une liste d'IDs"""
        if not mouvement_ids:
            return None
        query = """
            SELECT
                SUM(debit) as total_debit,
                SUM(credit) as total_credit,
                SUM(debit - credit) as solde
            FROM MOUVEMENTS
            WHERE id IN (%s)
        """ % ','.join(['%s'] * len(mouvement_ids))
        result = self.db.execute_query(query, tuple(mouvement_ids))
        return result[0] if result else None

    def get_last_lettrage_code(self) -> Optional[str]:
        """Récupère le dernier code de lettrage utilisé"""
        query = """
            SELECT lettrage_code
            FROM MOUVEMENTS
            WHERE lettrage_code IS NOT NULL AND lettrage_code != ''
            ORDER BY lettrage_code DESC
            LIMIT 1
        """
        result = self.db.execute_query(query)
        return result[0]['lettrage_code'] if result and result[0]['lettrage_code'] else None

    def set_lettrage(self, mouvement_ids: List[int], code_lettrage: str) -> int:
        """Applique un code de lettrage à une liste de mouvements"""
        if not mouvement_ids:
            return 0
        query = """
            UPDATE MOUVEMENTS
            SET lettrage_code = %s
            WHERE id IN (%s)
        """ % ','.join(['%s'] * len(mouvement_ids))
        params = [code_lettrage] + mouvement_ids
        return self.db.execute_query(query, tuple(params), fetch=False)

    def delettrer_mouvements(self, code_lettrage: str) -> int:
        """Supprime le lettrage pour un code donné"""
        query = """
            UPDATE MOUVEMENTS
            SET lettrage_code = NULL
            WHERE lettrage_code = %s
        """
        return self.db.execute_query(query, (code_lettrage,), fetch=False)

    def get_mouvements_lettres(
        self,
        societe_id: int,
        exercice_id: int,
        compte_numero: str
    ) -> List[dict]:
        """Récupère les mouvements lettrés groupés par code"""
        query = """
            SELECT
                m.id as mouvement_id,
                e.numero as ecriture_numero,
                e.date_ecriture as date,
                e.reference_piece as reference,
                m.libelle as libelle,
                m.debit as debit,
                m.credit as credit,
                m.lettrage_code as lettrage
            FROM MOUVEMENTS m
            JOIN ECRITURES e ON e.id = m.ecriture_id
            JOIN COMPTES c ON c.id = m.compte_id
            WHERE e.societe_id = %s
            AND e.exercice_id = %s
            AND c.compte = %s
            AND m.lettrage_code IS NOT NULL
            AND m.lettrage_code != ''
            ORDER BY m.lettrage_code, e.date_ecriture
        """
        return self.db.execute_query(query, (societe_id, exercice_id, compte_numero))


class BalanceDAO(BaseDAO):
    """DAO pour la gestion de la balance"""
    
    def get_all(self, societe_id: int, exercice_id: int) -> List[Balance]:
        """Récupère toute la balance"""
        query = """
            SELECT b.*, c.compte as compte
            FROM BALANCE b
            JOIN COMPTES c ON c.id = b.compte_id
            WHERE b.societe_id = %s AND b.exercice_id = %s 
            ORDER BY c.compte
        """
        rows = self.db.execute_query(query, (societe_id, exercice_id))
        return [Balance(**row) for row in rows]
    
    def calculer(self, societe_id: int, exercice_id: int):
        """Recalcule la balance via procédure stockée"""
        self.db.call_procedure('Calculer_Balance', (societe_id, exercice_id))
        logger.info("✅ Balance recalculée")


class ReportingDAO(BaseDAO):
    """DAO pour les requêtes de reporting/états financiers"""

    def get_compte_resultat(self, societe_id: int, exercice_id: int) -> List[dict]:
        query = """
            SELECT 
                CASE WHEN c.classe = '6' THEN 'CHARGES'
                     WHEN c.classe = '7' THEN 'PRODUITS' END AS categorie,
                c.compte, c.intitule,
                COALESCE(SUM(
                    CASE 
                        WHEN c.classe = '6' THEN m.debit - m.credit      -- charges >0 si débit
                        WHEN c.classe = '7' THEN m.credit - m.debit      -- produits >0 si crédit
                        ELSE 0
                    END
                ), 0) AS solde
            FROM COMPTES c
            LEFT JOIN MOUVEMENTS m ON c.id = m.compte_id
            LEFT JOIN ECRITURES e ON e.id = m.ecriture_id
            WHERE c.societe_id = %s 
            AND c.classe IN ('6','7')
            AND (e.exercice_id = %s OR e.exercice_id IS NULL)
            GROUP BY categorie, c.compte, c.intitule
            ORDER BY categorie, c.compte
        """
        return self.db.execute_query(query, (societe_id, exercice_id))

    def get_bilan(self, societe_id: int, exercice_id: int) -> List[dict]:
        query = """
            SELECT 
                c.compte,
                c.intitule,
                c.type_compte,
                c.classe,
                COALESCE(SUM(m.debit), 0) as total_debit,
                COALESCE(SUM(m.credit), 0) as total_credit,
                COALESCE(SUM(m.debit - m.credit), 0) as solde
            FROM COMPTES c
            LEFT JOIN MOUVEMENTS m ON c.id = m.compte_id
            LEFT JOIN ECRITURES e ON m.ecriture_id = e.id
            WHERE c.societe_id = %s
                AND c.classe IN ('1', '2', '3', '4', '5')
                AND (e.exercice_id = %s OR e.exercice_id IS NULL)
            GROUP BY c.id, c.compte, c.intitule, c.type_compte, c.classe
            HAVING ABS(COALESCE(SUM(m.debit - m.credit), 0)) > 0.001
            ORDER BY c.compte
        """
        return self.db.execute_query(query, (societe_id, exercice_id))

    def get_tva_recap(self, societe_id: int, exercice_id: int) -> List[dict]:
        query = """
            SELECT 
                CASE 
                    WHEN c.compte LIKE '4457%' THEN 'TVA Collectée'
                    WHEN c.compte LIKE '4456%' THEN 'TVA Déductible'
                    ELSE 'Autre TVA'
                END AS type_tva,
                c.compte, c.intitule,
                COALESCE(SUM(m.debit - m.credit), 0) AS solde
            FROM COMPTES c
            JOIN MOUVEMENTS m ON m.compte_id = c.id
            JOIN ECRITURES e ON e.id = m.ecriture_id
            WHERE c.societe_id = %s
            AND e.exercice_id = %s
            AND c.compte LIKE '445%'
            GROUP BY type_tva, c.compte, c.intitule
            ORDER BY c.compte
        """
        return self.db.execute_query(query, (societe_id, exercice_id))


class ProcedureDAO(BaseDAO):
    """DAO pour les procédures stockées."""

    def cloturer_exercice(self, societe_id: int, exercice_id: int):
        return self.db.call_procedure('Cloturer_Exercice', (societe_id, exercice_id))

    def exporter_fec(self, societe_id: int, exercice_id: int):
        return self.db.call_procedure('Exporter_FEC_Exercice', (societe_id, exercice_id))

    def tester_comptabilite(self, societe_id: int, exercice_id: int):
        return self.db.call_procedure('Tester_Comptabilite_Avancee', (societe_id, exercice_id))
