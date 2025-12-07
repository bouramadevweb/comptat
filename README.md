# Logiciel de Comptabilité

Application de comptabilité complète avec interface graphique Tkinter.

## 📁 Structure du projet

```
comptabilite-python/
├── src/                          # Code source
│   ├── presentation/             # Interface graphique (GUI)
│   ├── application/              # Logique métier (Services)
│   ├── domain/                   # Entités métier (Models)
│   ├── infrastructure/           # Infrastructure technique
│   │   ├── persistence/          # Base de données (DAO, Database)
│   │   ├── validation/           # Validation des données
│   │   └── configuration/        # Configuration (Constants, Config)
│   └── utils/                    # Utilitaires (Export, Backup)
├── scripts/                      # Scripts d'initialisation
├── tests/                        # Tests unitaires
├── docs/                         # Documentation
├── sql/                          # Fichiers SQL
├── main.py                       # Point d'entrée
├── requirements.txt              # Dépendances
└── .env                         # Configuration (ne pas commiter)
```

## 🚀 Installation

```bash
# 1. Cloner le projet
cd /chemin/vers/comptabilite-python

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la base de données
cp .env.example .env
# Éditer .env avec vos paramètres MySQL

# 4. Initialiser une société
python scripts/init_societe.py

# 5. Optimiser la base de données
mysql -u root -p COMPTA < sql/optimize_database.sql
```

## 🎯 Utilisation

```bash
# Lancer l'application
python main.py
```

## 📚 Documentation

Voir le dossier `docs/` :
- `ARCHITECTURE.md` - Architecture du logiciel
- `AMELIORATIONS.md` - Guide des améliorations
- `REORGANISATION.md` - Guide de réorganisation
- `QUICKSTART.md` - Démarrage rapide

## ✨ Fonctionnalités

- ✅ Gestion des écritures comptables
- ✅ Plan comptable complet
- ✅ Journaux (Vente, Achat, Banque, OD)
- ✅ Balance, Bilan, Compte de résultat
- ✅ Calcul automatique de la TVA
- ✅ Lettrage des comptes
- ✅ Clôture d'exercice
- ✅ Export Excel/CSV
- ✅ Backup automatique
- ✅ Export FEC (Fichier des Écritures Comptables)

## 🏗️ Architecture

Le logiciel suit une **architecture en couches (Layered Architecture)** :

1. **Présentation** : Interface graphique Tkinter
2. **Application** : Logique métier (ComptabiliteService)
3. **Domaine** : Entités métier pures
4. **Infrastructure** : Persistance, validation, configuration
5. **Utilitaires** : Export, backup

## 📖 Version

**Version 2.0** - Janvier 2025

## 📝 License

Propriétaire
# comptat
