"""Package principal de l'application de comptabilité"""

from src.application.services import ComptabiliteService
from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.configuration.config import Config

__version__ = "2.0.0"
__all__ = ['ComptabiliteService', 'DatabaseManager', 'Config']
