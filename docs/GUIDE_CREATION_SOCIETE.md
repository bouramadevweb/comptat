# 🏢 Guide : Créer une Nouvelle Société

## 📋 Vue d'Ensemble

Le script `init_societe.py` permet de créer automatiquement une société complète avec :
- ✅ Les informations de la société (SIREN, adresse, etc.)
- ✅ L'exercice comptable (dates, année)
- ✅ Le plan comptable général (PCG) complet (150+ comptes)
- ✅ Les journaux standards (VE, AC, BQ, OD)
- ✅ Les taux de TVA (20%, 10%, 5.5%, 2.1%)
- ✅ Des tiers exemples (clients et fournisseurs)

---

## 🚀 Méthode 1 : Mode Interactif (Recommandé)

### Étape 1 : Lancer le script

```bash
python init_societe.py
```

### Étape 2 : Répondre aux questions

Le script vous posera les questions suivantes :

```
Nom de la société : Ma Société SARL
SIREN (9 chiffres) : 123456789
Adresse : 10 Rue de la République
Code postal : 75001
Ville : Paris
Année de l'exercice (Enter = 2025) : 2025
```

### Étape 3 : Confirmer

```
✅ Confirmer la création ? (o/N) : o
```

### Étape 4 : Résultat

```
✅ SOCIÉTÉ INITIALISÉE AVEC SUCCÈS !

📊 Société : Ma Société SARL
📅 Exercice : 2025
🏢 ID Société : 2
📆 ID Exercice : 2

👉 Vous pouvez maintenant lancer l'application :
   python main.py
```

---

## 💻 Méthode 2 : Mode Programmatique

### Utiliser le script dans votre code Python

```python
from database import DatabaseManager
from init_societe import InitialisationSociete

# Connexion à la base
db = DatabaseManager()
db.connect()

# Créer l'initialisateur
init = InitialisationSociete(db)

# Créer la société
societe_id, exercice_id, message = init.creer_societe_complete(
    nom_societe="Ma Nouvelle Société SARL",
    siren="987654321",
    adresse="25 Avenue des Entrepreneurs",
    code_postal="69000",
    ville="Lyon",
    annee_exercice=2025
)

print(f"✅ {message}")
print(f"Société ID: {societe_id}, Exercice ID: {exercice_id}")

db.disconnect()
```

---

## 📊 Ce qui est Créé Automatiquement

### 1️⃣ La Société

```sql
Table: SOCIETES
┌────┬─────────────────────┬──────┬───────────┬────────────┬─────────┐
│ ID │ Nom                 │ Pays │ SIREN     │ Code Postal│ Ville   │
├────┼─────────────────────┼──────┼───────────┼────────────┼─────────┤
│ 2  │ Ma Société SARL     │ FR   │ 123456789 │ 75001      │ Paris   │
└────┴─────────────────────┴──────┴───────────┴────────────┴─────────┘
```

### 2️⃣ L'Exercice Comptable

```sql
Table: EXERCICES
┌────┬────────────┬───────┬─────────────┬─────────────┬─────────┐
│ ID │ Société ID │ Année │ Date Début  │ Date Fin    │ Clôturé │
├────┼────────────┼───────┼─────────────┼─────────────┼─────────┤
│ 2  │ 2          │ 2025  │ 2025-01-01  │ 2025-12-31  │ Non     │
└────┴────────────┴───────┴─────────────┴─────────────┴─────────┘
```

**Notes importantes :**
- L'exercice commence automatiquement le **1er janvier**
- Il se termine le **31 décembre**
- Il est **ouvert** par défaut (cloture = FALSE)

### 3️⃣ Les Journaux

```sql
Table: JOURNAUX
┌────┬──────┬─────────────────────────┬──────────┐
│ ID │ Code │ Libellé                 │ Type     │
├────┼──────┼─────────────────────────┼──────────┤
│ 1  │ VE   │ Journal des ventes      │ VENTE    │
│ 2  │ AC   │ Journal des achats      │ ACHAT    │
│ 3  │ BQ   │ Journal de banque       │ BANQUE   │
│ 4  │ OD   │ Opérations diverses     │ OD       │
└────┴──────┴─────────────────────────┴──────────┘
```

