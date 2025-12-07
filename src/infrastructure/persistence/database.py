"""
Gestionnaire de connexion à la base de données MySQL
Version améliorée avec pool de connexions et gestion avancée des erreurs
"""
import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from src.infrastructure.configuration.config import Config
import logging
import time
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données"""
    pass


class DatabaseManager:
    """Gestionnaire de connexion et d'opérations sur la base de données"""

    # Pool de connexions partagé
    _connection_pool: Optional[pooling.MySQLConnectionPool] = None

    def __init__(self):
        self.config = Config.get_db_config()
        self.connection = None
        self._init_pool()

    def _init_pool(self):
        """Initialise le pool de connexions (singleton)"""
        if DatabaseManager._connection_pool is None:
            try:
                pool_config = self.config.copy()
                DatabaseManager._connection_pool = pooling.MySQLConnectionPool(
                    pool_name="compta_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **pool_config
                )
                logger.info("✅ Pool de connexions initialisé (taille: 5)")
            except Error as e:
                logger.error(f"❌ Erreur initialisation pool : {e}")
                raise DatabaseError(f"Impossible d'initialiser le pool de connexions: {e}")

    def connect(self, use_pool: bool = True):
        """
        Établir une connexion à la base de données
        Args:
            use_pool: Si True, utilise le pool de connexions (recommandé)
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if use_pool and DatabaseManager._connection_pool:
                    self.connection = DatabaseManager._connection_pool.get_connection()
                    logger.debug("📊 Connexion obtenue du pool")
                else:
                    self.connection = mysql.connector.connect(**self.config)
                    logger.debug("🔗 Connexion directe établie")
            return self.connection
        except Error as e:
            logger.error(f"❌ Erreur de connexion : {e}")
            raise DatabaseError(f"Impossible de se connecter à la base de données: {e}")
    
    def disconnect(self):
        """Fermer la connexion à la base de données"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 Connexion fermée")
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager pour obtenir un curseur"""
        connection = self.connect()
        cursor = connection.cursor(dictionary=dictionary)
        try:
            yield cursor
            connection.commit()
        except Error as e:
            connection.rollback()
            logger.error(f"❌ Erreur lors de l'exécution : {e}")
            raise DatabaseError(f"Erreur d'exécution SQL: {e}")
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        """
        Context manager pour gérer une transaction explicite
        Usage:
            with db.transaction():
                db.execute_query(...)
                db.execute_query(...)
                # Commit automatique si aucune exception
                # Rollback automatique en cas d'exception
        """
        connection = self.connect()
        connection.start_transaction()
        try:
            yield connection
            connection.commit()
            logger.debug("✅ Transaction validée")
        except Exception as e:
            connection.rollback()
            logger.error(f"❌ Transaction annulée : {e}")
            raise DatabaseError(f"Erreur de transaction: {e}")

    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: bool = True, retry: int = 3) -> Any:
        """
        Exécuter une requête SQL avec retry automatique
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            fetch: Si True, retourne les résultats
            retry: Nombre de tentatives en cas d'erreur
        """
        last_error = None
        for attempt in range(retry):
            try:
                with self.get_cursor() as cursor:
                    cursor.execute(query, params or ())
                    if fetch:
                        return cursor.fetchall()
                    return cursor.rowcount
            except Error as e:
                last_error = e
                if attempt < retry - 1:
                    logger.warning(f"⚠️ Tentative {attempt + 1}/{retry} échouée, nouvelle tentative...")
                    time.sleep(0.5 * (attempt + 1))  # Backoff exponentiel
                else:
                    logger.error(f"❌ Échec après {retry} tentatives : {e}")

        raise DatabaseError(f"Échec de la requête après {retry} tentatives: {last_error}")

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Exécuter plusieurs requêtes avec différents paramètres"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def call_procedure(self, proc_name: str, params: Optional[tuple] = None) -> List[List[Dict]]:
        """Appeler une procédure stockée"""
        with self.get_cursor() as cursor:
            cursor.callproc(proc_name, params or ())
            results = []
            for result in cursor.stored_results():
                results.append(result.fetchall())
            return results

    def test_connection(self) -> bool:
        """
        Teste la connexion à la base de données
        Returns:
            True si la connexion fonctionne, False sinon
        """
        try:
            result = self.execute_query("SELECT 1 as test")
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"❌ Test de connexion échoué : {e}")
            return False

    def get_database_info(self) -> Dict[str, str]:
        """
        Récupère les informations sur la base de données
        """
        try:
            result = self.execute_query(
                "SELECT DATABASE() as db_name, VERSION() as version, USER() as user"
            )
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(f"❌ Erreur récupération info BDD : {e}")
            return {}

    def get_table_stats(self) -> List[Dict]:
        """
        Récupère les statistiques des tables
        """
        try:
            query = """
                SELECT
                    TABLE_NAME as table_name,
                    TABLE_ROWS as row_count,
                    ROUND(DATA_LENGTH / 1024 / 1024, 2) as size_mb
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY DATA_LENGTH DESC
            """
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"❌ Erreur récupération stats tables : {e}")
            return []
    
    def __enter__(self):
        """Support du context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager"""
        self.disconnect()
