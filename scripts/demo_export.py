#!/usr/bin/env python3
"""
Script de démonstration: Export Excel
Exporte la balance et le compte de résultat en Excel
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.factories import create_db_manager, create_service
from src.utils.export_utils import ExportManager

def demo_export():
    """Démonstration de l'export Excel"""

    print("=" * 70)
    print("📊 DÉMONSTRATION: EXPORT EXCEL")
    print("=" * 70)

    # Initialisation
    print("\n🔧 Initialisation...")
    db = create_db_manager()
    service = create_service(db)
    export_manager = ExportManager(output_dir="/tmp/compta_exports")

    # Récupérer la première société
    societes = service.get_societes()
    if not societes:
        print("❌ Aucune société trouvée")
        return

    societe = societes[0]
    print(f"✅ Société: {societe.nom}")

    # Récupérer l'exercice courant
    exercice = service.get_exercice_courant(societe.id)
    if not exercice:
        print("❌ Aucun exercice courant")
        return

    print(f"✅ Exercice: {exercice.annee}")

    # === 1. EXPORT BALANCE ===
    print("\n" + "─" * 70)
    print("1️⃣  Export de la Balance en Excel")
    print("─" * 70)

    balance = service.get_balance(societe.id, exercice.id)
    print(f"📋 {len(balance)} ligne(s) dans la balance")

    success, filepath = export_manager.exporter_balance_excel(
        balance_data=balance,
        societe_nom=societe.nom,
        exercice_annee=exercice.annee
    )

    if success:
        print(f"✅ Balance exportée:")
        print(f"   📄 {filepath}")

        # Taille du fichier
        import os
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   💾 Taille: {size_kb:.1f} KB")
    else:
        print(f"❌ Erreur: {filepath}")

    # === 2. EXPORT COMPTE DE RÉSULTAT ===
    print("\n" + "─" * 70)
    print("2️⃣  Export du Compte de Résultat en Excel")
    print("─" * 70)

    resultat = service.get_compte_resultat(societe.id, exercice.id)

    print(f"📊 Charges: {resultat['total_charges']:.2f} €")
    print(f"📊 Produits: {resultat['total_produits']:.2f} €")
    print(f"📊 Résultat: {resultat['resultat']:.2f} €")

    success, filepath = export_manager.exporter_compte_resultat_excel(
        charges=resultat['charges'],
        produits=resultat['produits'],
        total_charges=resultat['total_charges'],
        total_produits=resultat['total_produits'],
        resultat=resultat['resultat'],
        societe_nom=societe.nom,
        exercice_annee=exercice.annee
    )

    if success:
        print(f"✅ Compte de résultat exporté:")
        print(f"   📄 {filepath}")

        size_kb = os.path.getsize(filepath) / 1024
        print(f"   💾 Taille: {size_kb:.1f} KB")
    else:
        print(f"❌ Erreur: {filepath}")

    # === 3. EXPORT CSV ===
    print("\n" + "─" * 70)
    print("3️⃣  Export de la Balance en CSV")
    print("─" * 70)

    success, filepath = export_manager.exporter_balance_csv(
        balance_data=balance,
        filename=f"balance_{societe.nom}_{exercice.annee}.csv"
    )

    if success:
        print(f"✅ Balance CSV exportée:")
        print(f"   📄 {filepath}")

        size_kb = os.path.getsize(filepath) / 1024
        print(f"   💾 Taille: {size_kb:.1f} KB")
    else:
        print(f"❌ Erreur: {filepath}")

    # Fermeture
    db.disconnect()

    # Résumé
    print("\n" + "=" * 70)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 70)
    print(f"\n📁 Tous les fichiers sont dans: /tmp/compta_exports/")
    print("\n💡 Pour les ouvrir:")
    print("   libreoffice /tmp/compta_exports/*.xlsx")
    print("   cat /tmp/compta_exports/*.csv")
    print()

if __name__ == "__main__":
    try:
        demo_export()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
