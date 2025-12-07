"""
Gestionnaire de sauvegardes de la base de données (infrastructure).
"""
import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
import logging
from src.infrastructure.configuration.config import Config
from src.domain.repositories import DatabaseGateway

logger = logging.getLogger(__name__)


class BackupManager:
    """Gestionnaire de sauvegardes de la base de données"""

    def __init__(self, backup_dir: str = "/tmp/backups", db: Optional[DatabaseGateway] = None):
        """
        Initialise le gestionnaire de backups
        Args:
            backup_dir: Répertoire où stocker les backups
            db: passer un gateway base de données pour éviter d'instancier en dur
        """
        self.backup_dir = backup_dir
        self.config = Config.get_db_config()
        self.db = db
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"📁 Répertoire de backup: {backup_dir}")

    def creer_backup(
        self,
        compress: bool = True,
        include_procedures: bool = True
    ) -> Tuple[bool, str]:
        """
        Crée un backup complet de la base de données
        Args:
            compress: Si True, compresse le backup avec gzip
            include_procedures: Si True, inclut les procédures stockées
        Returns:
            (succès, chemin_fichier_ou_message_erreur)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            db_name = self.config['database']
            filename = f"backup_{db_name}_{timestamp}.sql"

            if compress:
                filename += ".gz"

            filepath = os.path.join(self.backup_dir, filename)

            # Construire la commande mysqldump
            cmd = [
                'mysqldump',
                '-h', self.config['host'],
                '-u', self.config['user'],
                '--databases', db_name,
                '--single-transaction',
                '--quick',
                '--lock-tables=false',
            ]

            if include_procedures:
                cmd.extend(['--routines', '--triggers'])

            # Ajouter le mot de passe si présent
            if self.config.get('password'):
                cmd.insert(6, f"--password={self.config['password']}")

            logger.info(f"🔄 Création du backup de {db_name}...")

            if compress:
                with gzip.open(filepath, 'wb') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    f.write(process.stdout.read())

                    stderr = process.stderr.read().decode()
                    if stderr and 'Warning' not in stderr:
                        raise Exception(stderr)
            else:
                with open(filepath, 'w') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE
                    )
                    process.wait()

                    stderr = process.stderr.read().decode()
                    if stderr and 'Warning' not in stderr:
                        raise Exception(stderr)

            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                return False, "❌ Le fichier de backup est vide ou n'existe pas"

            size_mb = os.path.getsize(filepath) / (1024 * 1024)

            logger.info(f"✅ Backup créé: {filepath} ({size_mb:.2f} MB)")
            return True, filepath

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erreur mysqldump: {e}")
            return False, f"❌ Erreur mysqldump: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Erreur création backup: {e}", exc_info=True)
            return False, f"❌ Erreur: {str(e)}"

    def restaurer_backup(self, backup_file: str) -> Tuple[bool, str]:
        """
        Restaure une base de données depuis un backup
        Args:
            backup_file: Chemin vers le fichier de backup
        Returns:
            (succès, message)
        """
        try:
            if not os.path.exists(backup_file):
                return False, f"❌ Fichier de backup introuvable: {backup_file}"

            logger.info(f"🔄 Restauration du backup: {backup_file}")

            cmd = [
                'mysql',
                '-h', self.config['host'],
                '-u', self.config['user'],
            ]

            if self.config.get('password'):
                cmd.extend([f"--password={self.config['password']}"])

            is_compressed = backup_file.endswith('.gz')

            if is_compressed:
                with gzip.open(backup_file, 'rb') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate(input=f.read())

                    if process.returncode != 0:
                        raise Exception(stderr.decode())
            else:
                with open(backup_file, 'r') as f:
                    process = subprocess.Popen(
                        cmd,
                        stdin=f,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate()

                    if process.returncode != 0:
                        raise Exception(stderr.decode())

            logger.info("✅ Restauration terminée")
            return True, "✅ Restauration effectuée avec succès"

        except Exception as e:
            logger.error(f"❌ Erreur restauration: {e}", exc_info=True)
            return False, f"❌ Erreur restauration: {str(e)}"

    def lister_backups(self) -> List[dict]:
        """
        Liste les backups disponibles dans le répertoire
        Returns:
            Liste de dictionnaires avec 'filename', 'filepath', 'size_mb', 'date'
        """
        backups = []
        for filename in sorted(os.listdir(self.backup_dir), reverse=True):
            if not (filename.startswith('backup_') and filename.endswith(('.sql', '.sql.gz'))):
                continue
            filepath = os.path.join(self.backup_dir, filename)
            stats = os.stat(filepath)
            backups.append({
                'filename': filename,
                'filepath': filepath,
                'size_mb': stats.st_size / (1024 * 1024),
                'date': datetime.fromtimestamp(stats.st_mtime)
            })
        return backups

    def nettoyer_anciens_backups(self, conserver: int = 5) -> Tuple[bool, str]:
        """
        Supprime les anciens backups en ne conservant que les N plus récents
        Args:
            conserver: nombre de backups à conserver
        Returns:
            (succès, message)
        """
        try:
            backups = self.lister_backups()
            if len(backups) <= conserver:
                return True, "ℹ️ Aucun ancien backup à supprimer"

            a_supprimer = backups[conserver:]
            for backup in a_supprimer:
                os.remove(backup['filepath'])
                logger.info(f"🗑️  Ancien backup supprimé: {backup['filename']}")

            return True, f"✅ Nettoyage terminé ({len(a_supprimer)} supprimé(s))"
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage backups: {e}")
            return False, f"❌ Erreur nettoyage: {str(e)}"

    def planifier_backup_quotidien(
        self,
        heure: int = 2,
        conserver: int = 5,
        compress: bool = True
    ) -> Tuple[bool, str]:
        """
        Planifie un backup quotidien (placeholder: à implémenter avec cron/systemd)
        """
        # Ici, on ne configure pas réellement le cron pour éviter toute action système.
        # On retourne un message indiquant la commande cron à ajouter.
        cron_line = f"0 {heure} * * * python -c \"from src.infrastructure.backup.backup_manager import BackupManager; BackupManager('{self.backup_dir}').creer_backup(compress={compress})\""
        message = (
            "ℹ️ Planification non appliquée automatiquement.\n"
            "Ajoutez la ligne suivante à votre crontab:\n"
            f"{cron_line}\n"
            f"Les {conserver} derniers backups seront conservés."
        )
        return True, message

    def rotation_backup(
        self,
        compress: bool = True,
        max_backups: int = 5
    ) -> Tuple[bool, str]:
        """
        Crée un backup et nettoie les anciens
        """
        # Créer le backup
        success, result = self.creer_backup(compress=compress)

        if not success:
            return False, result

        # Nettoyer les anciens backups si nécessaire
        backups = self.lister_backups()
        if len(backups) > max_backups:
            backups_a_supprimer = backups[max_backups:]
            for backup in backups_a_supprimer:
                try:
                    os.remove(backup['filepath'])
                    logger.info(f"🗑️  Ancien backup supprimé: {backup['filename']}")
                except Exception as e:
                    logger.warning(f"⚠️  Impossible de supprimer: {e}")

        return True, f"✅ Backup créé et anciens backups nettoyés ({len(backups)} conservés)"

    def exporter_donnees_json(
        self,
        societe_code: str,
        exercice_annee: int
    ) -> Tuple[bool, str]:
        """
        Exporte les données d'un exercice en JSON (pour archivage)
        Args:
            societe_code: Code de la société
            exercice_annee: Année de l'exercice
        Returns:
            (succès, chemin_fichier_ou_message)
        """
        try:
            import json

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"export_{societe_code}_{exercice_annee}_{timestamp}.json"
            filepath = os.path.join(self.backup_dir, filename)
            if not self.db:
                raise ValueError("Aucune connexion base fournie à BackupManager (paramètre db requis)")

            data = {}

            # Ecritures
            query = """
                SELECT e.*, j.code as journal_code
                FROM ECRITURES e
                JOIN JOURNAUX j ON j.id = e.journal_id
                WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = %s)
                AND e.exercice_id IN (
                    SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = %s) AND annee = %s
                )
            """
            ecritures = self.db.execute_query(query, (societe_code, societe_code, exercice_annee))

            # Mouvements
            query = """
                SELECT m.*, c.compte as compte_numero
                FROM MOUVEMENTS m
                JOIN COMPTES c ON c.id = m.compte_id
                JOIN ECRITURES e ON e.id = m.ecriture_id
                WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = %s)
                AND e.exercice_id IN (
                    SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = %s) AND annee = %s
                )
            """
            mouvements = self.db.execute_query(query, (societe_code, societe_code, exercice_annee))

            data['exercice'] = {'societe': societe_code, 'annee': exercice_annee}
            data['ecritures'] = ecritures
            data['mouvements'] = mouvements
            data['date_export'] = datetime.now().isoformat()

            def convert_decimal(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return float(obj) if isinstance(obj, (float, int)) else obj

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=convert_decimal, ensure_ascii=False)

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            logger.info(f"✅ Export JSON créé: {filepath} ({size_mb:.2f} MB)")
            return True, filepath

        except Exception as e:
            logger.error(f"❌ Erreur export JSON: {e}", exc_info=True)
            return False, f"❌ Erreur: {str(e)}"


def tester_mysqldump_disponible() -> bool:
    """
    Vérifie que mysqldump est disponible sur le système
    """
    try:
        result = subprocess.run(['mysqldump', '--version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def supprimer_backups_anciens(backup_dir: str, jours: int = 30) -> Tuple[bool, str]:
    """
    Supprime les backups plus vieux que X jours
    """
    try:
        cutoff = datetime.now() - timedelta(days=jours)
        supprimes = 0
        for filename in os.listdir(backup_dir):
            if not filename.startswith('backup_'):
                continue
            filepath = os.path.join(backup_dir, filename)
            if datetime.fromtimestamp(os.path.getmtime(filepath)) < cutoff:
                os.remove(filepath)
                supprimes += 1
        return True, f"✅ {supprimes} backup(s) supprimé(s) de plus de {jours} jours"
    except Exception as e:
        logger.error(f"❌ Erreur suppression anciens backups: {e}")
        return False, f"❌ Erreur: {str(e)}"


def restaurer_backup_le_plus_recent(backup_dir: str) -> Tuple[bool, str]:
    """
    Restaure le backup le plus récent trouvé dans backup_dir
    """
    try:
        backups = [f for f in os.listdir(backup_dir) if f.startswith('backup_')]
        if not backups:
            return False, "❌ Aucun backup trouvé"
        latest = max(backups, key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)))
        manager = BackupManager(backup_dir=backup_dir)
        return manager.restaurer_backup(os.path.join(backup_dir, latest))
    except Exception as e:
        logger.error(f"❌ Erreur restauration dernier backup: {e}")
        return False, f"❌ Erreur: {str(e)}"