### 4️⃣ Le Plan Comptable (150+ comptes)

Le script crée automatiquement **tous les comptes du PCG** :

#### Classe 1 : Capitaux
```
101000 - Capital social
106000 - Réserves
108000 - Compte de l'exploitant
120000 - Résultat de l'exercice (bénéfice)
129000 - Résultat de l'exercice (perte)
164000 - Emprunts
...
```

#### Classe 2 : Immobilisations
```
201000 - Frais d'établissement
205000 - Concessions et droits
211000 - Terrains
213000 - Constructions
215000 - Installations techniques
218300 - Matériel de bureau et informatique
281000 - Amortissements
...
```

#### Classe 3 : Stocks
```
311000 - Matières premières
321000 - Matières consommables
355000 - Produits finis
371000 - Stocks de marchandises
...
```

#### Classe 4 : Tiers
```
401000 - Fournisseurs (lettrable)
411000 - Clients (lettrable)
421000 - Personnel - Rémunérations
431000 - Sécurité sociale
445510 - TVA à décaisser
445660 - TVA déductible
445710 - TVA collectée
455000 - Associés - Comptes courants
...
```

#### Classe 5 : Financiers
```
512000 - Banque (lettrable)
514000 - Chèques postaux
530000 - Caisse
531000 - Caisse en euros
...
```

#### Classe 6 : Charges
```
601000 - Achats matières premières
606000 - Achats non stockés
607000 - Achats de marchandises
611000 - Sous-traitance
613200 - Locations immobilières
616000 - Primes d'assurance
622200 - Honoraires
626000 - Frais postaux
627000 - Services bancaires
641000 - Rémunérations du personnel
645000 - Charges sociales
661000 - Charges d'intérêts
681000 - Dotations aux amortissements
695000 - Impôts sur les bénéfices
...
```

#### Classe 7 : Produits
```
701000 - Ventes de produits finis
706000 - Prestations de services
707000 - Ventes de marchandises
740000 - Subventions d'exploitation
758000 - Produits divers
765000 - Escomptes obtenus
771000 - Produits exceptionnels
781000 - Reprises sur amortissements
...
```

### 5️⃣ Les Taux de TVA

```sql
Table: TAXES
┌────┬────────┬──────────┬───────┬──────────────┬───────────────────┐
│ ID │ Code   │ Nom      │ Taux  │ Compte Coll. │ Compte Déduct.    │
├────┼────────┼──────────┼───────┼──────────────┼───────────────────┤
│ 1  │ TVA20  │ TVA 20%  │ 0.200 │ 445710       │ 445660            │
│ 2  │ TVA10  │ TVA 10%  │ 0.100 │ 445710       │ 445660            │
│ 3  │ TVA055 │ TVA 5.5% │ 0.055 │ 445710       │ 445660            │
│ 4  │ TVA021 │ TVA 2.1% │ 0.021 │ 445710       │ 445660            │
└────┴────────┴──────────┴───────┴──────────────┴───────────────────┘
```

### 6️⃣ Les Tiers Exemples

```sql
Table: TIERS
┌────┬──────────┬───────────────────────┬─────────────┬─────────────┐
│ ID │ Code Aux │ Nom                   │ Type        │ Ville       │
├────┼──────────┼───────────────────────┼─────────────┼─────────────┤
│ 1  │ CLT0001  │ Client Exemple 1      │ CLIENT      │ Paris       │
│ 2  │ CLT0002  │ Client Exemple 2      │ CLIENT      │ Lyon        │
│ 3  │ FRN0001  │ Fournisseur Exemple 1 │ FOURNISSEUR │ Marseille   │
│ 4  │ FRN0002  │ Fournisseur Exemple 2 │ FOURNISSEUR │ Toulouse    │
└────┴──────────┴───────────────────────┴─────────────┴─────────────┘
```

---

## 🎯 Utilisation Après Création

### Lancer l'Application

```bash
python main.py
```

L'application chargera automatiquement :
- ✅ La dernière société créée
- ✅ L'exercice en cours (non clôturé)
- ✅ Tous les journaux
- ✅ Le plan comptable complet

