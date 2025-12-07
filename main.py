#!/usr/bin/env python3
"""
import sys
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


Point d'entrée principal de l'application de comptabilité
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('compta.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    missing = []
    
    try:
        import mysql.connector
    except ImportError:
        missing.append("mysql-connector-python")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing.append("python-dotenv")
    
    return missing


def check_config():
    """Vérifie que la configuration existe"""
    if not os.path.exists('.env'):
        return False, "Fichier .env manquant"
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DB_HOST', 'DB_USER', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        return False, f"Variables manquantes dans .env : {', '.join(missing_vars)}"
    
    return True, "Configuration OK"


def show_error_dialog(title, message):
    """Affiche une boîte de dialogue d'erreur"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()


def main():
    """Fonction principale"""
    logger.info("=" * 60)
    logger.info("DÉMARRAGE DE L'APPLICATION DE COMPTABILITÉ")
    logger.info("=" * 60)
    
    # Vérification des dépendances
    logger.info("🔍 Vérification des dépendances...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        error_msg = (
            f"❌ Dépendances manquantes :\n\n"
            f"{chr(10).join('  - ' + dep for dep in missing_deps)}\n\n"
            f"Installation :\n"
            f"  pip install -r requirements.txt"
        )
        logger.error(error_msg)
        show_error_dialog("Dépendances manquantes", error_msg)
        return 1
    
    logger.info("✅ Toutes les dépendances sont installées")
    
    # Vérification de la configuration
    logger.info("🔍 Vérification de la configuration...")
    config_ok, config_msg = check_config()
    
    if not config_ok:
        error_msg = (
            f"❌ {config_msg}\n\n"
            f"Solution :\n"
            f"1. Copiez .env.example vers .env\n"
            f"2. Éditez .env avec vos paramètres MySQL"
        )
        logger.error(error_msg)
        show_error_dialog("Configuration manquante", error_msg)
        return 1
    
    logger.info(f"✅ {config_msg}")
    
    # Vérification de la connexion à la base
    logger.info("🔍 Test de connexion à la base de données...")
    
    try:
        from src.infrastructure.persistence.database import DatabaseManager
        
        db = DatabaseManager()
        db.connect()
        
        # Test simple
        result = db.execute_query("SELECT DATABASE() as db, VERSION() as version")
        if result:
            logger.info(f"✅ Connecté à : {result[0]['db']}")
            logger.info(f"✅ Version MySQL : {result[0]['version']}")
        
        db.disconnect()
        
    except Exception as e:
        error_msg = (
            f"❌ Impossible de se connecter à la base de données\n\n"
            f"Erreur : {str(e)}\n\n"
            f"Vérifications :\n"
            f"1. MySQL/MariaDB est démarré ?\n"
            f"2. Les paramètres dans .env sont corrects ?\n"
            f"3. La base COMPTA existe ?\n"
            f"   → mysql -u root -p < schema_comptabilite.sql"
        )
        logger.error(error_msg)
        show_error_dialog("Erreur de connexion", error_msg)
        return 1
    
    # Lancement de l'application
    logger.info("🚀 Lancement de l'interface graphique...")

    try:
        # Utiliser ttkbootstrap pour une UI moderne
        try:
            import ttkbootstrap as ttkb
            root = ttkb.Window(themename="flatly")  # Thème moderne
            logger.info("✅ Interface moderne (ttkbootstrap) activée")
        except ImportError:
            # Fallback sur Tkinter standard si ttkbootstrap n'est pas installé
            root = tk.Tk()
            logger.warning("⚠️ ttkbootstrap non disponible, interface standard")

        from src.presentation.gui_main import ComptaApp

        app = ComptaApp(root)

        logger.info("✅ Application démarrée avec succès")
        logger.info("=" * 60)

        root.mainloop()

        logger.info("👋 Application fermée")
        return 0
        
    except Exception as e:
        error_msg = f"❌ Erreur lors du démarrage de l'application :\n\n{str(e)}"
        logger.error(error_msg, exc_info=True)
        show_error_dialog("Erreur fatale", error_msg)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Application interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"💥 Erreur fatale : {e}", exc_info=True)
        sys.exit(1)
