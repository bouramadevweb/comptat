"""Sous-couche persistance"""

from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.persistence.dao import *

__all__ = ['DatabaseManager']
