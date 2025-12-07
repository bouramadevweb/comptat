# 🎉 Système de Comptabilité Générale en Python POO

## ✨ Application Complète et Professionnelle

Vous venez de recevoir une **application de comptabilité complète** développée en Python avec une architecture orientée objet (POO) professionnelle, conforme au Plan Comptable Général (PCG) français.

---

## 📦 Contenu du Package

### 🚀 Fichiers Principaux

| Fichier | Description | Rôle |
|---------|-------------|------|
| **main.py** | 🎯 Point d'entrée recommandé | Lance l'application avec vérifications |
| **gui_main.py** | Interface graphique principale | Fenêtre principale de l'application |
| **config.py** | Configuration | Paramètres de connexion |
| **database.py** | Gestionnaire DB | Connexion MySQL/MariaDB |
| **models.py** | Modèles de données | Dataclasses Python |
| **dao.py** | Accès aux données | CRUD sur la base |
| **services.py** | Logique métier | Toute la logique comptable |

### 🖥️ Interfaces Utilisateur

| Fichier | Description |
|---------|-------------|
| **gui_vente.py** | Saisie rapide de vente |
| **gui_achat.py** | Saisie rapide d'achat |
| **gui_ecriture.py** | Saisie manuelle d'écriture |
| **gui_rapports.py** | Balance, Résultat, Bilan, TVA |

### 📚 Documentation

| Fichier | Description |
|---------|-------------|
| **README.md** | 📖 Documentation complète |
| **QUICKSTART.md** | 🚀 Démarrage en 5 minutes |
| **STRUCTURE.md** | 🏗️ Architecture du projet |

### 🔧 Configuration & Tests

| Fichier | Description |
|---------|-------------|
| **requirements.txt** | Dépendances Python |
| **.env.example** | Exemple de configuration |
| **test_installation.py** | Script de validation |

---

## 🎯 Fonctionnalités Principales

### ✅ Comptabilité Complète
- Saisie d'écritures (Ventes, Achats, Banque, OD)
- Plan comptable conforme au PCG
- Gestion des tiers (clients/fournisseurs)
- Calcul automatique de la TVA
- Lettrage des comptes

### 📊 Rapports et États
- Balance générale
- Compte de résultat
- Bilan (Actif/Passif)
- Récapitulatif TVA
- Grand Livre

### 🔒 Conformité Légale
- Export FEC (Fichier des Écritures Comptables)
- Tests automatiques de cohérence
- Clôture d'exercice complète
- Report à nouveau automatique

---

## 🚀 Démarrage Rapide

### 1️⃣ Prérequis

Vous devez avoir installé :
- ✅ **Python 3.8+**
- ✅ **MySQL 8.0+** ou **MariaDB 10.5+**

### 2️⃣ Installation (3 commandes)

```bash
# 1. Installer les dépendances Python
pip install -r requirements.txt

# 2. Créer la base de données
mysql -u root -p < schema_comptabilite.sql

# 3. Configurer l'application
cp .env.example .env
# Éditez .env avec votre mot de passe MySQL
```

### 3️⃣ Lancement

```bash
# Méthode recommandée (avec vérifications)
python main.py

# Ou directement l'interface
python gui_main.py
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
🎉 Tous les tests sont passés !
```

---

## 📖 Documentation Détaillée

### Pour commencer
👉 Lisez **QUICKSTART.md** - Guide de démarrage en 5 minutes

### Pour comprendre l'architecture
👉 Lisez **STRUCTURE.md** - Architecture complète du projet

### Pour tout savoir
👉 Lisez **README.md** - Documentation exhaustive

---

## 🏗️ Architecture POO Professionnelle

```
┌─────────────────────────────────────────────┐
│           COUCHE PRÉSENTATION               │
│  (gui_main.py, gui_vente.py, etc.)         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│           COUCHE MÉTIER                     │
│          (services.py)                      │
│  • Logique comptable                        │
│  • Validation des données                   │
│  • Génération de rapports                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       COUCHE ACCÈS DONNÉES                  │
│            (dao.py)                         │
│  • CRUD sur toutes les tables               │
│  • Pas de logique métier                    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      GESTIONNAIRE BASE DE DONNÉES           │
│          (database.py)                      │
│  • Connexion MySQL/MariaDB                  │
│  • Gestion des transactions                 │
└──────────────────┬──────────────────────────┘
                   │
              [MySQL/MariaDB]
```

