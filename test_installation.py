"""
Script de test pour vérifier l'installation et la configuration
"""
import sys
from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.persistence.dao import (
    SocieteDAO,
    ExerciceDAO,
    JournalDAO,
    CompteDAO,
    TiersDAO,
    EcritureDAO,
    BalanceDAO,
    ReportingDAO,
    ProcedureDAO,
)
from src.application.services import ComptabiliteService
from src.infrastructure.configuration.config import Config

def test_database_connection():
    """Test de connexion à la base de données"""
    print("🔍 Test de connexion à la base de données...")
    try:
        db = DatabaseManager()
        db.connect()
        print("✅ Connexion à la base de données réussie")
        
        # Test d'une requête simple
        result = db.execute_query("SELECT DATABASE()")
        print(f"✅ Base de données active : {result[0]['DATABASE()']}")
        
        db.disconnect()
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False


def test_tables_existence():
    """Vérifie que toutes les tables existent"""
    print("\n🔍 Vérification des tables...")
    tables_required = [
        'SOCIETES', 'EXERCICES', 'JOURNAUX', 'COMPTES', 'TIERS',
        'TAXES', 'ECRITURES', 'MOUVEMENTS', 'PAIEMENTS',
        'LETTRAGES', 'LETTRAGE_LIGNES', 'BALANCE'
    ]
    
    try:
        db = DatabaseManager()
        db.connect()
        
        query = "SHOW TABLES"
        result = db.execute_query(query)
        tables_found = [list(row.values())[0] for row in result]
        
        missing_tables = []
        for table in tables_required:
            if table not in tables_found:
                missing_tables.append(table)
                print(f"❌ Table manquante : {table}")
            else:
                print(f"✅ Table {table} OK")
        
        db.disconnect()
        
        if missing_tables:
            print(f"\n❌ {len(missing_tables)} table(s) manquante(s)")
            print("👉 Exécutez d'abord le script SQL de création de la base")
            return False
        
        print(f"\n✅ Toutes les tables sont présentes ({len(tables_required)})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def test_stored_procedures():
    """Vérifie que les procédures stockées existent"""
    print("\n🔍 Vérification des procédures stockées...")
    procedures_required = [
        'Calculer_Balance',
        'Cloturer_Exercice',
        'Exporter_FEC_Exercice',
        'Tester_Comptabilite_Avancee',
        'AutoAudit_Cloture'
    ]
    
    try:
        db = DatabaseManager()
        db.connect()
        
        query = """
            SELECT ROUTINE_NAME 
            FROM information_schema.ROUTINES 
            WHERE ROUTINE_SCHEMA = %s 
            AND ROUTINE_TYPE = 'PROCEDURE'
        """
        result = db.execute_query(query, (Config.DB_NAME,))
        procedures_found = [row['ROUTINE_NAME'] for row in result]
        
        missing_procedures = []
        for proc in procedures_required:
            if proc not in procedures_found:
                missing_procedures.append(proc)
                print(f"❌ Procédure manquante : {proc}")
            else:
                print(f"✅ Procédure {proc} OK")
        
        db.disconnect()
        
        if missing_procedures:
            print(f"\n⚠️ {len(missing_procedures)} procédure(s) manquante(s)")
            print("👉 Vérifiez le script SQL")
            return False
        
        print(f"\n✅ Toutes les procédures sont présentes ({len(procedures_required)})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def test_sample_data():
    """Vérifie la présence de données d'exemple"""
    print("\n🔍 Vérification des données d'exemple...")
    
    try:
        db = DatabaseManager()
        db.connect()
        service = ComptabiliteService(
            db=db,
            societe_repo=SocieteDAO(db),
            exercice_repo=ExerciceDAO(db),
            journal_repo=JournalDAO(db),
            compte_repo=CompteDAO(db),
            tiers_repo=TiersDAO(db),
            ecriture_repo=EcritureDAO(db),
            balance_repo=BalanceDAO(db),
            reporting_repo=ReportingDAO(db),
            procedure_repo=ProcedureDAO(db),
        )
        
        # Vérifier sociétés
        societes = service.get_societes()
        if not societes:
            print("⚠️ Aucune société trouvée")
            print("👉 Importez les données d'exemple du script SQL")
            return False
        
        print(f"✅ {len(societes)} société(s) trouvée(s)")
        print(f"   📍 {societes[0].nom}")
        
        # Vérifier exercices
        exercices = service.get_exercices(societes[0].id)
        if not exercices:
            print("⚠️ Aucun exercice trouvé")
            return False
        
        print(f"✅ {len(exercices)} exercice(s) trouvé(s)")
        print(f"   📅 Exercice {exercices[0].annee}")
        
        # Vérifier comptes
        comptes = service.get_comptes(societes[0].id)
        print(f"✅ {len(comptes)} compte(s) dans le plan comptable")
        
        # Vérifier écritures
        if exercices:
            ecritures = service.get_ecritures(exercices[0].id)
            print(f"✅ {len(ecritures)} écriture(s) comptable(s)")
        
        db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def test_balance_calculation():
    """Test du calcul de la balance"""
    print("\n🔍 Test du calcul de la balance...")
    
    try:
        db = DatabaseManager()
        db.connect()
        service = ComptabiliteService(
            db=db,
            societe_repo=SocieteDAO(db),
            exercice_repo=ExerciceDAO(db),
            journal_repo=JournalDAO(db),
            compte_repo=CompteDAO(db),
            tiers_repo=TiersDAO(db),
            ecriture_repo=EcritureDAO(db),
            balance_repo=BalanceDAO(db),
            reporting_repo=ReportingDAO(db),
            procedure_repo=ProcedureDAO(db),
        )
        
        societes = service.get_societes()
        if not societes:
            print("⚠️ Aucune société disponible pour le test")
            return False
        
        societe = societes[0]
        exercices = service.get_exercices(societe.id)
        
        if not exercices:
            print("⚠️ Aucun exercice disponible pour le test")
            return False
        
        exercice = exercices[0]
        
        # Calculer la balance
        print(f"   Calcul de la balance pour {societe.nom} - {exercice.annee}...")
        service.calculer_balance(societe.id, exercice.id)
        
        # Récupérer la balance
        balance = service.get_balance(societe.id, exercice.id)
        
        if balance:
            print(f"✅ Balance calculée : {len(balance)} compte(s)")
            
            # Vérifier l'équilibre
            total_debit = sum(b.total_debit for b in balance)
            total_credit = sum(b.total_credit for b in balance)
            
            print(f"   💰 Total Débit  : {total_debit:,.2f} €")
            print(f"   💰 Total Crédit : {total_credit:,.2f} €")
            
            if abs(total_debit - total_credit) < 0.01:
                print("✅ Balance équilibrée !")
            else:
                print(f"⚠️ Balance déséquilibrée (écart: {total_debit - total_credit:.2f} €)")
        else:
            print("⚠️ Aucune donnée dans la balance")
        
        db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("   SYSTÈME DE COMPTABILITÉ GÉNÉRALE - TESTS")
    print("=" * 60)
    
    results = []
    
    # Test 1 : Connexion
    results.append(("Connexion base de données", test_database_connection()))
    
    # Test 2 : Tables
    results.append(("Existence des tables", test_tables_existence()))
    
    # Test 3 : Procédures stockées
    results.append(("Procédures stockées", test_stored_procedures()))
    
    # Test 4 : Données d'exemple
    results.append(("Données d'exemple", test_sample_data()))
    
    # Test 5 : Calcul balance
    results.append(("Calcul de la balance", test_balance_calculation()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("   RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"   RÉSULTAT : {success_count}/{total_count} tests réussis")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n🎉 Tous les tests sont passés ! L'application est prête.")
        print("👉 Lancez l'application avec : python gui_main.py")
        return 0
    else:
        print("\n⚠️ Certains tests ont échoué.")
        print("👉 Consultez les messages ci-dessus pour corriger les problèmes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
