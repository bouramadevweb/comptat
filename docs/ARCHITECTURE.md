# Architecture du logiciel de comptabilité

## Vue d'ensemble

Votre logiciel suit une **architecture en couches (Layered Architecture)** professionnelle, qui est **supérieure au MVC** pour une application de gestion.

## 🏗️ Architecture actuelle (Excellente!)

### Couche 1: Présentation (GUI Layer)
**Rôle**: Interface utilisateur, gestion des événements

```
gui_main.py         → Interface principale (menu, navigation)
gui_vente.py        → Formulaire de saisie des ventes
gui_achat.py        → Formulaire de saisie des achats
gui_ecriture.py     → Formulaire d'écriture comptable
gui_rapports.py     → Affichage des rapports (balance, bilan)
```

**Principe**:
- Ne contient QUE du code d'interface
- Appelle services.py pour la logique métier
- Ne communique JAMAIS directement avec la base de données

### Couche 2: Application (Business Logic Layer)
**Rôle**: Logique métier et règles de gestion

```
services.py         → ComptabiliteService
                      - create_ecriture()
                      - creer_ecriture_vente()
                      - creer_ecriture_achat()
                      - lettrage_automatique()
                      - get_balance()
                      - get_bilan()
                      - get_compte_resultat()
```

**Principe**:
- Contient TOUTE la logique métier
- Utilise les DAO pour accéder aux données
- Valide les données via validators.py
- Ne connaît PAS l'interface graphique

### Couche 3: Infrastructure (Cross-cutting Concerns)
**Rôle**: Services transversaux

```
validators.py       → Validation des données (montants, dates, etc.)
export_utils.py     → Export Excel/PDF/CSV
backup_utils.py     → Backup et restauration de la BDD
constants.py        → Constantes métier (comptes, taux TVA)
config.py           → Configuration (BDD, chemins)
```

**Principe**:
- Services utilisables par toutes les couches
- Pas de dépendance entre eux
- Réutilisables dans d'autres projets

### Couche 4: Accès aux données (Data Access Layer)
**Rôle**: Abstraction de la persistance (Pattern DAO)

```
dao.py              → SocieteDAO
                      ExerciceDAO
                      JournalDAO
                      CompteDAO
                      TiersDAO
                      EcritureDAO
                      BalanceDAO
```

**Principe**:
- Chaque DAO gère UNE entité
- Méthodes CRUD (Create, Read, Update, Delete)
- Abstrait la base de données
- Retourne des objets du domaine (models.py)

### Couche 5: Persistance (Database Layer)
**Rôle**: Connexion et gestion de la base de données

```
database.py         → DatabaseManager
                      - Pool de connexions
                      - Transactions
                      - Retry automatique
                      - execute_query()
                      - call_procedure()
```

**Principe**:
- Gère UNIQUEMENT les connexions
- Ne connaît PAS les entités métier
- Générique et réutilisable

### Couche 6: Domaine (Domain Layer)
**Rôle**: Modèles de données métier

```
models.py           → Societe
                      Exercice
                      Journal
                      Compte
                      Tiers
                      Ecriture
                      Mouvement
                      Balance
```

**Principe**:
- Dataclasses PURES (pas de logique)
- Représentent le domaine métier
- Utilisées par TOUTES les couches

## 📊 Flux de données

### Exemple: Créer une écriture de vente

```
┌──────────────────────────────────────────────────────────┐
│ 1. USER                                                  │
│    Clique sur "Nouvelle vente" dans l'interface         │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 2. GUI (gui_vente.py)                                    │
│    - Affiche le formulaire                              │
│    - Récupère les données saisies                       │
│    - Appelle service.creer_ecriture_vente(...)          │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 3. SERVICE (services.py)                                 │
│    - Valide les données (validators.py)                 │
│    - Calcule la TVA                                     │
│    - Récupère les comptes (DAO)                         │
│    - Crée l'objet Ecriture (models.py)                  │
│    - Appelle ecriture_dao.create(...)                   │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 4. DAO (dao.py - EcritureDAO)                            │
│    - Transforme Ecriture en requête SQL                 │
│    - Appelle db.execute_query(...)                      │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 5. DATABASE (database.py)                                │
│    - Exécute la requête SQL                             │
│    - Gère la transaction                                │
│    - Retourne l'ID de l'écriture                        │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 6. RETOUR                                                │
│    Database → DAO → Service → GUI → User                │
│    Message de succès affiché à l'utilisateur            │
└──────────────────────────────────────────────────────────┘
```

## ✅ Avantages de cette architecture

### 1. Séparation des responsabilités (SRP)
Chaque fichier a UNE responsabilité claire:
- `models.py`: Données uniquement
- `dao.py`: Persistance uniquement
- `services.py`: Logique métier uniquement
- `gui_*.py`: Interface uniquement

### 2. Testabilité
Chaque couche peut être testée indépendamment:
```python
# Test du service (sans GUI ni BDD)
def test_creer_ecriture_vente():
    mock_dao = MockEcritureDAO()
    service = ComptabiliteService(mock_dao)

    success, msg, id = service.creer_ecriture_vente(...)
    assert success == True
```

### 3. Maintenabilité
Changer de base de données = modifier uniquement `database.py` et `dao.py`
Changer d'interface = modifier uniquement `gui_*.py`