### Avantages de cette architecture

✅ **Séparation des responsabilités** : Chaque couche a un rôle précis
✅ **Maintenabilité** : Facile de modifier une partie sans tout casser
✅ **Testabilité** : Chaque couche peut être testée indépendamment
✅ **Évolutivité** : Ajout de fonctionnalités sans impact majeur
✅ **Réutilisabilité** : Les services peuvent être utilisés ailleurs

---

## 🎨 Interface Graphique (Tkinter)

### Fenêtre Principale

```
┌────────────────────────────────────────────────┐
│  Système de Comptabilité Générale v2.0        │
├────────────────────────────────────────────────┤
│  Société: Bourama Transport SARL               │
│  Exercice: 2025 (2025-01-01 → 2025-12-31)    │
├────────────────────────────────────────────────┤
│  [📝 Écritures] [📊 Plan] [👥 Tiers] [📈 Bord]│
│                                                 │
│  ┌──────────────────────────────────────────┐ │
│  │  Liste des écritures comptables          │ │
│  │  N° | Date | Journal | Réf | Libellé    │ │
│  │  ─────────────────────────────────────── │ │
│  │  ...                                      │ │
│  └──────────────────────────────────────────┘ │
│                                                 │
└────────────────────────────────────────────────┘
```

### Fonctionnalités Clés

- 🖱️ **Saisie guidée** : Formulaires intuitifs
- 🔍 **Recherche rapide** : Trouver comptes et tiers facilement
- 📊 **Rapports visuels** : Tableaux bien structurés
- ⚠️ **Validations** : Vérifications en temps réel
- ✅ **Feedback visuel** : Messages de confirmation

---

## 💻 Exemples d'Utilisation

### Saisir une vente

```python
# Via l'interface : Menu → Comptabilité → Saisie Vente
# Ou programmatiquement :

from services import ComptabiliteService
from database import DatabaseManager
from datetime import date
from decimal import Decimal

db = DatabaseManager()
service = ComptabiliteService(db)

success, message, id = service.creer_ecriture_vente(
    societe_id=1,
    exercice_id=1,
    journal_id=1,  # Journal VE (Ventes)
    date_ecriture=date.today(),
    client_id=1,
    montant_ht=Decimal('1000'),
    taux_tva=Decimal('0.20'),
    reference="FAC001",
    libelle="Vente de marchandises"
)

if success:
    print(f"✅ {message}")
    # Génère automatiquement :
    # Débit  411 (Client)        : 1200.00
    # Crédit 707 (Ventes)        : 1000.00
    # Crédit 4457 (TVA collectée):  200.00
```

### Consulter la balance

```python
# Calculer la balance
service.calculer_balance(societe_id=1, exercice_id=1)

# Récupérer la balance
balance = service.get_balance(societe_id=1, exercice_id=1)

for ligne in balance:
    print(f"{ligne.compte} | {ligne.intitule:40s} | "
          f"Débit: {ligne.total_debit:>10.2f} | "
          f"Crédit: {ligne.total_credit:>10.2f} | "
          f"Solde: {ligne.solde:>10.2f}")
```

---

## 🔐 Sécurité et Conformité

### Validations Automatiques

- ✅ Équilibre des écritures (Débit = Crédit)
- ✅ Existence des comptes utilisés
- ✅ Cohérence de la TVA
- ✅ Respect du Plan Comptable Général
- ✅ Format FEC conforme

### Export FEC Légal

Format officiel pour l'administration fiscale française :
```
FEC_<SIREN>_<ANNEE>.txt
```

Contient toutes les écritures de l'exercice avec :
- 18 colonnes obligatoires
- Encodage UTF-8
- Séparateur pipe (|)
- Conforme à la norme BOFIP

---

## 🛠️ Technologies Utilisées

| Technologie | Usage | Version |
|-------------|-------|---------|
| **Python** | Langage principal | 3.8+ |
| **Tkinter** | Interface graphique | Standard |
| **MySQL** | Base de données | 8.0+ |
| **mysql-connector-python** | Connecteur DB | 8.2.0 |
| **python-dotenv** | Configuration | 1.0.0 |

