# 📊 Système de Comptabilité Générale - Version 2.0

Application de comptabilité complète en Python POO avec interface graphique Tkinter, conforme au Plan Comptable Général (PCG) français et capable d'exporter le FEC (Fichier des Écritures Comptables).

## 🎯 Fonctionnalités

### ✨ Gestion Comptable Complète
- ✅ **Saisie d'écritures** : Ventes, Achats, Opérations diverses, Banque
- ✅ **Plan comptable** : Conforme au PCG français (classes 1 à 7)
- ✅ **Tiers** : Gestion clients et fournisseurs
- ✅ **TVA** : Calcul automatique et déclaration
- ✅ **Lettrage** : Rapprochement des paiements

### 📈 Rapports et États Financiers
- ⚖️ **Balance** : Balance générale par compte
- 📊 **Compte de résultat** : Charges et produits
- 📋 **Bilan** : Actif et passif
- 💶 **TVA** : Récapitulatif TVA collectée/déductible
- 📑 **Grand Livre** : Détail de tous les mouvements

### 🔒 Clôture et Conformité
- 🧪 **Tests automatiques** : Vérification de cohérence comptable
- 📤 **Export FEC** : Fichier légal pour l'administration fiscale
- 🔐 **Clôture d'exercice** : Calcul du résultat et report à nouveau
- 📊 **Ouverture d'exercice** : Génération automatique des soldes d'ouverture

## 🏗️ Architecture

### Structure POO

```
📦 Système de Comptabilité
├── 🗄️ Couche Données (models.py)
│   ├── Societe
│   ├── Exercice
│   ├── Journal
│   ├── Compte
│   ├── Tiers
│   ├── Ecriture
│   └── Mouvement
│
├── 🔧 Couche Accès Données (dao.py)
│   ├── SocieteDAO
│   ├── ExerciceDAO
│   ├── CompteDAO
│   ├── EcritureDAO
│   └── BalanceDAO
│
├── 💼 Couche Métier (services.py)
│   └── ComptabiliteService
│       ├── Gestion des écritures
│       ├── Calculs comptables
│       ├── Génération de rapports
│       └── Clôture d'exercice
│
└── 🖥️ Couche Présentation (gui_*.py)
    ├── Interface principale (gui_main.py)
    ├── Saisie vente (gui_vente.py)
    ├── Saisie achat (gui_achat.py)
    ├── Saisie manuelle (gui_ecriture.py)
    └── Rapports (gui_rapports.py)
```

### Fichiers du Projet

```
.
├── config.py              # Configuration de l'application
├── database.py            # Gestionnaire de connexion MySQL
├── models.py              # Modèles de données (dataclasses)
├── dao.py                 # Data Access Objects (CRUD)
├── services.py            # Logique métier
├── gui_main.py           # Interface principale (POINT D'ENTRÉE)
├── gui_vente.py          # Fenêtre de saisie vente
├── gui_achat.py          # Fenêtre de saisie achat
├── gui_ecriture.py       # Fenêtre de saisie manuelle
├── gui_rapports.py       # Fenêtres de rapports
├── requirements.txt      # Dépendances Python
├── .env.example          # Configuration (à copier en .env)
└── README.md             # Cette documentation
```

## 📦 Installation

### Prérequis

