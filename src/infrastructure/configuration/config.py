"""
Configuration de la base de données
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration globale de l'application"""
    
    # Configuration Base de données
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'COMPTA')
    
    # Configuration Application
    APP_NAME = "Système de Comptabilité Générale"
    APP_VERSION = "2.0"
    
    # Chemins d'export
    EXPORT_DIR = os.getenv('EXPORT_DIR', '/tmp')

    @classmethod
    def get_db_config(cls):
        """Retourne la configuration DB sous forme de dictionnaire"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': 'utf8mb4'
        }


class Settings:
    """Settings de sécurité et authentification"""

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv(
        'JWT_SECRET_KEY',
        'votre-cle-secrete-jwt-a-changer-en-production-utiliser-secrets-token-urlsafe'
    )
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

    # Security
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_DURATION_MINUTES = int(os.getenv('ACCOUNT_LOCKOUT_DURATION_MINUTES', 30))

    # Audit
    AUDIT_LOG_RETENTION_DAYS = int(os.getenv('AUDIT_LOG_RETENTION_DAYS', 365))

    @classmethod
    def validate(cls):
        """Valide la configuration de sécurité"""
        if cls.JWT_SECRET_KEY == 'votre-cle-secrete-jwt-a-changer-en-production-utiliser-secrets-token-urlsafe':
            import warnings
            warnings.warn(
                "⚠️  ATTENTION: JWT_SECRET_KEY par défaut détectée! "
                "Changez-la en production via la variable d'environnement JWT_SECRET_KEY",
                UserWarning
            )
