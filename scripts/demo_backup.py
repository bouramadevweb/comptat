#!/usr/bin/env python3
"""
Script de démonstration: Backup automatique
Crée, liste et gère les backups de la base de données
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.backup import BackupManager

def demo_backup():
    """Démonstration du système de backup"""

    print("=" * 70)
    print("📦 DÉMONSTRATION: BACKUP AUTOMATIQUE")
    print("=" * 70)

    # Initialisation
    backup_dir = "/tmp/compta_backups_demo"
    manager = BackupManager(backup_dir=backup_dir)

    print(f"\n📁 Répertoire de backup: {backup_dir}")

    # === 1. LISTER LES BACKUPS EXISTANTS ===
    print("\n" + "─" * 70)
    print("1️⃣  Liste des backups existants")
    print("─" * 70)

    backups = manager.lister_backups()

    if backups:
        print(f"📋 {len(backups)} backup(s) trouvé(s):\n")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. {backup['filename']}")
            print(f"     📅 Date: {backup['date'].strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"     💾 Taille: {backup['size_mb']:.2f} MB")
            print(f"     🗜️  Compressé: {'Oui' if backup['compressed'] else 'Non'}")
            print()
    else:
        print("ℹ️  Aucun backup existant")

    # === 2. CRÉER UN NOUVEAU BACKUP ===
    print("─" * 70)
    print("2️⃣  Création d'un nouveau backup")
    print("─" * 70)

    print("⏳ Création en cours...")

    success, filepath = manager.creer_backup(
        compress=True,
        include_procedures=True
    )

    if success:
        print(f"✅ Backup créé avec succès:")
        print(f"   📄 {filepath}")

        # Afficher la taille
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"   💾 Taille: {size_mb:.2f} MB")

        # Vérifier le contenu (premières lignes)
        import gzip
        with gzip.open(filepath, 'rt') as f:
            first_lines = [f.readline() for _ in range(3)]

        print(f"   📝 Contenu (aperçu):")
        for line in first_lines:
            print(f"      {line.strip()[:60]}...")

    else:
        print(f"❌ Erreur: {filepath}")
        return

    # === 3. LISTER À NOUVEAU ===
    print("\n" + "─" * 70)
    print("3️⃣  Liste mise à jour des backups")
    print("─" * 70)

    backups = manager.lister_backups()
    print(f"📋 {len(backups)} backup(s) maintenant\n")

    for i, backup in enumerate(backups, 1):
        age_heures = (manager._get_now() - backup['date']).total_seconds() / 3600
        print(f"  {i}. {backup['filename']}")
        print(f"     🕐 Créé il y a {age_heures:.1f}h")
        print(f"     💾 {backup['size_mb']:.2f} MB")
        print()

    # === 4. BACKUP AUTOMATIQUE AVEC ROTATION ===
    print("─" * 70)
    print("4️⃣  Backup automatique avec rotation (max 3)")
    print("─" * 70)

    print("⏳ Création de plusieurs backups pour tester la rotation...")

    # Créer 3 backups de plus
    for i in range(3):
        success, msg = manager.creer_backup_automatique(
            max_backups=3,
            compress=True
        )
        print(f"   Backup {i+1}/3: {'✅' if success else '❌'}")

    backups = manager.lister_backups()
    print(f"\n✅ Rotation effectuée: {len(backups)} backup(s) conservé(s) (max 3)")

    # === 5. STATISTIQUES ===
    print("\n" + "─" * 70)
    print("5️⃣  Statistiques des backups")
    print("─" * 70)

    backups = manager.lister_backups()

    if backups:
        total_size = sum(b['size_mb'] for b in backups)
        oldest = min(backups, key=lambda b: b['date'])
        newest = max(backups, key=lambda b: b['date'])

        print(f"📊 Nombre de backups: {len(backups)}")
        print(f"💾 Espace total: {total_size:.2f} MB")
        print(f"📅 Plus ancien: {oldest['date'].strftime('%d/%m/%Y %H:%M')}")
        print(f"📅 Plus récent: {newest['date'].strftime('%d/%m/%Y %H:%M')}")

    # Résumé
    print("\n" + "=" * 70)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 70)
    print(f"\n📁 Backups dans: {backup_dir}")
    print(f"📋 {len(backups)} backup(s) disponible(s)")
    print(f"\n💡 Pour restaurer un backup:")
    print(f"   python -c \"from src.infrastructure.backup import BackupManager;")
    print(f"              m = BackupManager('{backup_dir}');")
    print(f"              m.restaurer_backup('chemin/vers/backup.sql.gz')\"")
    print()

    # Helper method pour la démo
    def _get_now(self):
        from datetime import datetime
        return datetime.now()

    manager._get_now = lambda: _get_now(manager)

if __name__ == "__main__":
    try:
        demo_backup()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
