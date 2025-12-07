#!/usr/bin/env python3
"""
Script de migration vers une architecture par couches
Réorganise automatiquement les fichiers en dossiers par couche
"""
import os
import shutil
from pathlib import Path
import re


class LayeredArchitectureMigrator:
    """Migre le projet vers une architecture en couches"""

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).resolve()
        self.src_dir = self.root / "src"
        self.backup_created = False

    def create_backup(self):
        """Crée un backup du projet avant migration"""
        backup_dir = self.root.parent / f"{self.root.name}_backup"

        if backup_dir.exists():
            print(f"⚠️  Backup existant trouvé: {backup_dir}")
            response = input("Écraser? (o/n): ")
            if response.lower() != 'o':
                print("❌ Migration annulée")
                return False
            shutil.rmtree(backup_dir)

        print(f"📦 Création du backup dans {backup_dir}...")
        shutil.copytree(self.root, backup_dir, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.git', 'venv', 'env', '*.egg-info'
        ))
        print(f"✅ Backup créé: {backup_dir}")
        self.backup_created = True
        return True

    def create_directory_structure(self):
        """Crée la structure de dossiers"""
        print("\n📁 Création de la structure de dossiers...")

        directories = [
            "src",
            "src/presentation",
            "src/application",
            "src/domain",
            "src/infrastructure",
            "src/infrastructure/persistence",
            "src/infrastructure/validation",
            "src/infrastructure/configuration",
            "src/utils",
            "scripts",
            "tests",
            "tests/presentation",
            "tests/application",
            "tests/domain",
            "tests/infrastructure",
            "docs",
            "sql",
        ]

        for directory in directories:
            dir_path = self.root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory}/")

        print("✅ Structure créée")

    def create_init_files(self):
        """Crée tous les fichiers __init__.py"""
        print("\n📝 Création des fichiers __init__.py...")

        init_files = {
            "src/__init__.py": '''"""Package principal de l'application de comptabilité"""

from src.application.services import ComptabiliteService
from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.configuration.config import Config

__version__ = "2.0.0"
__all__ = ['ComptabiliteService', 'DatabaseManager', 'Config']
''',
            "src/presentation/__init__.py": '''"""Couche présentation - Interfaces utilisateur"""
''',
            "src/application/__init__.py": '''"""Couche application - Logique métier"""

from src.application.services import ComptabiliteService

__all__ = ['ComptabiliteService']
''',
            "src/domain/__init__.py": '''"""Couche domaine - Entités métier"""

from src.domain.models import *

__all__ = [
    'Societe', 'Exercice', 'Journal', 'Compte', 'Tiers',
    'Ecriture', 'Mouvement', 'Balance', 'Taxe', 'Paiement'
]
''',
            "src/infrastructure/__init__.py": '''"""Couche infrastructure - Services techniques"""
''',
            "src/infrastructure/persistence/__init__.py": '''"""Sous-couche persistance"""

from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.persistence.dao import *

__all__ = ['DatabaseManager']
''',
            "src/infrastructure/validation/__init__.py": '''"""Sous-couche validation"""

from src.infrastructure.validation.validators import *

__all__ = ['ComptabiliteValidator', 'SocieteValidator', 'TiersValidator']
''',
            "src/infrastructure/configuration/__init__.py": '''"""Sous-couche configuration"""

from src.infrastructure.configuration.config import Config
from src.infrastructure.configuration.constants import *

__all__ = ['Config']
''',
            "src/utils/__init__.py": '''"""Utilitaires"""

from src.utils.export_utils import ExportManager
from src.infrastructure.backup import BackupManager

__all__ = ['ExportManager', 'BackupManager']
''',
            "scripts/__init__.py": '''"""Scripts d'initialisation et maintenance"""
''',
            "tests/__init__.py": '''"""Tests unitaires et d'intégration"""
''',
            "tests/presentation/__init__.py": "",
            "tests/application/__init__.py": "",
            "tests/domain/__init__.py": "",
            "tests/infrastructure/__init__.py": "",
        }

        for filepath, content in init_files.items():
            full_path = self.root / filepath
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {filepath}")

        print("✅ Fichiers __init__.py créés")

    def move_files(self):
        """Déplace les fichiers dans les bons dossiers"""
        print("\n🚚 Déplacement des fichiers...")

        file_mappings = {
            # Présentation
            "gui_main.py": "src/presentation/",
            "gui_vente.py": "src/presentation/",
            "gui_achat.py": "src/presentation/",
            "gui_ecriture.py": "src/presentation/",
            "gui_rapports.py": "src/presentation/",

            # Application
            "services.py": "src/application/",

            # Domaine
            "models.py": "src/domain/",

            # Infrastructure - Persistance
            "database.py": "src/infrastructure/persistence/",
            "dao.py": "src/infrastructure/persistence/",

            # Infrastructure - Validation
            "validators.py": "src/infrastructure/validation/",

            # Infrastructure - Configuration
            "constants.py": "src/infrastructure/configuration/",
            "config.py": "src/infrastructure/configuration/",

            # Utilitaires
            "export_utils.py": "src/utils/",
            "backup_utils.py": "src/infrastructure/backup/",

            # Scripts
            "init_societe.py": "scripts/",

            # Documentation
            "AMELIORATIONS.md": "docs/",
            "ARCHITECTURE.md": "docs/",
            "REORGANISATION.md": "docs/",
            "CORRECTIONS.md": "docs/",
            "GUIDE_CREATION_SOCIETE.md": "docs/",
            "GUIDE_TVA_AUTOMATIQUE.md": "docs/",
            "INDEX.md": "docs/",
            "QUICKSTART.md": "docs/",
            "README.md": "docs/",
            "START_HERE.md": "docs/",
            "STRUCTURE.md": "docs/",

            # SQL
            "procedures_stockees.sql": "sql/",
            "optimize_database.sql": "sql/",
        }

        for source_file, dest_dir in file_mappings.items():
            source = self.root / source_file
            dest = self.root / dest_dir / source_file

            if source.exists():
                shutil.move(str(source), str(dest))
                print(f"  ✓ {source_file} → {dest_dir}")
            else:
                print(f"  ⚠ {source_file} introuvable (ignoré)")

        print("✅ Fichiers déplacés")

    def update_imports(self):
        """Met à jour tous les imports dans les fichiers"""
        print("\n🔄 Mise à jour des imports...")

        # Mapping des anciens imports vers les nouveaux
        import_mappings = {
            r'from database import': 'from src.infrastructure.persistence.database import',
            r'from dao import': 'from src.infrastructure.persistence.dao import',
            r'from models import': 'from src.domain.models import',
            r'from services import': 'from src.application.services import',
            r'from validators import': 'from src.infrastructure.validation.validators import',
            r'from constants import': 'from src.infrastructure.configuration.constants import',
            r'from config import': 'from src.infrastructure.configuration.config import',
            r'from export_utils import': 'from src.utils.export_utils import',
            r'from backup_utils import': 'from src.infrastructure.backup import',

            r'import database': 'import src.infrastructure.persistence.database as database',
            r'import dao': 'import src.infrastructure.persistence.dao as dao',
            r'import models': 'import src.domain.models as models',
            r'import services': 'import src.application.services as services',
            r'import validators': 'import src.infrastructure.validation.validators as validators',
        }

        # Fichiers à mettre à jour
        python_files = list(self.src_dir.rglob("*.py"))
        python_files.extend([
            self.root / "main.py",
            self.root / "scripts" / "init_societe.py",
        ])

        for filepath in python_files:
            if not filepath.exists() or filepath.name == "__init__.py":
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # Appliquer les remplacements
                for old_import, new_import in import_mappings.items():
                    content = re.sub(old_import, new_import, content)

                # Sauvegarder si modifié
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ {filepath.relative_to(self.root)}")

            except Exception as e:
                print(f"  ⚠ Erreur sur {filepath}: {e}")

        print("✅ Imports mis à jour")

    def update_main_py(self):
        """Met à jour le fichier main.py"""
        print("\n📝 Mise à jour de main.py...")

        main_file = self.root / "main.py"

        if not main_file.exists():
            print("  ⚠ main.py introuvable")
            return

        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Ajouter l'ajustement du PYTHONPATH au début si pas déjà présent
            if "sys.path.insert" not in content:
                header = '''import sys
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

'''
                # Trouver la première ligne après les commentaires
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line and not line.startswith('#') and not line.startswith('"""'):
                        insert_pos = i
                        break

                lines.insert(insert_pos, header)
                content = '\n'.join(lines)

            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print("  ✓ main.py mis à jour")

        except Exception as e:
            print(f"  ⚠ Erreur: {e}")

    def create_readme(self):
        """Crée un README.md mis à jour"""
        print("\n📄 Création du README.md...")

        readme_content = '''# Logiciel de Comptabilité

Application de comptabilité complète avec interface graphique Tkinter.

## 📁 Structure du projet

```
comptabilite-python/
├── src/                          # Code source
│   ├── presentation/             # Interface graphique (GUI)
│   ├── application/              # Logique métier (Services)
│   ├── domain/                   # Entités métier (Models)
│   ├── infrastructure/           # Infrastructure technique
│   │   ├── persistence/          # Base de données (DAO, Database)
│   │   ├── validation/           # Validation des données
│   │   └── configuration/        # Configuration (Constants, Config)
│   └── utils/                    # Utilitaires (Export, Backup)
├── scripts/                      # Scripts d'initialisation
├── tests/                        # Tests unitaires
├── docs/                         # Documentation
├── sql/                          # Fichiers SQL
├── main.py                       # Point d'entrée
├── requirements.txt              # Dépendances
└── .env                         # Configuration (ne pas commiter)
```

## 🚀 Installation

```bash
# 1. Cloner le projet
cd /chemin/vers/comptabilite-python

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la base de données
cp .env.example .env
# Éditer .env avec vos paramètres MySQL

# 4. Initialiser une société
python scripts/init_societe.py

# 5. Optimiser la base de données
mysql -u root -p COMPTA < sql/optimize_database.sql
```

## 🎯 Utilisation

```bash
# Lancer l'application
python main.py
```

## 📚 Documentation

Voir le dossier `docs/` :
- `ARCHITECTURE.md` - Architecture du logiciel
- `AMELIORATIONS.md` - Guide des améliorations
- `REORGANISATION.md` - Guide de réorganisation
- `QUICKSTART.md` - Démarrage rapide

## ✨ Fonctionnalités

- ✅ Gestion des écritures comptables
- ✅ Plan comptable complet
- ✅ Journaux (Vente, Achat, Banque, OD)
- ✅ Balance, Bilan, Compte de résultat
- ✅ Calcul automatique de la TVA
- ✅ Lettrage des comptes
- ✅ Clôture d'exercice
- ✅ Export Excel/CSV
- ✅ Backup automatique
- ✅ Export FEC (Fichier des Écritures Comptables)

## 🏗️ Architecture

Le logiciel suit une **architecture en couches (Layered Architecture)** :

1. **Présentation** : Interface graphique Tkinter
2. **Application** : Logique métier (ComptabiliteService)
3. **Domaine** : Entités métier pures
4. **Infrastructure** : Persistance, validation, configuration
5. **Utilitaires** : Export, backup

## 📖 Version

**Version 2.0** - Janvier 2025

## 📝 License

Propriétaire
'''

        with open(self.root / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print("  ✓ README.md créé")

    def run(self):
        """Exécute la migration complète"""
        print("="*60)
        print("🔧 MIGRATION VERS ARCHITECTURE EN COUCHES")
        print("="*60)

        # 1. Backup
        if not self.create_backup():
            return False

        # 2. Structure
        self.create_directory_structure()

        # 3. __init__.py
        self.create_init_files()

        # 4. Déplacer fichiers
        self.move_files()

        # 5. Mettre à jour imports
        self.update_imports()

        # 6. Mettre à jour main.py
        self.update_main_py()

        # 7. Créer README
        self.create_readme()

        print("\n" + "="*60)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS!")
        print("="*60)
        print(f"\n📦 Backup: {self.root.parent / f'{self.root.name}_backup'}")
        print(f"📁 Projet migré: {self.root}")
        print("\n📝 Prochaines étapes:")
        print("  1. Vérifier que tout fonctionne: python main.py")
        print("  2. Tester les fonctionnalités principales")
        print("  3. Si tout fonctionne, supprimer le backup")
        print("  4. Consulter docs/ARCHITECTURE.md pour plus d'infos")
        print("\n" + "="*60)

        return True


def main():
    """Point d'entrée du script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migre le projet vers une architecture en couches"
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Répertoire racine du projet (défaut: répertoire courant)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Ne pas créer de backup (ATTENTION: risqué!)'
    )

    args = parser.parse_args()

    migrator = LayeredArchitectureMigrator(args.root)

    if args.no_backup:
        print("⚠️  Mode sans backup activé!")
        response = input("Êtes-vous SÛR? (tapez 'OUI' pour confirmer): ")
        if response != 'OUI':
            print("❌ Migration annulée")
            return 1
        migrator.backup_created = True  # Simuler que le backup est fait

    success = migrator.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