- Python 3.8+
- MySQL 8.0+ ou MariaDB 10.5+
- Tkinter (généralement inclus avec Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

3. **Configurer la base de données**

Créer la base de données en exécutant le script SQL fourni :
```bash
mysql -u root -p < schema_comptabilite.sql
```

4. **Configurer l'application**

Copier le fichier de configuration :
```bash
cp .env.example .env
```

Éditer `.env` avec vos paramètres :
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=COMPTA
EXPORT_DIR=/tmp
```

5. **Lancer l'application**
```bash
python gui_main.py
```

## 🚀 Utilisation

### Démarrage

1. Lancer l'application : `python gui_main.py`
2. L'application se connecte automatiquement à la base
3. La société "Bourama Transport SARL" et l'exercice 2025 sont chargés

### Saisie d'une Vente

1. Menu **Comptabilité** → **Saisie Vente**
2. Sélectionner le client
3. Saisir le montant HT
4. Le TTC et la TVA sont calculés automatiquement
5. Valider ✅

L'écriture générée comprend automatiquement :
- Débit 411 (Client)
- Crédit 707 (Ventes)
- Crédit 4457 (TVA collectée)

### Saisie d'un Achat

1. Menu **Comptabilité** → **Saisie Achat**
2. Sélectionner le fournisseur
3. Saisir le montant HT
4. Valider ✅

L'écriture générée comprend :
- Débit 606 (Achats)
- Débit 4456 (TVA déductible)
- Crédit 401 (Fournisseurs)

### Saisie Manuelle

1. Menu **Comptabilité** → **Nouvelle écriture**
2. Saisir l'en-tête (journal, date, référence, libellé)
3. Ajouter les lignes une par une :
   - Sélectionner un compte
   - Saisir le libellé
   - Renseigner le débit OU le crédit
4. Vérifier l'équilibre (Débit = Crédit)
5. Valider ✅

### Consulter la Balance

1. Menu **Rapports** → **Balance**
2. La balance affiche tous les comptes avec :
   - Total débit
   - Total crédit
   - Solde

### Clôture d'Exercice

**⚠️ IMPORTANT : Tester avant de clôturer !**

1. Menu **Clôture** → **Tester comptabilité**
   - Vérification de l'équilibre des écritures
   - Vérification de la cohérence TVA
   - Vérification du format FEC
   - ✅ Tous les tests doivent être OK

2. Menu **Fichier** → **Exporter FEC**
   - Génère le fichier FEC_<SIREN>_<ANNEE>.txt
   - Format conforme à l'administration fiscale

3. Menu **Clôture** → **Clôturer exercice**
   - ⚠️ Action irréversible !
   - Calcule le résultat (Produits - Charges)
   - Crée l'écriture de résultat (compte 120000 ou 129000)
   - Crée l'exercice suivant
   - Génère le Report À Nouveau (RAN)

## 🔧 Fonctionnalités Avancées

### Procédures Stockées Utilisées

L'application utilise les procédures SQL suivantes :

- `Calculer_Balance()` : Recalcule la balance
- `Cloturer_Exercice()` : Clôture complète
- `Exporter_FEC_Exercice()` : Export FEC
- `Tester_Comptabilite_Avancee()` : Tests de cohérence

### Format FEC

Le fichier FEC généré est conforme aux spécifications de l'administration fiscale :
- Encodage UTF-8
- Séparateur pipe (|)
- 18 colonnes obligatoires
- Nommage : FEC_<SIREN>_<ANNEE>.txt

Colonnes exportées :
```
JournalCode|JournalLib|EcritureNum|EcritureDate|CompteNum|CompteLib|
CompAuxNum|CompAuxLib|PieceRef|PieceDate|EcritureLib|Debit|Credit|
EcritureLet|DateLet|ValidDate|MontantDevise|Idevise
```

### Tests de Cohérence

Les tests automatiques vérifient :

1. ✅ **Équilibre** : Débit = Crédit pour chaque écriture
2. ✅ **Comptes existants** : Tous les comptes utilisés existent
3. ✅ **Classes PCG** : Les classes sont valides (1 à 7)
4. ✅ **TVA cohérente** : TVA collectée vs déductible
5. ✅ **FEC valide** : Aucun champ obligatoire vide

## 📊 Modèle de Données

### Principales Tables

- **SOCIETES** : Entreprises
- **EXERCICES** : Périodes comptables
- **JOURNAUX** : VE (Ventes), AC (Achats), BQ (Banque), OD (Divers)
- **COMPTES** : Plan Comptable Général
- **TIERS** : Clients et fournisseurs
- **ECRITURES** : En-têtes de pièces
- **MOUVEMENTS** : Lignes de débit/crédit
- **BALANCE** : Table agrégée des totaux

### Relations

```
SOCIETES
  ├── EXERCICES
  ├── JOURNAUX
  ├── COMPTES
  └── TIERS

EXERCICES
  └── ECRITURES
        └── MOUVEMENTS
              ├── COMPTES
              └── TIERS (optionnel)
```

## 🐛 Dépannage

### Erreur de connexion MySQL

```
❌ Impossible de se connecter à la base
```

**Solutions** :
1. Vérifier que MySQL est démarré
2. Vérifier les paramètres dans `.env`
3. Vérifier les permissions de l'utilisateur MySQL

### Erreur "secure_file_priv"

```
❌ Erreur export FEC : The MySQL server is running with the --secure-file-priv option
```

**Solution** :
```sql
SHOW VARIABLES LIKE 'secure_file_priv';
```
Utiliser le répertoire indiqué ou modifier `my.cnf` :
```
[mysqld]
secure_file_priv = ""
```

### Écriture déséquilibrée

```
❌ Écriture déséquilibrée : Débit=1200.00 vs Crédit=1199.99
```

**Solution** : Vérifier les arrondis. L'écart maximum toléré est 0.01 €.

## 📚 Ressources

- [Plan Comptable Général (PCG)](https://www.plancomptable.com/)
- [Spécifications FEC](https://bofip.impots.gouv.fr/bofip/10693-PGP.html)
- [Documentation MySQL](https://dev.mysql.com/doc/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

## 🤝 Contributions

Ce projet est à but pédagogique. Les contributions sont les bienvenues !

### Comment contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité X'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📝 Licence

Ce projet est à usage pédagogique et de démonstration.

## 👨‍💻 Auteur

**COULIBALY Bourama**
- Exemple pédagogique : Bourama Transport SARL

## ⭐ Remerciements

- Conforme au Plan Comptable Général français
- Inspiration : Pratiques comptables professionnelles
- Interface : Tkinter pour sa simplicité et portabilité

---

## 🎓 Note Pédagogique

Cette application démontre :

1. **Architecture POO** complète (Models, DAO, Services, Views)
2. **Séparation des responsabilités** (chaque couche a un rôle précis)
3. **Gestion de base de données** avec connexion pooling
4. **Interface graphique** professionnelle avec Tkinter
5. **Procédures stockées** pour la logique métier complexe
6. **Gestion des transactions** et de l'intégrité des données
7. **Export de fichiers** conformes aux standards légaux
8. **Tests automatiques** pour la validation des données

## 📞 Support

Pour toute question ou problème :
1. Consulter la section Dépannage
2. Vérifier les logs dans la console
3. Tester la connexion MySQL manuellement

---

**Version** : 2.0  
**Dernière mise à jour** : 2025  
**Statut** : Production-ready pour usage pédagogique ✅
