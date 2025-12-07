#!/usr/bin/env python3
"""
Script de démonstration: Lettrage des comptes
Montre comment lettrer automatiquement et manuellement
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.factories import create_db_manager, create_service

def demo_lettrage():
    """Démonstration du lettrage des comptes"""

    print("=" * 70)
    print("🔗 DÉMONSTRATION: LETTRAGE DES COMPTES")
    print("=" * 70)

    # Initialisation
    print("\n🔧 Initialisation...")
    db = create_db_manager()
    service = create_service(db)

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

    # Comptes à tester
    comptes_test = [
        ("411000", "Clients"),
        ("401000", "Fournisseurs"),
    ]

    for compte_numero, compte_nom in comptes_test:
        print("\n" + "─" * 70)
        print(f"📌 COMPTE: {compte_nom} ({compte_numero})")
        print("─" * 70)

        # === 1. MOUVEMENTS NON LETTRÉS ===
        print("\n1️⃣  Mouvements non lettrés")

        mouvements = service.get_mouvements_a_lettrer(
            societe_id=societe.id,
            exercice_id=exercice.id,
            compte_numero=compte_numero
        )

        if mouvements:
            print(f"📋 {len(mouvements)} mouvement(s) à lettrer:\n")

            # Afficher les 5 premiers
            for mvt in mouvements[:5]:
                solde_str = f"{mvt['solde']:.2f} €"
                sens = "Débit" if mvt['solde'] > 0 else "Crédit"

                print(f"  • ID {mvt['mouvement_id']}")
                print(f"    📅 {mvt['date'].strftime('%d/%m/%Y')}")
                print(f"    📄 {mvt['ecriture_numero']} - {mvt['reference']}")
                print(f"    💰 {solde_str} ({sens})")
                if mvt.get('tiers_nom'):
                    print(f"    👤 {mvt['tiers_nom']}")
                print()

            if len(mouvements) > 5:
                print(f"  ... et {len(mouvements) - 5} autre(s)\n")

            # === 2. LETTRAGE AUTOMATIQUE ===
            print("2️⃣  Tentative de lettrage automatique")

            nb_lettrages, message = service.lettrage_automatique(
                societe_id=societe.id,
                exercice_id=exercice.id,
                compte_numero=compte_numero
            )

            print(f"   {message}")

            if nb_lettrages > 0:
                print(f"   ✅ {nb_lettrages} paire(s) lettrée(s) automatiquement")

                # === 3. MOUVEMENTS LETTRÉS ===
                print("\n3️⃣  Mouvements lettrés")

                lettres = service.get_mouvements_lettres(
                    societe_id=societe.id,
                    exercice_id=exercice.id,
                    compte_numero=compte_numero
                )

                if lettres:
                    print(f"   📌 {len(lettres)} groupe(s) de lettrage:\n")

                    for code, mvts in list(lettres.items())[:3]:  # 3 premiers
                        total_debit = sum(m['debit'] for m in mvts)
                        total_credit = sum(m['credit'] for m in mvts)
                        equilibre = abs(total_debit - total_credit) < 0.01

                        print(f"   Code: {code}")
                        print(f"   Mouvements: {len(mvts)}")
                        print(f"   Débit: {total_debit:.2f} €")
                        print(f"   Crédit: {total_credit:.2f} €")
                        print(f"   Équilibre: {'✅' if equilibre else '❌'}")
                        print()

                # === 4. MOUVEMENTS RESTANTS ===
                print("4️⃣  Mouvements restants non lettrés")

                mouvements_restants = service.get_mouvements_a_lettrer(
                    societe_id=societe.id,
                    exercice_id=exercice.id,
                    compte_numero=compte_numero
                )

                print(f"   📋 {len(mouvements_restants)} mouvement(s) non lettrés")

                if mouvements_restants:
                    # Analyse des soldes
                    soldes_debiteurs = [m for m in mouvements_restants if m['solde'] > 0]
                    soldes_crediteurs = [m for m in mouvements_restants if m['solde'] < 0]

                    print(f"      • Débiteurs: {len(soldes_debiteurs)}")
                    print(f"      • Créditeurs: {len(soldes_crediteurs)}")

                    total_debiteur = sum(m['solde'] for m in soldes_debiteurs)
                    total_crediteur = abs(sum(m['solde'] for m in soldes_crediteurs))

                    print(f"\n   💰 Total débiteur: {total_debiteur:.2f} €")
                    print(f"   💰 Total créditeur: {total_crediteur:.2f} €")

            else:
                print(f"   ℹ️  Aucun lettrage automatique possible")
                print(f"       (pas de paires qui s'équilibrent)")

        else:
            print(f"ℹ️  Aucun mouvement non lettré")

    # === 5. STATISTIQUES GLOBALES ===
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES GLOBALES DE LETTRAGE")
    print("=" * 70)

    total_mouvements_non_lettres = 0
    total_groupes_lettrage = 0

    for compte_numero, compte_nom in comptes_test:
        mouvements = service.get_mouvements_a_lettrer(
            societe_id=societe.id,
            exercice_id=exercice.id,
            compte_numero=compte_numero
        )

        lettres = service.get_mouvements_lettres(
            societe_id=societe.id,
            exercice_id=exercice.id,
            compte_numero=compte_numero
        )

        total_mouvements_non_lettres += len(mouvements)
        total_groupes_lettrage += len(lettres)

        print(f"\n{compte_nom} ({compte_numero}):")
        print(f"  • Non lettrés: {len(mouvements)}")
        print(f"  • Groupes lettrés: {len(lettres)}")

    print(f"\n📊 TOTAL:")
    print(f"  • Mouvements non lettrés: {total_mouvements_non_lettres}")
    print(f"  • Groupes de lettrage: {total_groupes_lettrage}")

    # Fermeture
    db.disconnect()

    # Résumé
    print("\n" + "=" * 70)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 70)
    print(f"\n💡 Commandes utiles:")
    print(f"\n   # Voir mouvements non lettrés")
    print(f"   service.get_mouvements_a_lettrer(1, 1, '411000')")
    print(f"\n   # Lettrage automatique")
    print(f"   service.lettrage_automatique(1, 1, '411000')")
    print(f"\n   # Voir mouvements lettrés")
    print(f"   service.get_mouvements_lettres(1, 1, '411000')")
    print(f"\n   # Délettrer un groupe")
    print(f"   service.delettrer_mouvements('AA')")
    print()

if __name__ == "__main__":
    try:
        demo_lettrage()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
