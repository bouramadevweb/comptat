"""
Compatibilité: BackupManager est déplacé vers src.infrastructure.backup.backup_manager.
"""
from src.infrastructure.backup.backup_manager import BackupManager

__all__ = ["BackupManager"]
