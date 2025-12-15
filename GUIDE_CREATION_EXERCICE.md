# Guide Rapide : Créer un Exercice Comptable

## Option 1 : Utiliser le Script Interactif (Recommandé)

Le script `scripts/init_societe.py` crée automatiquement tout ce dont vous avez besoin.

### Comment l'utiliser :

```bash
# Depuis le terminal (mode interactif)
python -m scripts.init_societe
```

Le script va vous poser des questions et créer :
- ✅ La société
- ✅ **L'exercice comptable**
- ✅ Le plan comptable complet (300+ comptes validés)
- ✅ Les journaux (VE, AC, BQ, OD)
- ✅ Les taux de TVA
- ✅ Des tiers exemples

---

## Option 2 : Créer Manuellement en SQL

### 1. Créer une Société

```sql
INSERT INTO SOCIETES (nom, pays, siren, code_postal, ville, date_creation)
VALUES ('Ma Société SARL', 'FR', '123456789', '75001', 'Paris', CURDATE());
```

### 2. Créer un Exercice Comptable

```sql
-- Récupérer l'ID de la société que vous venez de créer
SELECT id, nom FROM SOCIETES ORDER BY id DESC LIMIT 1;

-- Créer l'exercice (remplacer 1 par l'ID de votre société)
INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
VALUES (1, 2025, '2025-01-01', '2025-12-31', FALSE);
```

### 3. Créer les Journaux

```sql
-- Remplacer 1 par l'ID de votre société
INSERT INTO JOURNAUX (societe_id, code, libelle, type, compteur) VALUES
(1, 'VE', 'Journal des ventes', 'VENTE', 0),
(1, 'AC', 'Journal des achats', 'ACHAT', 0),
(1, 'BQ', 'Journal de banque', 'BANQUE', 0),
(1, 'OD', 'Opérations diverses', 'OD', 0);
```

### 4. Créer quelques Comptes Essentiels

```sql
-- Remplacer 1 par l'ID de votre société
INSERT INTO COMPTES (societe_id, compte, intitule, classe, type_compte, lettrable) VALUES
-- Classe 1 : Capitaux
(1, '101000', 'Capital social', '1', 'passif', FALSE),
(1, '120000', 'Résultat de l\'exercice (bénéfice)', '1', 'passif', FALSE),

-- Classe 4 : Tiers
(1, '401000', 'Fournisseurs', '4', 'passif', TRUE),
(1, '411000', 'Clients', '4', 'actif', TRUE),
(1, '445660', 'TVA déductible', '4', 'actif', FALSE),
(1, '445710', 'TVA collectée', '4', 'passif', FALSE),

-- Classe 5 : Financiers
(1, '512000', 'Banque', '5', 'actif', TRUE),
(1, '530000', 'Caisse', '5', 'actif', FALSE),

-- Classe 6 : Charges
(1, '606000', 'Achats non stockés', '6', 'charge', FALSE),
(1, '607000', 'Achats de marchandises', '6', 'charge', FALSE),
(1, '641000', 'Rémunérations du personnel', '6', 'charge', FALSE),

-- Classe 7 : Produits
(1, '706000', 'Prestations de services', '7', 'produit', FALSE),
(1, '707000', 'Ventes de marchandises', '7', 'produit', FALSE);
```

### 5. Créer les Taux de TVA

```sql
-- D'abord récupérer les IDs des comptes de TVA
SELECT id, compte, intitule FROM COMPTES
WHERE societe_id = 1 AND compte IN ('445710', '445660');

-- Puis créer les taux (remplacer les IDs par ceux obtenus ci-dessus)
-- Exemple : compte_collecte_id = 10, compte_deductible_id = 11
INSERT INTO TAXES (societe_id, code, nom, taux, compte_collecte_id, compte_deductible_id) VALUES
(1, 'TVA20', 'TVA 20%', 0.200, 10, 11),
(1, 'TVA10', 'TVA 10%', 0.100, 10, 11),
(1, 'TVA055', 'TVA 5.5%', 0.055, 10, 11);
```

---

## Option 3 : Créer via Python (programmatique)

Créez un fichier `mon_init.py` :

