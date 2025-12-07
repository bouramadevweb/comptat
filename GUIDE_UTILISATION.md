# 📘 Guide d'Utilisation des Nouvelles Fonctionnalités

**Version 2.0** - Architecture en couches

---

## Table des matières

1. [Export Excel/PDF](#1-export-excelpdf)
2. [Backup Automatique](#2-backup-automatique)
3. [Lettrage des Comptes](#3-lettrage-des-comptes)
4. [Validation des Données](#4-validation-des-données)
5. [Utilisation des Constantes](#5-utilisation-des-constantes)
6. [Scripts Utiles](#6-scripts-utiles)

---

## 1. Export Excel/PDF

### 1.1 Exporter la Balance en Excel

```python
#!/usr/bin/env python3
"""
Exemple: Exporter la balance en Excel
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService
from src.utils.export_utils import ExportManager

# Initialisation
db = DatabaseManager()
service = ComptabiliteService(db)
export_manager = ExportManager(output_dir="/tmp/exports")

# Récupérer les données
societe_id = 1
exercice_id = 1

balance = service.get_balance(societe_id, exercice_id)
societe = service.get_societe(societe_id)
exercice = service.exercice_dao.get_by_id(exercice_id)

# Exporter en Excel
success, filepath = export_manager.exporter_balance_excel(
    balance_data=balance,
    societe_nom=societe.nom,
    exercice_annee=exercice.annee
)

if success:
    print(f"✅ Balance exportée: {filepath}")
else:
    print(f"❌ Erreur: {filepath}")

db.disconnect()
```

**Résultat**: Fichier Excel formaté avec couleurs, bordures, totaux

### 1.2 Exporter le Compte de Résultat en Excel

```python
#!/usr/bin/env python3
"""
Exemple: Exporter le compte de résultat en Excel
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService
from src.utils.export_utils import ExportManager

db = DatabaseManager()
service = ComptabiliteService(db)
export_manager = ExportManager(output_dir="/tmp/exports")

# Récupérer le compte de résultat
societe_id = 1
exercice_id = 1

resultat = service.get_compte_resultat(societe_id, exercice_id)
societe = service.get_societe(societe_id)
exercice = service.exercice_dao.get_by_id(exercice_id)

# Exporter
success, filepath = export_manager.exporter_compte_resultat_excel(
    charges=resultat['charges'],
    produits=resultat['produits'],
    total_charges=resultat['total_charges'],
    total_produits=resultat['total_produits'],
    resultat=resultat['resultat'],
    societe_nom=societe.nom,
    exercice_annee=exercice.annee
)

if success:
    print(f"✅ Compte de résultat exporté: {filepath}")
    print(f"   Résultat: {resultat['resultat']}")

db.disconnect()
```

### 1.3 Export CSV (plus simple)

```python
#!/usr/bin/env python3
"""
Exemple: Export CSV de la balance
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService
from src.utils.export_utils import ExportManager

db = DatabaseManager()
service = ComptabiliteService(db)
export_manager = ExportManager(output_dir="/tmp/exports")

balance = service.get_balance(1, 1)

success, filepath = export_manager.exporter_balance_csv(
    balance_data=balance,
    filename="balance_2025.csv"
)

if success:
    print(f"✅ Balance CSV: {filepath}")

db.disconnect()
```

---

## 2. Backup Automatique

### 2.1 Créer un Backup Simple

```python
#!/usr/bin/env python3
"""
Exemple: Créer un backup de la base de données
"""
from src.infrastructure.backup import BackupManager

# Initialiser le gestionnaire de backups
manager = BackupManager(backup_dir="/var/backups/compta")

# Créer un backup compressé
success, filepath = manager.creer_backup(
    compress=True,
    include_procedures=True
)

if success:
    print(f"✅ Backup créé: {filepath}")

    # Afficher la taille
    import os
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"   Taille: {size_mb:.2f} MB")
else:
    print(f"❌ Erreur: {filepath}")
```

### 2.2 Backup Automatique avec Rotation

```python
#!/usr/bin/env python3
"""
Exemple: Backup avec rotation (garder seulement les 7 derniers)
"""
from src.infrastructure.backup import BackupManager

manager = BackupManager(backup_dir="/var/backups/compta")

# Créer backup et nettoyer les anciens (garde 7 backups max)
success, message = manager.creer_backup_automatique(
    max_backups=7,
    compress=True
)

print(message)
```

### 2.3 Lister les Backups Existants

```python
#!/usr/bin/env python3
"""
Exemple: Lister tous les backups
"""
from src.infrastructure.backup import BackupManager

manager = BackupManager(backup_dir="/var/backups/compta")

backups = manager.lister_backups()

print(f"📦 {len(backups)} backup(s) trouvé(s):\n")

for backup in backups:
    print(f"  📄 {backup['filename']}")
    print(f"     Date: {backup['date'].strftime('%d/%m/%Y %H:%M')}")
    print(f"     Taille: {backup['size_mb']:.2f} MB")
    print(f"     Compressé: {'Oui' if backup['compressed'] else 'Non'}")
    print()
```

### 2.4 Nettoyer les Vieux Backups

```python
#!/usr/bin/env python3
"""
Exemple: Supprimer les backups de plus de 30 jours
"""
from src.infrastructure.backup import BackupManager

manager = BackupManager(backup_dir="/var/backups/compta")

# Supprimer backups > 30 jours
nb_supprime, espace_libere = manager.nettoyer_anciens_backups(nb_jours=30)

print(f"🗑️  {nb_supprime} backup(s) supprimé(s)")
print(f"💾 {espace_libere} MB libérés")
```

### 2.5 Restaurer un Backup

```python
#!/usr/bin/env python3
"""
Exemple: Restaurer une base de données depuis un backup
⚠️  ATTENTION: Cela écrase la base actuelle!
"""
from src.infrastructure.backup import BackupManager

manager = BackupManager(backup_dir="/var/backups/compta")

# Lister les backups
backups = manager.lister_backups()

if backups:
    # Prendre le plus récent
    backup_recent = backups[0]

    print(f"⚠️  Restauration de: {backup_recent['filename']}")
    confirmation = input("Êtes-vous SÛR? (tapez 'OUI'): ")

    if confirmation == "OUI":
        success, message = manager.restaurer_backup(backup_recent['filepath'])
        print(message)
    else:
        print("❌ Restauration annulée")
```

### 2.6 Planifier un Backup Quotidien (Cron)

```bash
# Créer le script de backup quotidien
cat > /usr/local/bin/backup-compta.sh << 'EOF'
#!/bin/bash
cd /home/bracoul/Bureau/comptabilite/compta/comptabilite-python
/usr/bin/python3 -c "
from src.infrastructure.backup import BackupManager
manager = BackupManager('/var/backups/compta')
success, msg = manager.creer_backup_automatique(max_backups=7)
print(msg)
" >> /var/log/compta-backup.log 2>&1
EOF

# Rendre exécutable
chmod +x /usr/local/bin/backup-compta.sh

# Ajouter au cron (tous les jours à 2h du matin)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-compta.sh") | crontab -
```

---

## 3. Lettrage des Comptes

### 3.1 Voir les Mouvements à Lettrer

```python
#!/usr/bin/env python3
"""
Exemple: Afficher les mouvements non lettrés d'un compte
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService

db = DatabaseManager()
service = ComptabiliteService(db)

# Récupérer les mouvements non lettrés du compte clients
mouvements = service.get_mouvements_a_lettrer(
    societe_id=1,
    exercice_id=1,
    compte_numero="411000",  # Compte clients
    tiers_id=None  # Tous les clients
)

print(f"📋 {len(mouvements)} mouvement(s) à lettrer:\n")

for mvt in mouvements:
    print(f"  ID: {mvt['mouvement_id']}")
    print(f"  Date: {mvt['date']}")
    print(f"  Écriture: {mvt['ecriture_numero']}")
    print(f"  Référence: {mvt['reference']}")
    print(f"  Débit: {mvt['debit']:.2f} €")
    print(f"  Crédit: {mvt['credit']:.2f} €")
    print(f"  Solde: {mvt['solde']:.2f} €")
    if mvt['tiers_nom']:
        print(f"  Tiers: {mvt['tiers_nom']}")
    print()

db.disconnect()
```

### 3.2 Lettrer des Mouvements Manuellement

```python
#!/usr/bin/env python3
"""
Exemple: Lettrer manuellement une facture avec son paiement
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService

db = DatabaseManager()
service = ComptabiliteService(db)

# IDs des mouvements à lettrer (facture + paiement)
mouvement_facture_id = 123
mouvement_paiement_id = 456

# Lettrer
success, message = service.lettrer_mouvements(
    mouvement_ids=[mouvement_facture_id, mouvement_paiement_id],
    code_lettrage="AA"  # Optionnel, généré auto sinon
)

print(message)

db.disconnect()
```

### 3.3 Lettrage Automatique

```python
#!/usr/bin/env python3
"""
Exemple: Lettrage automatique du compte clients
Trouve et lettre automatiquement les factures avec leurs paiements
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService

db = DatabaseManager()
service = ComptabiliteService(db)

# Lettrage automatique du compte 411000
nb_lettrages, message = service.lettrage_automatique(
    societe_id=1,
    exercice_id=1,
    compte_numero="411000",  # Clients
    tiers_id=None  # Tous les clients
)

print(message)
print(f"✅ {nb_lettrages} paire(s) lettrée(s) automatiquement")

db.disconnect()
```

### 3.4 Délettrer des Mouvements

```python
#!/usr/bin/env python3
"""
Exemple: Annuler un lettrage
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService

db = DatabaseManager()
service = ComptabiliteService(db)

# Délettrer le code "AA"
success, message = service.delettrer_mouvements(code_lettrage="AA")

print(message)

db.disconnect()
```

### 3.5 Voir les Mouvements Lettrés

```python
#!/usr/bin/env python3
"""
Exemple: Afficher tous les mouvements lettrés
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService

db = DatabaseManager()
service = ComptabiliteService(db)

# Récupérer les mouvements lettrés groupés par code
lettres = service.get_mouvements_lettres(
    societe_id=1,
    exercice_id=1,
    compte_numero="411000"
)

print(f"📌 {len(lettres)} groupe(s) de lettrage:\n")

for code, mouvements in lettres.items():
    print(f"  Code lettrage: {code}")
    print(f"  Nombre de mouvements: {len(mouvements)}")

    total_debit = sum(m['debit'] for m in mouvements)
    total_credit = sum(m['credit'] for m in mouvements)

    print(f"  Débit total: {total_debit:.2f} €")
    print(f"  Crédit total: {total_credit:.2f} €")
    print(f"  Équilibre: {'✅' if abs(total_debit - total_credit) < 0.01 else '❌'}")
    print()

db.disconnect()
```

---

## 4. Validation des Données

### 4.1 Valider un Montant

```python
from src.infrastructure.validation.validators import ComptabiliteValidator

# Valider un montant
result = ComptabiliteValidator.valider_montant(1234.56)

if result.is_valid:
    print("✅ Montant valide")
else:
    print(f"❌ Erreur: {result.message}")
```

### 4.2 Valider une Écriture Complète

```python
from datetime import date
from src.infrastructure.validation.validators import ComptabiliteValidator
from src.domain.models import Mouvement
from decimal import Decimal

# Exemple d'écriture
mouvements = [
    Mouvement(compte_id=1, debit=Decimal("1000"), credit=Decimal("0")),
    Mouvement(compte_id=2, debit=Decimal("0"), credit=Decimal("1000")),
]

result = ComptabiliteValidator.valider_ecriture_complete(
    mouvements=mouvements,
    date_ecriture=date(2025, 1, 15),
    exercice_debut=date(2025, 1, 1),
    exercice_fin=date(2025, 12, 31),
    reference="FACT-001",
    libelle="Test"
)

if result.is_valid:
    print("✅ Écriture valide")
else:
    print(f"❌ {result.message}")
```

### 4.3 Valider et Convertir

```python
from src.infrastructure.validation.validators import valider_et_convertir_montant

# Valider et convertir un montant
success, montant, erreur = valider_et_convertir_montant("1,234.56")

if success:
    print(f"✅ Montant converti: {montant}")  # Decimal
else:
    print(f"❌ Erreur: {erreur}")
```

---

## 5. Utilisation des Constantes

### 5.1 Numéros de Comptes

```python
from src.infrastructure.configuration.constants import ComptesComptables

# Au lieu de:
compte_client = "411000"  # ❌ Risque d'erreur de frappe

# Utilisez:
compte_client = ComptesComptables.CLIENTS  # ✅ Autocomplete + sûr

# Exemples
compte_vente = ComptesComptables.VENTES_MARCHANDISES  # 707000
compte_achat = ComptesComptables.ACHATS_FOURNITURES   # 606000
compte_banque = ComptesComptables.BANQUE              # 512000
compte_capital = ComptesComptables.CAPITAL_SOCIAL     # 101000
```

### 5.2 Taux de TVA

```python
from src.infrastructure.configuration.constants import TauxTVA

# Taux de TVA
tva_normale = TauxTVA.TAUX_NORMAL        # 0.20 (20%)
tva_reduite = TauxTVA.TAUX_REDUIT        # 0.055 (5.5%)
tva_intermediaire = TauxTVA.TAUX_INTERMEDIAIRE  # 0.10 (10%)

# Utilisation
montant_ht = Decimal("1000")
montant_tva = montant_ht * TauxTVA.TAUX_NORMAL  # 200
montant_ttc = montant_ht + montant_tva          # 1200
```

### 5.3 Fonctions Utilitaires

```python
from src.infrastructure.configuration.constants import (
    get_compte_tva_collectee,
    get_compte_tva_deductible,
    get_libelle_tva,
    TauxTVA
)

# Obtenir le bon compte de TVA
taux = TauxTVA.TAUX_NORMAL
compte_tva = get_compte_tva_collectee(taux)  # "445711" pour TVA 20%

# Générer le libellé
libelle = get_libelle_tva(taux, collectee=True)
print(libelle)  # "TVA collectée 20.0%"
```

---

## 6. Scripts Utiles

### 6.1 Script d'Export Complet

```python
#!/usr/bin/env python3
"""
Script: Exporter tous les rapports d'un exercice
"""
import sys
from datetime import datetime
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService
from src.utils.export_utils import ExportManager

def exporter_tout(societe_id, exercice_id, output_dir="/tmp/exports"):
    """Exporte tous les rapports"""

    db = DatabaseManager()
    service = ComptabiliteService(db)
    export_manager = ExportManager(output_dir)

    societe = service.get_societe(societe_id)
    exercice = service.exercice_dao.get_by_id(exercice_id)

    print(f"📊 Export complet - {societe.nom} - Exercice {exercice.annee}")
    print("=" * 60)

    # 1. Balance
    print("\n1️⃣  Export de la balance...")
    balance = service.get_balance(societe_id, exercice_id)
    success, path = export_manager.exporter_balance_excel(
        balance, societe.nom, exercice.annee
    )
    print(f"   {'✅' if success else '❌'} {path}")

    # 2. Compte de résultat
    print("\n2️⃣  Export du compte de résultat...")
    resultat = service.get_compte_resultat(societe_id, exercice_id)
    success, path = export_manager.exporter_compte_resultat_excel(
        resultat['charges'],
        resultat['produits'],
        resultat['total_charges'],
        resultat['total_produits'],
        resultat['resultat'],
        societe.nom,
        exercice.annee
    )
    print(f"   {'✅' if success else '❌'} {path}")

    # 3. Balance CSV
    print("\n3️⃣  Export CSV de la balance...")
    success, path = export_manager.exporter_balance_csv(balance)
    print(f"   {'✅' if success else '❌'} {path}")

    db.disconnect()

    print("\n" + "=" * 60)
    print(f"✅ Export terminé - Fichiers dans: {output_dir}")

if __name__ == "__main__":
    societe_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    exercice_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    exporter_tout(societe_id, exercice_id)
```

**Utilisation**:
```bash
python scripts/export_complet.py 1 1
```

### 6.2 Script de Backup Quotidien

```python
#!/usr/bin/env python3
"""
Script: Backup quotidien avec rotation
À exécuter via cron tous les jours
"""
import sys
from datetime import datetime
from src.infrastructure.backup import BackupManager

def backup_quotidien(backup_dir="/var/backups/compta", max_backups=7):
    """Crée un backup et nettoie les anciens"""

    print(f"📦 Backup quotidien - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    manager = BackupManager(backup_dir)

    # Créer backup avec rotation
    success, message = manager.creer_backup_automatique(
        max_backups=max_backups,
        compress=True
    )

    print(message)

    # Lister les backups
    backups = manager.lister_backups()
    print(f"\n📋 {len(backups)} backup(s) conservé(s)")

    return 0 if success else 1

if __name__ == "__main__":
    backup_dir = sys.argv[1] if len(sys.argv) > 1 else "/var/backups/compta"
    sys.exit(backup_quotidien(backup_dir))
```

**Utilisation**:
```bash
python scripts/backup_quotidien.py /var/backups/compta
```

### 6.3 Script de Lettrage Automatique

```python
#!/usr/bin/env python3
"""
Script: Lettrage automatique de tous les comptes lettrables
"""
from src.infrastructure.persistence.database import DatabaseManager
from src.application.services import ComptabiliteService

def lettrage_auto_complet(societe_id, exercice_id):
    """Lettre automatiquement tous les comptes lettrables"""

    db = DatabaseManager()
    service = ComptabiliteService(db)

    # Comptes à lettrer
    comptes_lettrables = [
        ("411000", "Clients"),
        ("401000", "Fournisseurs"),
    ]

    print("🔗 Lettrage automatique")
    print("=" * 60)

    total_lettrages = 0

    for compte, nom in comptes_lettrables:
        print(f"\n📌 {nom} ({compte})")

        nb, msg = service.lettrage_automatique(
            societe_id, exercice_id, compte
        )

        print(f"   {msg}")
        total_lettrages += nb

    print("\n" + "=" * 60)
    print(f"✅ Total: {total_lettrages} lettrage(s) effectué(s)")

    db.disconnect()

if __name__ == "__main__":
    lettrage_auto_complet(1, 1)
```

**Utilisation**:
```bash
python scripts/lettrage_auto.py
```

---

## 📝 Prochaines étapes

### Sauvegarder ces scripts

```bash
# Créer les scripts dans le dossier scripts/
cd scripts/

# Créer export_complet.py
# Créer backup_quotidien.py
# Créer lettrage_auto.py

# Rendre exécutables
chmod +x *.py
```

### Tester chaque fonctionnalité

1. **Export Excel**
   ```bash
   python -c "from src.utils.export_utils import ExportManager; ..."
   ```

2. **Backup**
   ```bash
   python scripts/backup_quotidien.py
   ```

3. **Lettrage**
   ```bash
   python scripts/lettrage_auto.py
   ```

---

**Guide créé le**: 23 Novembre 2024
**Version**: 2.0
**Pour toute question**, consulter la documentation complète dans `docs/`
