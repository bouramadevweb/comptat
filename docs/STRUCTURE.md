# 📁 STRUCTURE DU PROJET - Système de Comptabilité Générale

## 🌳 Arborescence Complète

```
comptabilite-python/
│
├── 📄 main.py                    # 🚀 POINT D'ENTRÉE PRINCIPAL (recommandé)
├── 📄 gui_main.py                # Interface principale (alternative)
│
├── 🔧 CONFIGURATION
│   ├── config.py                 # Configuration globale
│   ├── .env                      # Variables d'environnement (à créer)
│   ├── .env.example              # Exemple de configuration
│   └── requirements.txt          # Dépendances Python
│
├── 🗄️ COUCHE DONNÉES
│   ├── database.py               # Gestionnaire de connexion MySQL
│   ├── models.py                 # Modèles de données (dataclasses)
│   └── dao.py                    # Data Access Objects (CRUD)
│
├── 💼 COUCHE MÉTIER
│   └── services.py               # Logique métier comptable
│
├── 🖥️ COUCHE PRÉSENTATION
│   ├── gui_main.py              # Fenêtre principale
│   ├── gui_vente.py             # Saisie de vente
│   ├── gui_achat.py             # Saisie d'achat
│   ├── gui_ecriture.py          # Saisie manuelle d'écriture
│   └── gui_rapports.py          # Fenêtres de rapports
│
├── 🧪 TESTS & OUTILS
│   └── test_installation.py     # Script de test et validation
│
├── 📚 DOCUMENTATION
│   ├── README.md                # Documentation complète
│   ├── QUICKSTART.md            # Guide de démarrage rapide
│   └── STRUCTURE.md             # Ce fichier
│
└── 📊 SQL
    └── schema_comptabilite.sql  # Script de création de la base
```

## 📦 Description des Modules

### 🚀 Point d'Entrée

#### `main.py` ⭐ RECOMMANDÉ
- Point d'entrée robuste avec gestion d'erreurs
- Vérification automatique des dépendances
- Validation de la configuration
- Test de connexion à la base
- Logging détaillé
- **Usage** : `python main.py`

#### `gui_main.py`
- Lancement direct de l'interface
- Sans vérifications préalables
- **Usage** : `python gui_main.py`

### 🔧 Configuration

#### `config.py`
```python
class Config:
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'COMPTA'
```

#### `.env` (à créer depuis .env.example)
```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=COMPTA
```

### 🗄️ Couche Données

#### `database.py` - DatabaseManager
**Responsabilité** : Gestion de la connexion MySQL

**Méthodes principales** :
- `connect()` : Établir la connexion
- `disconnect()` : Fermer la connexion
- `get_cursor()` : Context manager pour curseur
- `execute_query()` : Exécuter une requête
- `call_procedure()` : Appeler une procédure stockée

**Exemple** :
```python
with DatabaseManager() as db:
    results = db.execute_query("SELECT * FROM COMPTES")
```

#### `models.py` - Dataclasses
**Responsabilité** : Définition des structures de données

**Classes principales** :
- `Societe` : Entreprise
- `Exercice` : Période comptable
- `Journal` : Journal comptable (VE, AC, BQ, OD)
- `Compte` : Compte du plan comptable
- `Tiers` : Client ou fournisseur
- `Ecriture` : En-tête de pièce comptable
- `Mouvement` : Ligne débit/crédit
- `Balance` : Ligne de balance

**Exemple** :
```python
compte = Compte(
    compte="512000",
    intitule="Banque BNP",
    classe="5",
    type_compte="actif"
)
```

#### `dao.py` - Data Access Objects
**Responsabilité** : Opérations CRUD sur la base

**Classes DAO** :
- `SocieteDAO` : Gestion des sociétés
- `ExerciceDAO` : Gestion des exercices
- `JournalDAO` : Gestion des journaux
- `CompteDAO` : Gestion des comptes
- `TiersDAO` : Gestion des tiers
- `EcritureDAO` : Gestion des écritures
- `BalanceDAO` : Gestion de la balance

