#!/bin/bash
# ==========================================
# Script de correction automatique SQL
# Corrige toutes les erreurs PascalCase → snake_case
# ==========================================

echo "🔧 Correction des erreurs SQL en cours..."
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Demander le mot de passe MySQL une seule fois
read -sp "Entrez le mot de passe MySQL root: " MYSQL_PASSWORD
echo ""
echo ""

# Fonction pour exécuter un script SQL
execute_sql() {
    local file=$1
    local description=$2

    echo -e "${YELLOW}➤${NC} $description..."

    if mysql -u root -p"$MYSQL_PASSWORD" Comptabilite < "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description - OK"
        return 0
    else
        echo -e "${RED}✗${NC} $description - ERREUR"
        echo "   Fichier: $file"
        echo "   Détails de l'erreur:"
        mysql -u root -p"$MYSQL_PASSWORD" Comptabilite < "$file" 2>&1 | tail -5
        return 1
    fi
}

echo "================================================"
echo "  CORRECTION DES PROCÉDURES STOCKÉES"
echo "================================================"
echo ""

# Exécuter les corrections
ERRORS=0

execute_sql "sql/04_fix_all_procedures.sql" "Correction procédures (IDs)" || ((ERRORS++))

echo ""
echo "================================================"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Toutes les corrections appliquées avec succès!${NC}"
    echo ""
    echo "Vous pouvez maintenant:"
    echo "  1. Relancer l'application: python src/main.py"
    echo "  2. Tester les procédures:"
    echo "     mysql -u root -p Comptabilite"
    echo "     CALL Tester_Comptabilite_Avancee(1, 1);"
else
    echo -e "${RED}❌ $ERRORS erreur(s) détectée(s)${NC}"
    echo ""
    echo "Vérifiez:"
    echo "  - Que MySQL est démarré"
    echo "  - Que le mot de passe est correct"
    echo "  - Que la base 'Comptabilite' existe"
    echo ""
    echo "Pour créer la base si nécessaire:"
    echo "  mysql -u root -p < sql/01_database_schema.sql"
fi

echo ""
