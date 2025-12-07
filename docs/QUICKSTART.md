# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## Installation en 5 minutes

### 1️⃣ Prérequis

Vérifiez que vous avez :
- ✅ Python 3.8+ installé
- ✅ MySQL 8.0+ ou MariaDB 10.5+ installé et démarré
- ✅ Accès root ou utilisateur avec privilèges CREATE DATABASE

### 2️⃣ Installation

```bash
# 1. Installer les dépendances Python
pip install -r requirements.txt

# 2. Créer la base de données
mysql -u root -p < schema_comptabilite.sql
# Entrez votre mot de passe MySQL

# 3. Configurer l'application
cp .env.example .env
# Éditez .env avec votre mot de passe MySQL
```

### 3️⃣ Configuration

Éditez le fichier `.env` :

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=VOTRE_MOT_DE_PASSE    # ⚠️ À MODIFIER
DB_NAME=COMPTA
EXPORT_DIR=/tmp
```

### 4️⃣ Test de l'installation

```bash
python test_installation.py
```

Vous devriez voir :
```
✅ Connexion à la base de données réussie
✅ Toutes les tables sont présentes (12)
✅ Toutes les procédures sont présentes (5)
✅ 1 société(s) trouvée(s)
✅ Balance calculée : X compte(s)
🎉 Tous les tests sont passés ! L'application est prête.
```

### 5️⃣ Lancer l'application

```bash
python gui_main.py
```

## 🎯 Premier Usage

### Saisir votre première vente

1. Menu **Comptabilité** → **Saisie Vente**
2. Remplir :
   - Client : `CLT0001 - Client Dupont SA`
   - Date : `2025-01-15`
   - Référence : `FAC001`
   - Montant HT : `1000`
   - TVA : `20%`
3. Cliquer sur **✅ Valider**

### Voir la balance

1. Menu **Comptabilité** → **Calculer Balance** (une seule fois)
2. Menu **Rapports** → **Balance**

### Voir le compte de résultat

1. Menu **Rapports** → **Compte de résultat**

Vous verrez :
- 📊 **Produits** : 1000.00 €
- 📊 **Charges** : 0.00 €
- 💚 **Résultat (BÉNÉFICE)** : 1000.00 €

## 🔧 Résolution de Problèmes

### ❌ Erreur de connexion MySQL

```bash
# Vérifier que MySQL est démarré
sudo systemctl status mysql
# ou
sudo service mysql status

# Démarrer MySQL si nécessaire
sudo systemctl start mysql
```

### ❌ Mot de passe MySQL incorrect

Éditez le fichier `.env` et corrigez `DB_PASSWORD`

### ❌ Base de données non trouvée

Recréez la base :
```bash
mysql -u root -p < schema_comptabilite.sql
```

### ❌ Tables manquantes

Le script SQL n'a pas été exécuté complètement. Recommencez :
```bash
# Supprimer la base existante
mysql -u root -p -e "DROP DATABASE IF EXISTS COMPTA;"

# Recréer
mysql -u root -p < schema_comptabilite.sql
```

## 📚 Exemples d'utilisation

### Saisir un achat

```
Menu Comptabilité → Saisie Achat
Fournisseur : FRN0001 - Fournisseur Martin SAS
Montant HT : 500
Référence : FACFOUR001
✅ Valider
```

### Saisir une écriture manuelle

```
Menu Comptabilité → Nouvelle écriture

Ligne 1 : 512000 (Banque) - Débit : 2000
Ligne 2 : 101000 (Capital) - Crédit : 2000

✅ Valider
```

### Exporter le FEC

```
Menu Fichier → Exporter FEC
```

Le fichier sera créé dans `/tmp/FEC_123456789_2025.txt`

### Tester la comptabilité

```
Menu Clôture → Tester comptabilité
```

Résultat attendu :
```
✅ OK - Equilibre_Ecritures
✅ OK - Comptes_Existants
✅ OK (TVA à payer : XX.XX €) - Cohérence_TVA
✅ OK - Classes_PCG
✅ OK - FEC_Conformité
💚 COMPTABILITÉ CONFORME
```

## 🎓 Concepts Clés

### Les Journaux

- **VE** : Ventes
- **AC** : Achats
- **BQ** : Banque
- **OD** : Opérations diverses

### Les Classes PCG

- **Classe 1** : Capitaux
- **Classe 2** : Immobilisations
- **Classe 3** : Stocks
- **Classe 4** : Tiers (clients/fournisseurs)
- **Classe 5** : Financiers (banque, caisse)
- **Classe 6** : Charges
- **Classe 7** : Produits

### L'Équilibre Comptable

Chaque écriture doit respecter :
```
DÉBIT = CRÉDIT
```

Exemple de vente 1200 € TTC (1000 HT + 200 TVA) :
```
Débit  411 (Client)        : 1200
Crédit 707 (Ventes)        : 1000
Crédit 4457 (TVA collectée): 200
──────────────────────────────
TOTAL DÉBIT  = 1200
TOTAL CRÉDIT = 1200  ✅
```

## 📞 Support

Si vous rencontrez des problèmes :

1. 🧪 Exécuter les tests : `python test_installation.py`
2. 📖 Consulter le README.md complet
3. 🔍 Vérifier les logs dans la console

## ✨ Fonctionnalités Principales

| Fonctionnalité | Raccourci |
|----------------|-----------|
| Nouvelle vente | Menu Comptabilité → Saisie Vente |
| Nouvel achat | Menu Comptabilité → Saisie Achat |
| Balance | Menu Rapports → Balance |
| Résultat | Menu Rapports → Compte de résultat |
| Export FEC | Menu Fichier → Exporter FEC |
| Tests | Menu Clôture → Tester comptabilité |
| Clôture | Menu Clôture → Clôturer exercice |

## 🎯 Prochaines Étapes

1. ✅ Installer et tester l'application
2. 📝 Saisir quelques écritures de test
3. 📊 Consulter les rapports
4. 🧪 Tester la cohérence
5. 📤 Exporter le FEC
6. 🔒 Clôturer l'exercice (optionnel)

---

**Prêt à démarrer ?** → `python gui_main.py`

Bon travail ! 🚀
