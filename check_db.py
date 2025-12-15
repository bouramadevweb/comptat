#!/usr/bin/env python3
"""
Script pour vérifier le contenu de la base de données
"""
from src.infrastructure.persistence.database import DatabaseManager

def check_database():
    """Vérifie le contenu de la base de données"""

    db = DatabaseManager()

    try:
        db.connect()
        print("✅ Connexion à la base de données réussie\n")
        print("=" * 70)
        print("ÉTAT DE LA BASE DE DONNÉES")
        print("=" * 70)

        # 1. Vérifier les sociétés
        print("\n📊 SOCIÉTÉS :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM SOCIETES")
            societes = cursor.fetchall()

            if societes:
                for soc in societes:
                    print(f"  ID {soc['id']} : {soc['nom']}")
                    print(f"    SIREN: {soc['siren']}")
                    print(f"    Ville: {soc['ville']}")
                    print()
            else:
                print("  ❌ Aucune société trouvée")

        # 2. Vérifier les exercices
        print("\n📅 EXERCICES :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT e.*, s.nom as societe_nom
                FROM EXERCICES e
                LEFT JOIN SOCIETES s ON e.societe_id = s.id
                ORDER BY e.annee DESC
            """)
            exercices = cursor.fetchall()

            if exercices:
                for ex in exercices:
                    statut = "🔒 Clôturé" if ex['cloture'] else "✅ Ouvert"
                    print(f"  ID {ex['id']} : Exercice {ex['annee']} {statut}")
                    print(f"    Société: {ex['societe_nom']}")
                    print(f"    Période: {ex['date_debut']} → {ex['date_fin']}")
                    print()
            else:
                print("  ❌ Aucun exercice trouvé")

        # 3. Vérifier les journaux
        print("\n📚 JOURNAUX :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM JOURNAUX")
            journaux = cursor.fetchall()

            if journaux:
                for j in journaux:
                    print(f"  [{j['code']}] {j['libelle']} (Type: {j['type']})")
            else:
                print("  ❌ Aucun journal trouvé")

        # 4. Vérifier les comptes
        print("\n💰 PLAN COMPTABLE :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT classe, type_compte, COUNT(*) as nb_comptes
                FROM COMPTES
                GROUP BY classe, type_compte
                ORDER BY classe
            """)
            comptes = cursor.fetchall()

            if comptes:
                total = 0
                for c in comptes:
                    nb = c['nb_comptes']
                    total += nb
                    print(f"  Classe {c['classe']} ({c['type_compte']}) : {nb} comptes")
                print(f"\n  TOTAL : {total} comptes")
            else:
                print("  ❌ Aucun compte trouvé")

        # 5. Vérifier les taux de TVA
        print("\n💸 TAUX DE TVA :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM TAXES")
            taxes = cursor.fetchall()

            if taxes:
                for t in taxes:
                    print(f"  [{t['code']}] {t['nom']} : {float(t['taux'])*100}%")
            else:
                print("  ❌ Aucun taux de TVA trouvé")

        # 6. Vérifier les tiers
        print("\n👥 TIERS :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("SELECT type, COUNT(*) as nb FROM TIERS GROUP BY type")
            tiers = cursor.fetchall()

            if tiers:
                for t in tiers:
                    print(f"  {t['type']}S : {t['nb']}")
            else:
                print("  ❌ Aucun tiers trouvé")

        # 7. Vérifier les écritures
        print("\n📝 ÉCRITURES :")
        print("-" * 70)
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as nb FROM ECRITURES")
            result = cursor.fetchone()
            nb_ecritures = result['nb']

            cursor.execute("SELECT COUNT(*) as nb FROM MOUVEMENTS")
            result = cursor.fetchone()
            nb_mouvements = result['nb']

            print(f"  Écritures : {nb_ecritures}")
            print(f"  Mouvements : {nb_mouvements}")

        print("\n" + "=" * 70)
        print("RÉSUMÉ")
        print("=" * 70)

        # Diagnostic
        if not societes:
            print("\n❌ PROBLÈME : Aucune société n'existe")
            print("   → Vous devez créer une société d'abord")
            print("   → Utilisez: python -m scripts.init_societe")
        elif not exercices:
            print("\n⚠️  ATTENTION : Vous avez une société mais pas d'exercice")
            print("   → Vous devez créer un exercice comptable")
            print("   → Utilisez: python -m scripts.init_societe")
        elif not journaux:
            print("\n⚠️  ATTENTION : Vous avez une société et un exercice mais pas de journaux")
            print("   → Utilisez: python -m scripts.init_societe")
        elif not comptes:
            print("\n⚠️  ATTENTION : Vous n'avez pas de plan comptable")
            print("   → Utilisez: python -m scripts.init_societe")
        else:
            print("\n✅ Votre base de données est configurée !")
            print(f"   → {len(societes)} société(s)")
            print(f"   → {len(exercices)} exercice(s)")
            print(f"   → {len(journaux)} journaux")
            print(f"   → Plan comptable complet")

        print()

    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        db.disconnect()
        print("🔌 Connexion fermée\n")

if __name__ == "__main__":
    check_database()