**Exemple** :
```python
compte_dao = CompteDAO(db_manager)
comptes = compte_dao.get_all(societe_id=1)
compte = compte_dao.get_by_numero(1, "512000")
```

### 💼 Couche Métier

#### `services.py` - ComptabiliteService
**Responsabilité** : Logique métier et orchestration

**Groupes de méthodes** :

##### 📊 Gestion des écritures
- `get_ecritures()` : Lister les écritures
- `get_ecriture()` : Détail d'une écriture
- `create_ecriture()` : Créer une écriture
- `creer_ecriture_vente()` : Écriture de vente automatique
- `creer_ecriture_achat()` : Écriture d'achat automatique

##### 📈 Rapports
- `calculer_balance()` : Recalculer la balance
- `get_balance()` : Récupérer la balance
- `get_compte_resultat()` : Compte de résultat
- `get_bilan()` : Bilan comptable
- `get_tva_recap()` : Récapitulatif TVA

##### 🔒 Clôture
- `tester_comptabilite()` : Tests de cohérence
- `cloturer_exercice()` : Clôture complète
- `exporter_fec()` : Export FEC

**Exemple** :
```python
service = ComptabiliteService(db_manager)
success, msg, id = service.creer_ecriture_vente(
    societe_id=1,
    exercice_id=1,
    journal_id=1,
    date_ecriture=date.today(),
    client_id=1,
    montant_ht=Decimal('1000'),
    taux_tva=Decimal('0.20'),
    reference="FAC001",
    libelle="Vente marchandises"
)
```

### 🖥️ Couche Présentation

#### `gui_main.py` - ComptaApp
**Responsabilité** : Fenêtre principale et navigation

**Onglets** :
- 📝 Écritures : Liste des écritures comptables
- 📊 Plan Comptable : Tous les comptes
- 👥 Tiers : Clients et fournisseurs
- 📈 Tableau de bord : Indicateurs et actions rapides

**Menu** :
- Fichier : Export FEC, Quitter
- Comptabilité : Saisies, Calcul balance
- Rapports : Balance, Résultat, Bilan, TVA
- Clôture : Tests, Clôture exercice
- Aide : À propos

#### `gui_vente.py` - VenteWindow
**Responsabilité** : Saisie simplifiée de vente

**Champs** :
- Journal (VE)
- Date
- Client
- Référence facture
- Montant HT
- Taux TVA
- → Calcul automatique TTC

**Génère automatiquement** :
```
411 (Client)        : Débit TTC
707 (Ventes)        : Crédit HT
4457 (TVA collectée): Crédit TVA
```

#### `gui_achat.py` - AchatWindow
**Responsabilité** : Saisie simplifiée d'achat

**Génère automatiquement** :
```
606 (Achats)         : Débit HT
4456 (TVA déductible): Débit TVA
401 (Fournisseur)    : Crédit TTC
```

#### `gui_ecriture.py` - EcritureWindow
**Responsabilité** : Saisie manuelle d'écriture

**Fonctionnalités** :
- Ajout de lignes une par une
- Recherche de comptes
- Vérification d'équilibre en temps réel
- Suppression de lignes
- Validation avant enregistrement

#### `gui_rapports.py`
**Responsabilité** : Affichage des rapports

**Classes** :
- `BalanceWindow` : Balance générale
- `ResultatWindow` : Compte de résultat
- `BilanWindow` : Bilan (Actif/Passif)
- `TVAWindow` : Récapitulatif TVA

### 🧪 Tests

#### `test_installation.py`
**Responsabilité** : Validation de l'installation

**Tests effectués** :
1. ✅ Connexion à la base
2. ✅ Existence des tables
3. ✅ Existence des procédures stockées
4. ✅ Présence des données d'exemple
5. ✅ Calcul de la balance

**Usage** :
```bash
python test_installation.py
```

## 🔄 Flux de Données

### Flux de saisie d'une vente

