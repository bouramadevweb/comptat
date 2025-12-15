# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## ⚡ Lancer l'Application en 3 Étapes

### Étape 1 : Activer l'Environnement Virtuel

```bash
cd /home/bracoul/Bureau/Bureau/comptabilite/compta/comptabilite-python
source .venv/bin/activate
```

Vous devriez voir `(.venv)` au début de votre ligne de commande.

### Étape 2 : Vérifier les Dépendances

```bash
pip install -r requirements.txt
```

### Étape 3 : Lancer l'Application

```bash
python main.py
```

L'interface graphique devrait s'ouvrir ! 🎉

---

## 📊 Ce que Vous Avez Déjà

D'après la vérification de votre base de données :

✅ **Société** : Coulibaly et fils (ID: 1)
- SIREN: 259835566
- Ville: Billom

✅ **Exercice 2025** : Ouvert (01/01/2025 → 31/12/2025)

✅ **Plan Comptable** : 157 comptes configurés

✅ **Journaux** : VE, AC, BQ, OD

✅ **Taux TVA** : 20%, 10%, 5.5%, 2.1%

✅ **Tiers** : 2 clients, 2 fournisseurs exemples

---

## 🎯 Que Faire Ensuite ?

### 1. Saisir une Première Écriture

Dans l'application :
1. Menu **Comptabilité** → **Saisie Écriture**
2. Choisir un journal (ex: VE pour ventes)
3. Saisir vos lignes
4. Vérifier l'équilibre (Débit = Crédit)
5. Valider

### 2. Consulter la Balance

1. Menu **Rapports** → **Balance**
2. Choisir l'exercice 2025
3. Voir les totaux par compte

### 3. Gérer les Tiers

1. Menu **Tiers** → **Gestion Tiers**
2. Ajouter clients et fournisseurs
3. Consulter les fiches

---

## 🆘 Problèmes Courants

### Erreur "ModuleNotFoundError"

**Solution** : Vérifiez que vous êtes dans le venv
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Erreur "Access denied for user 'root'"

**Solution** : Vérifiez votre configuration MySQL dans `.env`
```bash
# Créer un fichier .env à la racine du projet
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=COMPTA
```

### L'interface ne s'ouvre pas

**Solution** : Vérifiez que tkinter est installé
```bash
# Sur Ubuntu/Debian
sudo apt-get install python3-tk

# Tester
python -c "import tkinter; print('✅ tkinter OK')"
```

### Erreur "Database does not exist"

**Solution** : Créez la base de données
```bash
mysql -u root -p < sql/entity.sql
```

---

## 📝 Commandes Utiles

### Vérifier l'État de la Base

```bash
python check_db.py
```

### Créer une Nouvelle Société

```bash
# Mode simple (non-interactif)
python create_societe_simple.py "Nom Société" "SIREN" 2025

# Mode interactif (dans un terminal)
python -m scripts.init_societe
```

### Lancer les Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

### Générer un Rapport de Couverture

```bash
source .venv/bin/activate
pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

---

## 🔧 Configuration Avancée

### Créer un Fichier .env

Pour personnaliser la configuration, créez `.env` à la racine :

```bash
# Base de données
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=COMPTA

# Sécurité JWT
JWT_SECRET_KEY=votre-cle-secrete-a-changer
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Chemins
EXPORT_DIR=/tmp/exports
BACKUP_DIR=/var/backups/compta
```

**Important** : Ne jamais committer `.env` dans Git !

---

## 📚 Documentation Complète

Pour plus d'informations :

- **Guide d'utilisation** : `GUIDE_UTILISATION.md`
- **Architecture** : `ANALYSE_ARCHITECTURE_COMPLETE.md`
- **Plan d'amélioration** : `PLAN_AMELIORATIONS_PRIORITAIRES.md`
- **Authentification** : `AUTHENTIFICATION_GUIDE.md`
- **Exercices comptables** : `GUIDE_CREATION_EXERCICE.md`

---

## ✅ Checklist de Démarrage

Avant de commencer à utiliser l'application :

- [ ] Environnement virtuel activé (`source .venv/bin/activate`)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Base de données créée et configurée
- [ ] Société existante vérifiée (`python check_db.py`)
- [ ] Application lance sans erreur (`python main.py`)

---

## 🎉 Félicitations !

Vous êtes prêt à utiliser votre système de comptabilité !

Pour toute question, consultez la documentation ou créez une issue sur le projet.

---

**Bon travail comptable !** 📊💼
