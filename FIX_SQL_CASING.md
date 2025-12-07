# 🔧 Correction des Erreurs SQL - PascalCase → snake_case

**Problème détecté**: Les procédures stockées utilisent encore PascalCase (`EcritureId`) alors que la base de données utilise snake_case (`ecriture_id`).

**Erreur**:
```
Unknown column 'EcritureId' in 'SELECT'
```

---

## 🚀 Solution Rapide (2 minutes)

### 1. Exécuter le Script de Correction

```bash
# Depuis le répertoire du projet
mysql -u root -p Comptabilite < sql/03_fix_procedures_casing.sql
```

### 2. Vérifier que ça fonctionne

```bash
# Se connecter à MySQL
mysql -u root -p Comptabilite

# Tester la procédure corrigée
CALL TesterComptabilite('SOC001', 2025);

# Si pas d'erreur, c'est bon! ✅
```

---

## 📝 Ce qui a été corrigé

### Fichiers Modifiés

1. ✅ **sql/03_fix_procedures_casing.sql** (CRÉÉ)
   - Procédure `TesterComptabilite` recréée avec snake_case

2. ✅ **src/infrastructure/backup/backup_manager.py** (CORRIGÉ)
   - Ligne 291: `j.Id = e.JournalId` → `j.id = e.journal_id`
   - Ligne 292-294: `e.SocieteCode`, `e.ExerciceId` → utilise sous-requête avec `societe_id`
   - Ligne 301: `CompteNumero` → `compte_numero`

### Colonnes Corrigées

| Avant (PascalCase) | Après (snake_case) |
|-------------------|-------------------|
| `EcritureId` | `ecriture_id` |
| `ExerciceId` | `exercice_id` |
| `JournalId` | `journal_id` |
| `CompteId` | `compte_id` |
| `SocieteCode` | utilise `societe_id` avec sous-requête |
| `CompteNumero` | `compte_numero` |
| `JournalCode` | `journal_code` |

---

## 🔍 Vérification Complète

### Test 1: Procédure TesterComptabilite

```sql
-- Devrait fonctionner sans erreur maintenant
CALL TesterComptabilite('SOC001', 2025);
```

**Résultat attendu**:
```
+-----------------------------------+----------------+-------------+----------+---------+
| test                              | tests_reussis  | tests_total | resultat | details |
+-----------------------------------+----------------+-------------+----------+---------+
| Tests de cohérence comptable      | 5              | 5           | OK       | ...     |
+-----------------------------------+----------------+-------------+----------+---------+
```

### Test 2: Backup

```python
from src.infrastructure.backup.backup_manager import BackupManager
from src.infrastructure.database.database_manager import DatabaseManager

db = DatabaseManager()
backup = BackupManager(db=db)

# Test backup
success, filename = backup.backup_exercice('SOC001', 2025)
print(f"✅ Backup: {success} - {filename}")
```

### Test 3: Application Complète

```bash
# Lancer l'application
source venv/bin/activate
python src/main.py

# L'erreur "Unknown column 'EcritureId'" ne devrait plus apparaître
```

---

## 📋 Checklist

Avant de continuer:

- [ ] Script SQL exécuté (`sql/03_fix_procedures_casing.sql`)
- [ ] Procédure `TesterComptabilite` testée avec succès
- [ ] Aucune erreur "Unknown column" dans les logs
- [ ] Backup fonctionne correctement
- [ ] Application se lance sans erreur

---

## 🐛 Si Problèmes Persistent

### Erreur: "Access denied"

```bash
# Vérifier vos identifiants MySQL
mysql -u root -p

# Si erreur, essayer avec sudo
sudo mysql

# Ou utiliser votre utilisateur MySQL spécifique
mysql -u votre_utilisateur -p
```

### Erreur: "Procedure already exists"

C'est normal, le script fait `DROP PROCEDURE IF EXISTS` avant de recréer.

### Autres Erreurs SQL

1. Vérifier que la base de données existe:
```sql
SHOW DATABASES LIKE 'Comptabilite';
```

2. Vérifier les tables:
```sql
USE Comptabilite;
SHOW TABLES;
DESC ECRITURES;  -- Vérifier les noms de colonnes
```

3. Si colonnes en PascalCase, relancer le script de migration initial:
```bash
mysql -u root -p Comptabilite < sql/01_database_schema.sql
```

---

## 💡 Prévention Future

Pour éviter ce problème:

1. **Toujours utiliser snake_case** dans les nouvelles requêtes SQL
2. **Tester** les procédures stockées après création
3. **Vérifier les logs** lors du développement

### Convention de Nommage SQL

```sql
-- ✅ CORRECT (snake_case)
SELECT e.id, e.societe_id, e.exercice_id
FROM ECRITURES e
WHERE e.journal_id = 1

-- ❌ INCORRECT (PascalCase)
SELECT e.Id, e.SocieteCode, e.ExerciceId
FROM ECRITURES e
WHERE e.JournalId = 1
```

---

## 📞 Si Ça Ne Fonctionne Toujours Pas

1. Vérifier les logs: `tail -f logs/comptabilite.log`
2. Chercher toutes les occurrences restantes:
```bash
grep -r "EcritureId\|CompteId\|JournalId" sql/
grep -r "EcritureId\|CompteId\|JournalId" src/
```

3. Vérifier le schéma actuel:
```sql
SELECT TABLE_NAME, COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'Comptabilite'
AND TABLE_NAME IN ('ECRITURES', 'MOUVEMENTS', 'JOURNAUX')
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

---

*Guide créé le 23 novembre 2025*
*Correction des erreurs de casse SQL*