### Commencer à Saisir

1. **Saisir une vente** : Menu Comptabilité → Saisie Vente
2. **Saisir un achat** : Menu Comptabilité → Saisie Achat
3. **Voir la balance** : Menu Rapports → Balance
4. **Voir les comptes** : Onglet "Plan Comptable"

---

## 🔧 Personnalisation

### Ajouter des Comptes Supplémentaires

Si vous avez besoin de comptes spécifiques non présents dans le PCG standard :

```python
# Après avoir créé la société
from database import DatabaseManager

db = DatabaseManager()
db.connect()

query = """
    INSERT INTO COMPTES (societe_id, compte, intitule, classe, type_compte, lettrable)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

# Exemple : ajouter un compte spécifique
db.execute_query(query, (
    2,  # societe_id
    '512100',
    'Banque Crédit Agricole',
    '5',
    'actif',
    True
), fetch=False)

db.disconnect()
```

### Modifier l'Exercice Comptable

Si vous voulez un exercice décalé (ex: 01/07/2025 → 30/06/2026) :

```python
# Modifier manuellement dans la base
UPDATE EXERCICES 
SET date_debut = '2025-07-01', 
    date_fin = '2026-06-30' 
WHERE id = 2;
```

Ou modifier directement dans le script `init_societe.py`, ligne 82 :

```python
def _creer_exercice(self, societe_id, annee):
    # Exercice décalé : 01/07/N → 30/06/N+1
    date_debut = date(annee, 7, 1)
    date_fin = date(annee + 1, 6, 30)
    ...
```

---

## ❓ Questions Fréquentes

### Q : Peut-on créer plusieurs sociétés ?
**R :** Oui ! Vous pouvez créer autant de sociétés que vous voulez. Chacune aura son propre plan comptable et ses exercices.

### Q : Comment supprimer une société ?
**R :** Via MySQL :
```sql
DELETE FROM SOCIETES WHERE id = 2;
```
⚠️ Attention : Cela supprimera aussi tous les exercices, comptes, et écritures associés (CASCADE).

### Q : Le plan comptable est-il complet ?
**R :** Le script crée **150+ comptes** du PCG standard. C'est largement suffisant pour la plupart des entreprises. Vous pouvez ajouter des comptes supplémentaires si nécessaire.

### Q : Peut-on modifier le SIREN après création ?
**R :** Oui :
```sql
UPDATE SOCIETES SET siren = '111222333' WHERE id = 2;
```

### Q : Comment créer un nouvel exercice pour une société existante ?
**R :** Le plus simple est d'utiliser la fonction de clôture qui crée automatiquement l'exercice suivant :
```bash
# Dans l'application : Menu Clôture → Clôturer exercice
```

Ou manuellement :
```sql
INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
VALUES (2, 2026, '2026-01-01', '2026-12-31', FALSE);
```

---

## 📝 Exemple Complet

```bash
# 1. Créer la société
$ python init_societe.py

Nom de la société : Restaurant Le Bon Goût
SIREN (9 chiffres) : 123456789
Adresse : 15 Place de la Mairie
Code postal : 69000
Ville : Lyon
Année de l'exercice : 2025

✅ Confirmer la création ? (o/N) : o

✅ SOCIÉTÉ INITIALISÉE AVEC SUCCÈS !
📊 Société : Restaurant Le Bon Goût
📅 Exercice : 2025
🏢 ID Société : 2

# 2. Lancer l'application
$ python main.py

# 3. Commencer à utiliser !
```

---

## 🎓 Résumé

| Action | Commande | Résultat |
|--------|----------|----------|
| **Créer une société** | `python init_societe.py` | Société + Exercice + PCG + Journaux + TVA |
| **Lancer l'app** | `python main.py` | Interface graphique |
| **Tester** | `python test_installation.py` | Validation complète |

---

**Le script `init_societe.py` fait tout le travail pour vous !** 🚀

Plus besoin de créer manuellement les comptes, les journaux, la TVA, etc. Tout est automatique et conforme au PCG français.
