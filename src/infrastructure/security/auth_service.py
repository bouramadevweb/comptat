"""
Service d'authentification et de gestion des sessions
Utilise JWT pour les tokens et bcrypt pour les mots de passe
"""
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from dataclasses import asdict

from src.domain.models import User, Role, Session, AuditLog
from src.infrastructure.configuration.config import Settings

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service d'authentification avec JWT"""

    def __init__(self, db_manager, secret_key: Optional[str] = None):
        """
        Initialize authentication service
        Args:
            db_manager: DatabaseManager instance
            secret_key: Clé secrète pour signer les JWT (par défaut depuis config)
        """
        self.db = db_manager
        self.secret_key = secret_key or Settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60  # 1 heure
        self.max_login_attempts = 5

    # ==================== GESTION DES MOTS DE PASSE ====================

    def hash_password(self, password: str) -> str:
        """
        Hash un mot de passe avec bcrypt
        Args:
            password: Mot de passe en clair
        Returns:
            Hash bcrypt du mot de passe
        """
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Vérifie un mot de passe contre son hash
        Args:
            password: Mot de passe en clair
            password_hash: Hash bcrypt à vérifier
        Returns:
            True si le mot de passe correspond
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erreur vérification mot de passe: {e}")
            return False

    # ==================== GÉNÉRATION DE TOKENS ====================

    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crée un token JWT pour un utilisateur
        Args:
            user: Utilisateur pour qui créer le token
            expires_delta: Durée de validité (défaut: 1h)
        Returns:
            Token JWT signé
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role_id": user.role_id,
            "role_code": user.role.code if user.role else None,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict]:
        """
        Décode et vérifie un token JWT
        Args:
            token: Token JWT à décoder
        Returns:
            Payload du token ou None si invalide
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expiré")
            return None
        except jwt.JWTError as e:
            logger.error(f"Erreur décodage token: {e}")
            return None

    # ==================== AUTHENTIFICATION ====================

    def authenticate(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str], Optional[User]]:
        """
        Authentifie un utilisateur
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            ip_address: Adresse IP du client
            user_agent: User-Agent du client
        Returns:
            (success, message, token, user)
        """
        try:
            # Récupérer l'utilisateur
            user = self._get_user_by_username(username)

            if not user:
                self._log_failed_login(username, "Utilisateur inconnu", ip_address)
                return False, "❌ Identifiants incorrects", None, None

            # Vérifier si le compte est actif
            if not user.actif:
                self._log_failed_login(username, "Compte désactivé", ip_address)
                return False, "❌ Compte désactivé", None, None

            # Vérifier si le compte est bloqué
            if user.compte_bloque:
                self._log_failed_login(username, "Compte bloqué", ip_address)
                return False, "❌ Compte bloqué suite à trop de tentatives", None, None

            # Vérifier le mot de passe
            if not self.verify_password(password, user.password_hash):
                self._increment_failed_attempts(user.id, username, ip_address)
                return False, "❌ Identifiants incorrects", None, None

            # Réinitialiser les tentatives de connexion
            self._reset_failed_attempts(user.id)

            # Créer le token JWT
            token = self.create_access_token(user)

            # Créer la session en base de données
            session_id = self._create_session(user.id, token, ip_address, user_agent)

            # Mettre à jour la dernière connexion
            self._update_last_login(user.id)

            # Logger la connexion réussie
            self._log_successful_login(user.id, username, ip_address)

            logger.info(f"✅ Connexion réussie pour {username}")
            return True, "✅ Connexion réussie", token, user

        except Exception as e:
            logger.error(f"Erreur authentification: {e}", exc_info=True)
            return False, f"❌ Erreur serveur: {str(e)}", None, None

    def logout(
        self,
        token: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Déconnecte un utilisateur (révoque le token)
        Args:
            token: Token JWT à révoquer
            user_id: ID de l'utilisateur (optionnel)
            username: Nom d'utilisateur (pour log)
            ip_address: Adresse IP
        Returns:
            (success, message)
        """
        try:
            # Révoquer la session
            self._revoke_session(token)

            # Logger la déconnexion
            if user_id:
                self._log_logout(user_id, username or "", ip_address)

            return True, "✅ Déconnexion réussie"

        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
            return False, f"❌ Erreur: {str(e)}"

    # ==================== GESTION DES UTILISATEURS ====================

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        nom: str,
        prenom: str,
        role_code: str
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Crée un nouvel utilisateur
        Args:
            username: Nom d'utilisateur unique
            email: Email unique
            password: Mot de passe (sera hashé)
            nom: Nom de famille
            prenom: Prénom
            role_code: Code du rôle (ADMIN, COMPTABLE, LECTEUR)
        Returns:
            (success, message, user_id)
        """
        try:
            # Vérifier que l'username est disponible
            if self._get_user_by_username(username):
                return False, "❌ Nom d'utilisateur déjà utilisé", None

            # Vérifier que l'email est disponible
            if self._get_user_by_email(email):
                return False, "❌ Email déjà utilisé", None

            # Récupérer le rôle
            role = self._get_role_by_code(role_code)
            if not role:
                return False, f"❌ Rôle {role_code} introuvable", None

            # Hasher le mot de passe
            password_hash = self.hash_password(password)

            # Créer l'utilisateur
            query = """
                INSERT INTO USERS (username, email, password_hash, nom, prenom, role_id, actif)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """

            with self.db.get_cursor() as cursor:
                cursor.execute(query, (username, email, password_hash, nom, prenom, role.id))
                user_id = cursor.lastrowid

            logger.info(f"✅ Utilisateur {username} créé avec succès (ID: {user_id})")
            return True, f"✅ Utilisateur créé avec succès", user_id

        except Exception as e:
            logger.error(f"Erreur création utilisateur: {e}", exc_info=True)
            return False, f"❌ Erreur: {str(e)}", None

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change le mot de passe d'un utilisateur
        Args:
            user_id: ID de l'utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
        Returns:
            (success, message)
        """
        try:
            # Récupérer l'utilisateur
            user = self._get_user_by_id(user_id)
            if not user:
                return False, "❌ Utilisateur introuvable"

            # Vérifier l'ancien mot de passe
            if not self.verify_password(old_password, user.password_hash):
                return False, "❌ Ancien mot de passe incorrect"

            # Hasher le nouveau mot de passe
            new_password_hash = self.hash_password(new_password)

            # Mettre à jour
            query = "UPDATE USERS SET password_hash = %s WHERE id = %s"
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (new_password_hash, user_id))

            # Révoquer toutes les sessions existantes
            self.db.call_procedure('RevokeUserSessions', (user_id,))

            logger.info(f"✅ Mot de passe changé pour user ID {user_id}")
            return True, "✅ Mot de passe changé avec succès"

        except Exception as e:
            logger.error(f"Erreur changement mot de passe: {e}")
            return False, f"❌ Erreur: {str(e)}"

    # ==================== MÉTHODES PRIVÉES ====================

    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par son username"""
        query = """
            SELECT u.*, r.code as role_code, r.nom as role_nom,
                   r.peut_creer, r.peut_modifier, r.peut_supprimer,
                   r.peut_valider, r.peut_cloturer, r.peut_gerer_users
            FROM USERS u
            INNER JOIN ROLES r ON u.role_id = r.id
            WHERE u.username = %s
        """
        results = self.db.execute_query(query, (username,))
        if not results:
            return None

        row = results[0]
        role = Role(
            id=row['role_id'],
            code=row['role_code'],
            nom=row['role_nom'],
            peut_creer=bool(row['peut_creer']),
            peut_modifier=bool(row['peut_modifier']),
            peut_supprimer=bool(row['peut_supprimer']),
            peut_valider=bool(row['peut_valider']),
            peut_cloturer=bool(row['peut_cloturer']),
            peut_gerer_users=bool(row['peut_gerer_users'])
        )

        user = User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            nom=row['nom'],
            prenom=row['prenom'],
            role_id=row['role_id'],
            role=role,
            actif=bool(row['actif']),
            date_creation=row['date_creation'],
            date_derniere_connexion=row['date_derniere_connexion'],
            tentatives_connexion=row['tentatives_connexion'],
            compte_bloque=bool(row['compte_bloque'])
        )

        return user

    def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        query = """
            SELECT u.*, r.code as role_code, r.nom as role_nom,
                   r.peut_creer, r.peut_modifier, r.peut_supprimer,
                   r.peut_valider, r.peut_cloturer, r.peut_gerer_users
            FROM USERS u
            INNER JOIN ROLES r ON u.role_id = r.id
            WHERE u.id = %s
        """
        results = self.db.execute_query(query, (user_id,))
        if not results:
            return None

        row = results[0]
        role = Role(
            id=row['role_id'],
            code=row['role_code'],
            nom=row['role_nom'],
            peut_creer=bool(row['peut_creer']),
            peut_modifier=bool(row['peut_modifier']),
            peut_supprimer=bool(row['peut_supprimer']),
            peut_valider=bool(row['peut_valider']),
            peut_cloturer=bool(row['peut_cloturer']),
            peut_gerer_users=bool(row['peut_gerer_users'])
        )

        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            nom=row['nom'],
            prenom=row['prenom'],
            role_id=row['role_id'],
            role=role,
            actif=bool(row['actif']),
            date_creation=row['date_creation'],
            date_derniere_connexion=row['date_derniere_connexion'],
            tentatives_connexion=row['tentatives_connexion'],
            compte_bloque=bool(row['compte_bloque'])
        )

    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email"""
        query = "SELECT id FROM USERS WHERE email = %s"
        results = self.db.execute_query(query, (email,))
        return self._get_user_by_id(results[0]['id']) if results else None

    def _get_role_by_code(self, code: str) -> Optional[Role]:
        """Récupère un rôle par son code"""
        query = "SELECT * FROM ROLES WHERE code = %s"
        results = self.db.execute_query(query, (code,))
        if not results:
            return None

        row = results[0]
        return Role(
            id=row['id'],
            code=row['code'],
            nom=row['nom'],
            description=row.get('description'),
            peut_creer=bool(row['peut_creer']),
            peut_modifier=bool(row['peut_modifier']),
            peut_supprimer=bool(row['peut_supprimer']),
            peut_valider=bool(row['peut_valider']),
            peut_cloturer=bool(row['peut_cloturer']),
            peut_gerer_users=bool(row['peut_gerer_users'])
        )

    def _create_session(
        self,
        user_id: int,
        token: str,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> int:
        """Crée une session en base de données"""
        expiration = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        query = """
            INSERT INTO SESSIONS (user_id, token, ip_address, user_agent, date_expiration)
            VALUES (%s, %s, %s, %s, %s)
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, (user_id, token, ip_address, user_agent, expiration))
            return cursor.lastrowid

    def _revoke_session(self, token: str):
        """Révoque une session"""
        query = """
            UPDATE SESSIONS
            SET revoked = TRUE, date_revocation = NOW()
            WHERE token = %s
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (token,))

    def _increment_failed_attempts(self, user_id: int, username: str, ip_address: Optional[str]):
        """Incrémente les tentatives de connexion échouées"""
        query = """
            UPDATE USERS
            SET tentatives_connexion = tentatives_connexion + 1
            WHERE id = %s
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (user_id,))

        # Bloquer le compte si trop de tentatives
        self.db.call_procedure('BlockUserAfterFailedAttempts', (username, self.max_login_attempts))

        self._log_failed_login(username, "Mot de passe incorrect", ip_address)

    def _reset_failed_attempts(self, user_id: int):
        """Réinitialise les tentatives de connexion échouées"""
        query = "UPDATE USERS SET tentatives_connexion = 0 WHERE id = %s"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (user_id,))

    def _update_last_login(self, user_id: int):
        """Met à jour la date de dernière connexion"""
        query = "UPDATE USERS SET date_derniere_connexion = NOW() WHERE id = %s"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (user_id,))

    def _log_successful_login(self, user_id: int, username: str, ip_address: Optional[str]):
        """Enregistre une connexion réussie dans l'audit"""
        self.db.call_procedure('LogAudit', (
            user_id,
            username,
            'LOGIN',
            'USER',
            user_id,
            None,
            ip_address,
            True,
            None
        ))

    def _log_failed_login(self, username: str, reason: str, ip_address: Optional[str]):
        """Enregistre une tentative de connexion échouée"""
        self.db.call_procedure('LogAudit', (
            None,
            username,
            'LOGIN_FAILED',
            'USER',
            None,
            None,
            ip_address,
            False,
            reason
        ))

    def _log_logout(self, user_id: int, username: str, ip_address: Optional[str]):
        """Enregistre une déconnexion"""
        self.db.call_procedure('LogAudit', (
            user_id,
            username,
            'LOGOUT',
            'USER',
            user_id,
            None,
            ip_address,
            True,
            None
        ))