```python
#!/usr/bin/env python3
from datetime import date
from src.infrastructure.persistence.database import DatabaseManager

def creer_exercice_simple():
    """Crée un exercice simple pour une société"""

    db = DatabaseManager()
    db.connect()

    # 1. Créer la société
    query_societe = """
        INSERT INTO SOCIETES (nom, pays, siren, code_postal, ville, date_creation)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    with db.get_cursor() as cursor:
        cursor.execute(query_societe, (
            'Ma Société SARL',
            'FR',
            '123456789',
            '75001',
            'Paris',
            date.today()
        ))
        societe_id = cursor.lastrowid
        print(f"✅ Société créée (ID: {societe_id})")

    # 2. Créer l'exercice
    query_exercice = """
        INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
        VALUES (%s, %s, %s, %s, %s)
    """

    with db.get_cursor() as cursor:
        cursor.execute(query_exercice, (
            societe_id,
            2025,
            date(2025, 1, 1),
            date(2025, 12, 31),
            False
        ))
        exercice_id = cursor.lastrowid
        print(f"✅ Exercice créé (ID: {exercice_id})")

    # 3. Créer les journaux
    query_journal = """
        INSERT INTO JOURNAUX (societe_id, code, libelle, type, compteur)
        VALUES (%s, %s, %s, %s, 0)
    """

    journaux = [
        ('VE', 'Journal des ventes', 'VENTE'),
        ('AC', 'Journal des achats', 'ACHAT'),
        ('BQ', 'Journal de banque', 'BANQUE'),
        ('OD', 'Opérations diverses', 'OD'),
    ]

    with db.get_cursor() as cursor:
        for code, libelle, type_j in journaux:
            cursor.execute(query_journal, (societe_id, code, libelle, type_j))
        print("✅ 4 journaux créés")

    db.disconnect()

    print(f"\n🎉 Configuration terminée !")
    print(f"📊 Société ID : {societe_id}")
    print(f"📅 Exercice ID : {exercice_id}")
    print(f"📅 Période : 01/01/2025 → 31/12/2025")

if __name__ == "__main__":
    creer_exercice_simple()
```

Puis exécutez :

```bash
python mon_init.py
```

---

## Option 4 : Vérifier ce qui Existe Déjà

Peut-être que vous avez déjà une société et un exercice. Vérifiez :

```sql
-- Voir toutes les sociétés
SELECT * FROM SOCIETES;

-- Voir tous les exercices
SELECT e.*, s.nom
FROM EXERCICES e
JOIN SOCIETES s ON e.societe_id = s.id;

-- Voir si vous avez des journaux
SELECT * FROM JOURNAUX;

-- Voir si vous avez des comptes
SELECT COUNT(*) as nb_comptes FROM COMPTES;
```

---

## Résumé

| Méthode | Complexité | Résultat |
|---------|-----------|----------|
| **Script interactif** | Facile | Société + Exercice + Plan complet + Journaux + TVA |
| **SQL manuel** | Moyen | Configuration minimale rapide |
| **Python custom** | Avancé | Configuration sur mesure |
| **Vérification** | Très facile | Voir ce qui existe |

---

## Pour Lancer le Script Interactif

Ouvrez un **nouveau terminal** et tapez :

```bash
cd /home/bracoul/Bureau/Bureau/comptabilite/compta/comptabilite-python
python -m scripts.init_societe
```

Puis répondez aux questions :
1. Afficher les règles ? → `n`
2. Nom de la société → `Ma Société`
3. SIREN → `123456789`
4. Adresse → `10 Rue du Commerce`
5. Code postal → `75001`
6. Ville → `Paris`
7. Année → `2025` (ou Entrée)
8. Mode validation → `1` (strict)
9. Confirmer → `o`

**C'est tout !** Votre société et exercice seront créés avec tout le nécessaire.

---

## Questions Fréquentes

### Comment créer un 2ème exercice ?

Si vous avez déjà une société et voulez ajouter l'exercice 2026 :

```sql
INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
VALUES (1, 2026, '2026-01-01', '2026-12-31', FALSE);
```

### Comment modifier les dates d'un exercice ?

Si votre exercice n'est pas de janvier à décembre (ex: juillet à juin) :

```sql
UPDATE EXERCICES
SET date_debut = '2025-07-01',
    date_fin = '2026-06-30'
WHERE id = 1;
```

### Comment clôturer un exercice ?

```sql
UPDATE EXERCICES
SET cloture = TRUE
WHERE id = 1;
```

---

**Conseil** : La méthode la plus simple est d'utiliser le script interactif dans un terminal. Il fait tout automatiquement ! 🚀
