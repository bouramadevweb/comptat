# 🔐 Guide d'Authentification et d'Autorisation

**Version**: 3.0 - Système sécurisé multi-utilisateurs
**Date**: 23 novembre 2025
**Statut**: ✅ Production Ready

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Rôles et Permissions](#r%C3%B4les-et-permissions)
7. [Audit Trail](#audit-trail)
8. [Sécurité](#s%C3%A9curit%C3%A9)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Vue d'ensemble

Le système d'authentification et d'autorisation offre :

- ✅ **Authentification JWT** (JSON Web Tokens)
- ✅ **Gestion des rôles** (ADMIN, COMPTABLE, LECTEUR)
- ✅ **Permissions granulaires**
- ✅ **Sessions sécurisées**
- ✅ **Audit trail complet**
- ✅ **Protection contre les attaques**
- ✅ **Hashage bcrypt** des mots de passe

---

## 🏗️ Architecture

### Composants Principaux

```
src/infrastructure/security/
├── auth_service.py        # Service d'authentification JWT
├── audit_service.py       # Service de journalisation d'audit
├── decorators.py          # Décorateurs pour permissions
└── __init__.py

src/domain/models.py
└── User, Role, Session, AuditLog  # Modèles de données

sql/02_authentication_authorization.sql  # Schéma base de données
```

### Modèles de Données

```python
@dataclass
class Role:
    code: str                  # ADMIN, COMPTABLE, LECTEUR
    nom: str
    peut_creer: bool
    peut_modifier: bool
    peut_supprimer: bool
    peut_valider: bool
    peut_cloturer: bool
    peut_gerer_users: bool

@dataclass
class User:
    username: str
    email: str
    password_hash: str         # Hash bcrypt
    role: Role
    actif: bool
    compte_bloque: bool
    tentatives_connexion: int

@dataclass
class Session:
    user_id: int
    token: str                 # JWT token
    date_expiration: datetime
    revoked: bool

@dataclass
class AuditLog:
    user_id: int
    username: str
    action: str               # CREATE, UPDATE, DELETE, VALIDATE, etc.
    entity_type: str          # ECRITURE, USER, EXERCICE, etc.
    entity_id: int
    details: dict             # JSON avec détails
    date_action: datetime
    success: bool
```

---

## 📦 Installation

### 1. Installer les Dépendances

```bash
pip install PyJWT bcrypt
```

### 2. Créer les Tables

```bash
mysql -u root -p Comptabilite < sql/02_authentication_authorization.sql
```

### 3. Vérifier l'Installation

```python
from src.infrastructure.security import AuthenticationService
from src.infrastructure.database.database_manager import DatabaseManager

db = DatabaseManager()
auth_service = AuthenticationService(db)

# Tester avec l'utilisateur admin par défaut
success, message, token, user = auth_service.authenticate(
    username='admin',
    password='admin123'  # ⚠️ À changer en production!
)

if success:
    print(f"✅ Authentification réussie: {user.username}")
    print(f"Token JWT: {token[:50]}...")
else:
    print(f"❌ Échec: {message}")
```

---

## ⚙️ Configuration

### Variables d'Environnement

Créer/modifier `.env` :

```bash
# JWT Configuration
JWT_SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire-256-bits
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Sécurité
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30

# Audit
AUDIT_LOG_RETENTION_DAYS=365
```

### Générer une Clé JWT Sécurisée

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={secret_key}")
```

Ou en bash:
```bash
python3 -c "import secrets; print(f'JWT_SECRET_KEY={secrets.token_urlsafe(32)}')"
```

---

## 💻 Utilisation

### 1. Authentification

```python
from src.infrastructure.security import AuthenticationService
from src.infrastructure.database.database_manager import DatabaseManager

# Initialiser le service
db = DatabaseManager()
auth_service = AuthenticationService(db)

# Se connecter
success, message, token, user = auth_service.authenticate(
    username='admin',
    password='admin123',
    ip_address='192.168.1.100',
    user_agent='Mozilla/5.0...'
)

if success:
    print(f"✅ Connecté: {user.username}")
    print(f"Rôle: {user.role.code}")
    print(f"Token: {token}")

    # Utiliser le token pour les requêtes suivantes
    current_user_token = token
else:
    print(f"❌ Erreur: {message}")
```

### 2. Vérifier un Token

```python
# Décoder et vérifier un token JWT
payload = auth_service.decode_token(token)

if payload:
    user_id = payload['sub']
    username = payload['username']
    role_code = payload['role_code']
    print(f"✅ Token valide pour {username} (ID: {user_id})")
else:
    print("❌ Token invalide ou expiré")
```

### 3. Déconnexion

```python
success, message = auth_service.logout(
    token=current_user_token,
    user_id=user.id,
    username=user.username,
    ip_address='192.168.1.100'
)

print(message)  # "✅ Déconnexion réussie"
```

### 4. Créer un Utilisateur

```python
success, message, user_id = auth_service.create_user(
    username='jean.dupont',
    email='jean.dupont@example.com',
    password='MotDePasseSecurise123!',
    nom='Dupont',
    prenom='Jean',
    role_code='COMPTABLE'
)

if success:
    print(f"✅ Utilisateur créé (ID: {user_id})")
else:
    print(f"❌ Erreur: {message}")
```

### 5. Changer de Mot de Passe

```python
success, message = auth_service.change_password(
    user_id=user.id,
    old_password='ancien_mot_de_passe',
    new_password='nouveau_mot_de_passe_securise'
)

print(message)
```

---

## 👥 Rôles et Permissions

### Rôles Prédéfinis

| Rôle | Code | Permissions |
|------|------|-------------|
| **Administrateur** | `ADMIN` | ✅ Toutes les permissions |
| **Comptable** | `COMPTABLE` | ✅ Créer, Modifier, Valider écritures |
| **Lecteur** | `LECTEUR` | 👁️  Lecture seule (consultation) |

### Matrice des Permissions

| Permission | ADMIN | COMPTABLE | LECTEUR |
|-----------|-------|-----------|---------|
| `peut_creer` | ✅ | ✅ | ❌ |
| `peut_modifier` | ✅ | ✅ | ❌ |
| `peut_supprimer` | ✅ | ❌ | ❌ |
| `peut_valider` | ✅ | ✅ | ❌ |
| `peut_cloturer` | ✅ | ❌ | ❌ |
| `peut_gerer_users` | ✅ | ❌ | ❌ |

### Utiliser les Décorateurs

```python
from src.infrastructure.security.decorators import (
    require_create_permission,
    require_admin_role,
    audit_action,
    require_active_exercice
)

class ComptabiliteService:
    def __init__(self, audit_service):
        self.audit_service = audit_service

    @require_create_permission()
    @require_active_exercice()
    @audit_action('CREATE', 'ECRITURE')
    def create_ecriture(
        self,
        user: User,          # Utilisateur authentifié
        exercice: Exercice,
        ecriture: Ecriture
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Crée une écriture
        - Vérifie que l'utilisateur a la permission 'peut_creer'
        - Vérifie que l'exercice n'est pas clôturé
        - Enregistre automatiquement l'action dans l'audit
        """
        ecriture_id = self.dao.create(ecriture)
        return True, "✅ Écriture créée", ecriture_id

    @require_admin_role()
    @audit_action('DELETE', 'USER')
    def delete_user(
        self,
        user: User,           # Doit être ADMIN
        target_user_id: int
    ) -> Tuple[bool, str]:
        """Seuls les ADMIN peuvent supprimer des utilisateurs"""
        self.dao.delete(target_user_id)
        return True, "✅ Utilisateur supprimé"
```

### Gestion Manuelle des Permissions

```python
# Vérifier une permission spécifique
if user.role.peut_valider:
    # Valider l'écriture
    ecriture.validee = True
else:
    return False, "❌ Permission requise: peut_valider"

# Vérifier le rôle
if user.role.code == 'ADMIN':
    # Actions administrateur
    pass
```

---

## 📝 Audit Trail

### Service d'Audit

```python
from src.infrastructure.security.audit_service import AuditService

audit_service = AuditService(db)
```

### Logger une Action

```python
# Log manuel
audit_id = audit_service.log_action(
    user_id=user.id,
    username=user.username,
    action='CREATE',
    entity_type='ECRITURE',
    entity_id=ecriture_id,
    details={
        'numero': 'VE001',
        'montant_total': '1200.00'
    },
    ip_address='192.168.1.100',
    success=True
)
```

### Méthodes Spécialisées

```python
# Écriture créée
audit_service.log_ecriture_created(
    user_id=user.id,
    username=user.username,
    ecriture_id=ecriture_id,
    numero='VE001',
    montant_total=Decimal('1200.00'),
    ip_address='192.168.1.100'
)

# Écriture validée
audit_service.log_ecriture_validated(...)

# Exercice clôturé
audit_service.log_exercice_closed(...)

# Lettrage
audit_service.log_lettrage(...)

# Export FEC
audit_service.log_export_fec(...)

# Permission refusée
audit_service.log_permission_denied(...)
```

### Consulter les Logs

```python
from datetime import date, timedelta

# Logs des 7 derniers jours
logs = audit_service.get_audit_logs(
    start_date=date.today() - timedelta(days=7),
    end_date=date.today(),
    limit=100
)

for log in logs:
    print(f"{log.date_action} - {log.username} - {log.action} {log.entity_type}")

# Activité d'un utilisateur
activity = audit_service.get_user_activity(
    user_id=5,
    days=30
)

print(f"Actions totales: {activity['summary']['total_actions']}")
print(f"Taux de succès: {activity['summary']['success_rate']}%")

# Historique d'une entité
history = audit_service.get_entity_history(
    entity_type='ECRITURE',
    entity_id=123
)

print(f"Historique de l'écriture #123:")
for log in history:
    print(f"  {log.date_action} - {log.action} par {log.username}")
```

### Nettoyage des Anciens Logs

```python
# Supprimer les logs de plus d'1 an
deleted_count = audit_service.clean_old_logs(days_to_keep=365)
print(f"✅ {deleted_count} logs archivés")
```

---

## 🛡️ Sécurité

### Mots de Passe

- **Hashage**: bcrypt avec salt automatique
- **Vérification**: Résistant au timing attack
- **Stockage**: Jamais en clair, uniquement le hash

```python
# Hasher un mot de passe
password_hash = auth_service.hash_password('mon_mot_de_passe')

# Vérifier un mot de passe
is_valid = auth_service.verify_password('mon_mot_de_passe', password_hash)
```

### Protection contre les Attaques

#### 1. Brute Force
- Max 5 tentatives de connexion
- Blocage automatique du compte après
- Déblocage manuel requis

#### 2. Token JWT
- Signature HMAC-SHA256
- Expiration après 1h (configurable)
- Révocation possible via la base de données

#### 3. Sessions
- Tracking des sessions actives
- Révocation possible (logout)
- Nettoyage automatique des sessions expirées

### Procédures de Sécurité

```sql
-- Nettoyer les sessions expirées
CALL CleanExpiredSessions();

-- Révoquer toutes les sessions d'un utilisateur
CALL RevokeUserSessions(5);

-- Bloquer un utilisateur après trop de tentatives
CALL BlockUserAfterFailedAttempts('username', 5);
```

### Bonnes Pratiques

1. **Ne jamais commit la JWT_SECRET_KEY** dans Git
2. **Changer le mot de passe admin par défaut**
3. **Utiliser HTTPS en production**
4. **Activer les logs d'audit**
5. **Faire des backups réguliers de AUDIT_LOG**
6. **Nettoyer les anciennes sessions régulièrement**

---

## 📚 API Reference

### AuthenticationService

#### `authenticate(username, password, ip_address, user_agent)`
Authentifie un utilisateur et crée une session.

**Returns**: `(success: bool, message: str, token: str, user: User)`

#### `logout(token, user_id, username, ip_address)`
Déconnecte un utilisateur et révoque son token.

**Returns**: `(success: bool, message: str)`

#### `create_user(username, email, password, nom, prenom, role_code)`
Crée un nouvel utilisateur.

**Returns**: `(success: bool, message: str, user_id: int)`

#### `change_password(user_id, old_password, new_password)`
Change le mot de passe d'un utilisateur.

**Returns**: `(success: bool, message: str)`

#### `create_access_token(user, expires_delta)`
Crée un token JWT pour un utilisateur.

**Returns**: `str` (JWT token)

#### `decode_token(token)`
Décode et vérifie un token JWT.

**Returns**: `dict` (payload) ou `None`

### AuditService

#### `log_action(user_id, username, action, entity_type, entity_id, details, ip_address, success, error_message)`
Enregistre une action dans l'audit.

**Returns**: `int` (audit_id)

#### `get_audit_logs(user_id, action, entity_type, start_date, end_date, limit, offset)`
Récupère les logs d'audit avec filtres.

**Returns**: `List[AuditLog]`

#### `get_user_activity(user_id, days)`
Obtient les statistiques d'activité d'un utilisateur.

**Returns**: `dict` (summary + actions)

#### `get_entity_history(entity_type, entity_id)`
Obtient l'historique complet d'une entité.

**Returns**: `List[AuditLog]`

---

## 🔧 Troubleshooting

### Problème: Token expiré

```
Erreur: "Token expiré"
```

**Solution**: Re-authentifier l'utilisateur ou augmenter `ACCESS_TOKEN_EXPIRE_MINUTES`

### Problème: Compte bloqué

```
Erreur: "Compte bloqué suite à trop de tentatives"
```

**Solution**: Débloquer manuellement en base de données:
```sql
UPDATE USERS SET compte_bloque = FALSE, tentatives_connexion = 0 WHERE username = 'username';
```

### Problème: Permission refusée

```
Erreur: "Permission 'peut_creer' requise (rôle actuel: LECTEUR)"
```

**Solution**: Attribuer le bon rôle à l'utilisateur ou créer un rôle custom avec les permissions requises

### Problème: Sessions multiples

```
Question: Comment limiter à une seule session par utilisateur?
```

**Solution**:
```python
# Avant de créer une nouvelle session, révoquer les anciennes
auth_service.db.call_procedure('RevokeUserSessions', (user.id,))
# Puis créer la nouvelle session
```

---

## 📞 Support

Pour toute question ou problème:

1. Consulter les logs: `logs/comptabilite.log`
2. Vérifier la base de données: `SELECT * FROM AUDIT_LOG ORDER BY date_action DESC LIMIT 100;`
3. Consulter `ROADMAP_PRO.md` pour le planning d'évolutions

---

*Guide créé le 23 novembre 2025*
*Version: 3.0 - Système sécurisé multi-utilisateurs* ✅