### Choix Techniques

✅ **Tkinter** : Portable, inclus avec Python, léger
✅ **MySQL** : Robuste, performant, largement utilisé
✅ **Dataclasses** : Code propre et type-safe
✅ **Context managers** : Gestion propre des ressources
✅ **Procédures stockées** : Logique métier dans la base

---

## 📊 Base de Données

### 12 Tables Principales

```
SOCIETES ──┬── EXERCICES
           ├── JOURNAUX
           ├── COMPTES
           ├── TIERS
           └── TAXES

EXERCICES ─── ECRITURES ─── MOUVEMENTS ──┬── COMPTES
                                          └── TIERS

LETTRAGES ─── LETTRAGE_LIGNES ─── MOUVEMENTS

BALANCE (table agrégée)
```

### 5 Procédures Stockées

1. **Calculer_Balance** : Recalcule la balance
2. **Cloturer_Exercice** : Clôture complète avec résultat
3. **Exporter_FEC_Exercice** : Génère le fichier FEC
4. **Tester_Comptabilite_Avancee** : Tests de cohérence
5. **AutoAudit_Cloture** : Audit + clôture automatique

---

## 🎓 Projet Pédagogique

Cette application démontre :

### Concepts de Programmation
- ✅ Architecture en couches (POO)
- ✅ Séparation des responsabilités
- ✅ Gestion de base de données
- ✅ Interfaces graphiques
- ✅ Tests automatiques
- ✅ Logging et gestion d'erreurs

### Concepts Comptables
- ✅ Plan Comptable Général (PCG)
- ✅ Partie double (Débit/Crédit)
- ✅ Journaux comptables
- ✅ Balance, Bilan, Résultat
- ✅ TVA collectée/déductible
- ✅ Clôture d'exercice

---

## 🚀 Évolutions Possibles

### Court Terme
- [ ] Export Excel des rapports
- [ ] Graphiques de suivi
- [ ] Impression PDF

### Moyen Terme
- [ ] Multi-société
- [ ] Multi-utilisateur avec permissions
- [ ] Rapprochement bancaire automatique

### Long Terme
- [ ] API REST
- [ ] Application web (Flask/Django)
- [ ] Application mobile
- [ ] Intelligence artificielle (catégorisation automatique)

---

## 📞 Support et Documentation

### Fichiers à Consulter

1. **Problème d'installation ?** → `QUICKSTART.md`
2. **Comment utiliser ?** → `README.md`
3. **Comment ça marche ?** → `STRUCTURE.md`
4. **Erreurs ?** → `test_installation.py`

### Commandes de Dépannage

```bash
# Tester l'installation
python test_installation.py

# Voir les logs
tail -f compta.log

# Recréer la base
mysql -u root -p -e "DROP DATABASE IF EXISTS COMPTA;"
mysql -u root -p < schema_comptabilite.sql
```

---

## ✨ Points Forts de l'Application

| Aspect | Description |
|--------|-------------|
| 🏗️ **Architecture** | POO professionnelle, maintenable |
| 📚 **Documentation** | Complète et pédagogique |
| ✅ **Qualité** | Code propre, type hints, docstrings |
| 🔒 **Sécurité** | Validations, transactions, tests |
| 📊 **Conformité** | PCG, FEC, normes comptables |
| 🎨 **UX** | Interface intuitive et guidée |
| 🧪 **Tests** | Automatiques et complets |
| 📈 **Performance** | Optimisée avec procédures stockées |

---

## 🎯 Conclusion

Vous disposez maintenant d'une **application de comptabilité complète et professionnelle** qui peut servir :

✅ De **base d'apprentissage** pour Python POO
✅ De **référence** pour une architecture en couches
✅ De **prototype** pour un logiciel de gestion
✅ D'**outil pédagogique** pour la comptabilité
✅ De **base** pour un projet plus ambitieux

---

## 🎉 Prêt à Démarrer ?

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer
cp .env.example .env
# Éditez .env

# 3. Créer la base
mysql -u root -p < schema_comptabilite.sql

# 4. Tester
python test_installation.py

# 5. Lancer !
python main.py
```

---

**Version** : 2.0  
**Licence** : Usage pédagogique  
**Auteur** : Exemple pédagogique COULIBALY Bourama

**🚀 Bon développement !**
