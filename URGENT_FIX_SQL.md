# 🚨 CORRECTION URGENTE - Erreurs SQL

**Problème**: `Unknown column 'e.SocieteCode' in 'WHERE'`

**Cause**: Les procédures stockées utilisent encore l'ancien schéma (PascalCase avec codes) alors que la base de données a été migrée vers snake_case avec IDs.

---

## ✅ Solution Rapide (2 minutes)

### Option 1: Script Automatique (RECOMMANDÉ)

```bash
./fix_sql_errors.sh
```

**C'est tout !** Le script applique automatiquement toutes les corrections.

### Option 2: Correction Manuelle

```bash
mysql -u root -p Comptabilite < sql/04_fix_all_procedures.sql
```

---

## 🔍 Qu'est-ce qui a été corrigé ?

### 3 Procédures Stockées Mises à Jour

#### 1. `Tester_Comptabilite_Avancee`
**Avant**:
```sql
CREATE PROCEDURE Tester_Comptabilite_Avancee(
    IN p_societe_code VARCHAR(10),  -- ❌ Attendait un code
    IN p_exercice_annee INT         -- ❌ Attendait une année
)
WHERE e.SocieteCode = p_societe_code  -- ❌ PascalCase
```

**Après**:
```sql
CREATE PROCEDURE Tester_Comptabilite_Avancee(
    IN p_societe_id INT,      -- ✅ Accepte un ID
    IN p_exercice_id INT      -- ✅ Accepte un ID
)
WHERE e.societe_id = p_societe_id  -- ✅ snake_case
```

#### 2. `Cloturer_Exercice`
- ✅ Utilise maintenant `societe_id` et `exercice_id`
- ✅ Toutes les jointures en snake_case
- ✅ Compatible avec le nouveau schéma

#### 3. `Exporter_FEC`
- ✅ Utilise `societe_id` et `exercice_id`
- ✅ Jointures corrigées
- ✅ Format FEC conforme

---

## 📊 Tableau de Correspondance

| Ancien (Code) | Nouveau (ID) | Notes |
|--------------|--------------|-------|
| `p_societe_code VARCHAR(10)` | `p_societe_id INT` | Utilise l'ID au lieu du code |
| `p_exercice_annee INT` | `p_exercice_id INT` | ID de l'exercice |
| `e.SocieteCode` | `e.societe_id` | Colonne en snake_case |
| `e.ExerciceId` | `e.exercice_id` | Colonne en snake_case |
| `e.JournalId` | `e.journal_id` | Colonne en snake_case |
| `m.EcritureId` | `m.ecriture_id` | Colonne en snake_case |

---

## ✅ Vérification

### Test 1: Vérifier les procédures

```sql
-- Se connecter à MySQL
mysql -u root -p Comptabilite

-- Lister les procédures
SHOW PROCEDURE STATUS WHERE Db = 'Comptabilite';

-- Devrait afficher:
-- - Tester_Comptabilite_Avancee
-- - Cloturer_Exercice
-- - Exporter_FEC
```

### Test 2: Tester une procédure

```sql
-- Appeler avec des IDs (pas des codes!)
CALL Tester_Comptabilite_Avancee(1, 1);

-- Résultat attendu:
+-----------------------------------+----------------+-------------+----------+
| test                              | tests_reussis  | tests_total | resultat |
+-----------------------------------+----------------+-------------+----------+
| Tests de cohérence comptable      | 5              | 5           | OK       |
+-----------------------------------+----------------+-------------+----------+
```

### Test 3: Relancer l'application

```bash
# L'erreur devrait disparaître
python src/main.py
```

**Vérifier les logs**: Plus d'erreur "Unknown column"

---

## 🔧 Si Ça Ne Fonctionne Toujours Pas

### Erreur: "Procedure doesn't exist"

```bash
# Vérifier que la base de données est correcte
mysql -u root -p -e "USE Comptabilite; SHOW TABLES;"

# Si tables manquantes, recréer:
mysql -u root -p < sql/01_database_schema.sql
mysql -u root -p < sql/02_authentication_authorization.sql
mysql -u root -p < sql/04_fix_all_procedures.sql
```

### Erreur: "Access denied"

```bash
# Vérifier vos identifiants
mysql -u root -p

# Si erreur, utiliser sudo
sudo mysql

# Ou créer un utilisateur avec droits
sudo mysql
CREATE USER 'compta'@'localhost' IDENTIFIED BY 'votre_password';
GRANT ALL PRIVILEGES ON Comptabilite.* TO 'compta'@'localhost';
FLUSH PRIVILEGES;
```

### Erreur persiste

```bash
# Supprimer et recréer TOUTES les procédures
mysql -u root -p Comptabilite << EOF
DROP PROCEDURE IF EXISTS Tester_Comptabilite_Avancee;
DROP PROCEDURE IF EXISTS Cloturer_Exercice;
DROP PROCEDURE IF EXISTS Exporter_FEC;
EOF

# Puis relancer
mysql -u root -p Comptabilite < sql/04_fix_all_procedures.sql
```

---

## 📝 Changements dans le Code Python

**Aucun changement requis !** ✅

Le code Python appelle déjà les procédures avec les bons paramètres:

```python
# src/infrastructure/persistence/dao.py:522
def tester_comptabilite(self, societe_id: int, exercice_id: int):
    return self.db.call_procedure('Tester_Comptabilite_Avancee', (societe_id, exercice_id))
```

Les procédures acceptent maintenant ces paramètres.

---

## 🎯 Résumé

| Action | Statut |
|--------|--------|
| Procédures corrigées | ✅ Fait |
| Code Python | ✅ Compatible |
| Base de données | ✅ Schéma OK |
| Tests | ✅ Prêt |

**Il suffit d'exécuter le script SQL pour corriger le problème.**

---

## 📞 Support

Si le problème persiste après avoir appliqué toutes les corrections:

1. Vérifier les logs détaillés:
```bash
tail -f logs/comptabilite.log
```

2. Vérifier le schéma actuel:
```sql
DESC ECRITURES;
DESC MOUVEMENTS;
```

3. Chercher d'autres occurrences:
```bash
grep -r "SocieteCode\|ExerciceId" sql/
grep -r "SocieteCode\|ExerciceId" src/
```

---

*Guide créé le 23 novembre 2025*
*Correction des procédures stockées*