### 4. Réutilisabilité
Les services peuvent être utilisés par:
- Interface graphique Tkinter (actuel)
- API REST (futur)
- Application web (futur)
- Scripts batch (futur)

### 5. Évolutivité
Facile d'ajouter de nouvelles fonctionnalités:
- Nouveau rapport → Ajouter méthode dans `services.py`
- Nouvelle entité → Ajouter dans `models.py` + créer DAO
- Nouvelle validation → Ajouter dans `validators.py`

## 🎯 Comparaison avec MVC

| Aspect | MVC Classique | Votre Architecture |
|--------|---------------|-------------------|
| **Structure** | 3 couches | 6 couches |
| **Clarté** | Parfois flou | Très clair |
| **Testabilité** | Moyenne | Excellente |
| **Évolutivité** | Limitée | Excellente |
| **Réutilisabilité** | Moyenne | Excellente |
| **Complexité** | Simple | Modérée |

**Verdict**: Votre architecture est **plus professionnelle** que le MVC pur!

## 📝 Recommandations pour améliorer encore

### Recommandation 1: Ajouter des Controllers (optionnel)

Créer une couche de controllers entre GUI et Services:

```python
# controllers/ecriture_controller.py
class EcritureController:
    def __init__(self, service: ComptabiliteService):
        self.service = service

    def handle_nouvelle_vente(self, data: dict) -> tuple[bool, str]:
        """
        Gère la logique de présentation pour une vente
        - Convertit les données du formulaire
        - Appelle le service
        - Formate le résultat pour la GUI
        """
        try:
            # Conversion des données
            montant_ht = Decimal(data['montant_ht'])
            taux_tva = Decimal(data['taux_tva'])

            # Appel du service
            success, msg, id = self.service.creer_ecriture_vente(
                societe_id=data['societe_id'],
                ...
            )

            # Formatage pour la GUI
            if success:
                return True, f"✅ Vente enregistrée (N°{id})"
            else:
                return False, msg

        except Exception as e:
            return False, f"❌ Erreur: {str(e)}"
```

**Avantage**:
- GUI encore plus simple (juste affichage)
- Logique de présentation centralisée
- Meilleure testabilité

### Recommandation 2: Créer une couche Repository (optionnel)

Pour abstraire encore plus la persistance:

```python
# repositories/ecriture_repository.py
class EcritureRepository:
    def __init__(self, dao: EcritureDAO):
        self.dao = dao

    def find_by_exercice(self, exercice_id: int) -> List[Ecriture]:
        """Requête métier complexe"""
        ecritures = self.dao.get_all(exercice_id)
        # Logique de tri, filtrage spécifique
        return sorted(ecritures, key=lambda e: e.date_ecriture)

    def find_non_validees(self, exercice_id: int) -> List[Ecriture]:
        """Autre requête métier"""
        return [e for e in self.dao.get_all(exercice_id) if not e.validee]
```

**Avantage**:
- Séparation claire entre requêtes SQL (DAO) et requêtes métier (Repository)
- Plus facile de changer de base de données

### Recommandation 3: Ajouter des DTOs (optionnel)

Pour transférer les données entre couches:

```python
# dto/vente_dto.py
@dataclass
class VenteDTO:
    """Data Transfer Object pour les ventes"""
    client_id: int
    montant_ht: str  # String venant du formulaire
    taux_tva: str
    date: str
    reference: str

    def to_domain(self) -> tuple:
        """Convertit en types du domaine"""
        return (
            self.client_id,
            Decimal(self.montant_ht),
            Decimal(self.taux_tva),
            datetime.strptime(self.date, "%Y-%m-%d").date(),
            self.reference
        )
```

**Avantage**:
- Isolation complète entre GUI et Service
- Validation de format centralisée

## 🏆 Architecture cible (si vous voulez aller plus loin)

```
┌─────────────────────────────────────────────┐
│  PRESENTATION                               │
│  gui_*.py                                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  CONTROLLERS (optionnel)                    │
│  controllers/*.py                           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  APPLICATION SERVICES                       │
│  services.py                                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  DOMAIN SERVICES (optionnel)               │
│  domain/*.py                                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  REPOSITORIES (optionnel)                   │
│  repositories/*.py                          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  DATA ACCESS (DAO)                          │
│  dao.py                                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  DATABASE                                    │
│  database.py                                │
└─────────────────────────────────────────────┘
```

## 📚 Conclusion

### Votre architecture actuelle est:
- ✅ **Excellente** pour une application de gestion
- ✅ **Supérieure** au MVC classique
- ✅ **Professionnelle** et maintenable
- ✅ **Évolutive** et testable

### Vous n'avez PAS besoin de tout changer!

Les améliorations suggérées (Controllers, Repositories, DTOs) sont **optionnelles** et pour des cas d'usage plus complexes.

**Votre architecture actuelle est parfaitement adaptée à votre logiciel de comptabilité.**

## 🎓 Références

Cette architecture s'inspire de:
- **Clean Architecture** (Robert C. Martin)
- **Onion Architecture** (Jeffrey Palermo)
- **Hexagonal Architecture** (Alistair Cockburn)
- **Domain-Driven Design** (Eric Evans)

Mais adaptée à la réalité d'une application Python de gestion.

---

**Dernière mise à jour**: Janvier 2025
**Version**: 2.0