```
┌─────────────────┐
│   gui_vente.py  │ ← Utilisateur saisit
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   services.py   │ ← Validation & création
│ creer_ecriture_ │
│     vente()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     dao.py      │ ← Enregistrement
│  EcritureDAO    │
│   .create()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  database.py    │ ← Connexion MySQL
│ execute_query() │
└────────┬────────┘
         │
         ▼
    [MySQL/MariaDB]
    Tables: ECRITURES
            MOUVEMENTS
```

### Flux de génération de rapport

```
┌──────────────────┐
│ gui_rapports.py  │ ← Utilisateur demande
│  BalanceWindow   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   services.py    │ ← Récupération données
│  get_balance()   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     dao.py       │ ← Lecture base
│   BalanceDAO     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  database.py     │ ← Exécution requête
└────────┬─────────┘
         │
         ▼
    [MySQL/MariaDB]
    Tables: BALANCE
            COMPTES
```

## 🎨 Principes de Design

### Séparation des Responsabilités

1. **Models** : Structure pure, pas de logique
2. **DAO** : CRUD uniquement, pas de logique métier
3. **Services** : Toute la logique métier
4. **GUI** : Affichage et interaction utilisateur

### Avantages

✅ **Maintenabilité** : Chaque couche est indépendante
✅ **Testabilité** : Facile de tester chaque couche
✅ **Évolutivité** : Ajout de fonctionnalités sans impact
✅ **Réutilisabilité** : Les services peuvent être utilisés en CLI

## 📊 Base de Données

### Tables Principales

```
SOCIETES (1)
  ├─── EXERCICES (N)
  ├─── JOURNAUX (N)
  ├─── COMPTES (N)
  └─── TIERS (N)

EXERCICES (1)
  └─── ECRITURES (N)
         └─── MOUVEMENTS (N)
                ├─── COMPTES (1)
                └─── TIERS (0..1)
```

### Procédures Stockées

- `Calculer_Balance(societe_id, exercice_id)`
- `Cloturer_Exercice(societe_id, exercice_id)`
- `Exporter_FEC_Exercice(societe_id, exercice_id)`
- `Tester_Comptabilite_Avancee(societe_id, exercice_id)`
- `AutoAudit_Cloture(societe_id, exercice_id, ouvrir_suivant)`

## 🚀 Commandes Utiles

### Installation
```bash
pip install -r requirements.txt
mysql -u root -p < schema_comptabilite.sql
cp .env.example .env
# Éditer .env
```

### Lancement
```bash
python main.py              # Recommandé
python gui_main.py          # Alternative
python test_installation.py # Tests
```

### Maintenance
```bash
# Logs
tail -f compta.log

# Backup base de données
mysqldump -u root -p COMPTA > backup_$(date +%Y%m%d).sql

# Restauration
mysql -u root -p COMPTA < backup_20250115.sql
```

## 📝 Notes de Développement

### Ajouter une nouvelle fonctionnalité

1. **Modèle** : Ajouter la dataclass dans `models.py`
2. **DAO** : Créer le DAO dans `dao.py`
3. **Service** : Ajouter la logique dans `services.py`
4. **GUI** : Créer l'interface dans `gui_*.py`

### Conventions de Code

- **PEP 8** : Style Python standard
- **Type hints** : Utilisés partout
- **Docstrings** : Sur toutes les classes et méthodes publiques
- **Logging** : Au lieu de print()

### Bonnes Pratiques

✅ Toujours utiliser des transactions pour les écritures
✅ Valider les données côté service ET côté GUI
✅ Logger les erreurs avec le contexte
✅ Utiliser les context managers pour les connexions DB
✅ Ne jamais exposer les mots de passe dans les logs

## 🎯 Roadmap Future

- [ ] Export Excel des rapports
- [ ] Graphiques de suivi
- [ ] Multi-société
- [ ] Multi-utilisateur avec permissions
- [ ] API REST
- [ ] Application web avec Flask/Django
- [ ] Import automatique de relevés bancaires
- [ ] Rapprochement bancaire
- [ ] Gestion de la trésorerie
- [ ] Budget prévisionnel

---

**Version** : 2.0
**Auteur** : COULIBALY Bourama
**Licence** : Usage pédagogique
