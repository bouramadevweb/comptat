"""
Décorateurs pour la gestion des permissions et l'audit automatique
"""
import functools
import logging
from typing import Callable, Optional
from src.domain.models import User

logger = logging.getLogger(__name__)


class PermissionDenied(Exception):
    """Exception levée quand une permission est refusée"""
    pass


def require_permission(permission_attr: str):
    """
    Décorateur pour vérifier qu'un utilisateur a une permission spécifique

    Usage:
        @require_permission('peut_creer')
        def create_ecriture(self, user: User, ...):
            ...

    Args:
        permission_attr: Nom de l'attribut de permission à vérifier sur le Role
                        (peut_creer, peut_modifier, peut_supprimer, peut_valider,
                         peut_cloturer, peut_gerer_users)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Trouver l'utilisateur dans les arguments
            user = None

            # Chercher dans args
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break

            # Chercher dans kwargs
            if not user and 'user' in kwargs:
                user = kwargs['user']

            # Si pas d'utilisateur trouvé, lever une erreur
            if not user:
                raise ValueError(
                    f"Le décorateur @require_permission nécessite un paramètre 'user: User'"
                )

            # Vérifier que l'utilisateur est actif
            if not user.actif:
                raise PermissionDenied("Utilisateur désactivé")

            # Vérifier que le compte n'est pas bloqué
            if user.compte_bloque:
                raise PermissionDenied("Compte bloqué")

            # Vérifier la permission
            if not user.role:
                raise PermissionDenied("Utilisateur sans rôle")

            has_permission = getattr(user.role, permission_attr, False)

            if not has_permission:
                logger.warning(
                    f"❌ Permission refusée: {user.username} n'a pas {permission_attr}"
                )
                raise PermissionDenied(
                    f"Permission '{permission_attr}' requise (rôle actuel: {user.role.code})"
                )

            # Permission OK, exécuter la fonction
            logger.debug(f"✅ Permission {permission_attr} accordée à {user.username}")
            return func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(role_code: str):
    """
    Décorateur pour vérifier qu'un utilisateur a un rôle spécifique

    Usage:
        @require_role('ADMIN')
        def delete_user(self, user: User, ...):
            ...

    Args:
        role_code: Code du rôle requis (ADMIN, COMPTABLE, LECTEUR)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Trouver l'utilisateur
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            if not user and 'user' in kwargs:
                user = kwargs['user']

            if not user:
                raise ValueError(
                    f"Le décorateur @require_role nécessite un paramètre 'user: User'"
                )

            # Vérifier le rôle
            if not user.role or user.role.code != role_code:
                current_role = user.role.code if user.role else "AUCUN"
                logger.warning(
                    f"❌ Rôle refusé: {user.username} a le rôle {current_role}, "
                    f"{role_code} requis"
                )
                raise PermissionDenied(
                    f"Rôle '{role_code}' requis (rôle actuel: {current_role})"
                )

            return func(*args, **kwargs)

        return wrapper
    return decorator


def audit_action(action: str, entity_type: str):
    """
    Décorateur pour logger automatiquement une action dans l'audit

    Usage:
        @audit_action('CREATE', 'ECRITURE')
        def create_ecriture(self, user: User, ecriture: Ecriture):
            ...
            return success, message, ecriture_id

    La fonction décorée doit retourner (success, message, entity_id) ou (success, message)

    Args:
        action: Type d'action (CREATE, UPDATE, DELETE, VALIDATE, etc.)
        entity_type: Type d'entité (ECRITURE, USER, EXERCICE, etc.)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Trouver l'utilisateur et le service d'audit
            user = None
            audit_service = None

            # Dans les args
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                # Chercher AuditService dans self
                if hasattr(arg, 'audit_service'):
                    audit_service = arg.audit_service

            # Dans kwargs
            if not user and 'user' in kwargs:
                user = kwargs['user']

            # Exécuter la fonction
            result = func(*args, **kwargs)

            # Logger dans l'audit si le service est disponible
            if audit_service and user:
                try:
                    # Extraire entity_id du résultat
                    entity_id = None
                    success = False
                    error_message = None

                    if isinstance(result, tuple):
                        if len(result) >= 2:
                            success = result[0]
                            error_message = result[1] if not success else None
                        if len(result) >= 3:
                            entity_id = result[2]

                    # Logger l'action
                    audit_service.log_action(
                        user_id=user.id,
                        username=user.username,
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        success=success,
                        error_message=error_message
                    )
                except Exception as e:
                    logger.error(f"Erreur logging audit dans décorateur: {e}")

            return result

        return wrapper
    return decorator


def require_active_exercice():
    """
    Décorateur pour vérifier qu'un exercice est actif (non clôturé)

    Usage:
        @require_active_exercice()
        def create_ecriture(self, exercice: Exercice, ...):
            ...

    L'exercice doit être passé en argument
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from src.domain.models import Exercice

            # Trouver l'exercice
            exercice = None
            for arg in args:
                if isinstance(arg, Exercice):
                    exercice = arg
                    break
            if not exercice and 'exercice' in kwargs:
                exercice = kwargs['exercice']

            if not exercice:
                raise ValueError(
                    "Le décorateur @require_active_exercice nécessite un paramètre Exercice"
                )

            # Vérifier que l'exercice n'est pas clôturé
            if exercice.cloture:
                raise PermissionDenied(
                    f"L'exercice {exercice.annee} est clôturé, modification impossible"
                )

            return func(*args, **kwargs)

        return wrapper
    return decorator


# ==================== DÉCORATEURS COMBINÉS ====================

def require_create_permission():
    """Décorateur combiné: vérifie la permission de création"""
    return require_permission('peut_creer')


def require_modify_permission():
    """Décorateur combiné: vérifie la permission de modification"""
    return require_permission('peut_modifier')


def require_delete_permission():
    """Décorateur combiné: vérifie la permission de suppression"""
    return require_permission('peut_supprimer')


def require_validate_permission():
    """Décorateur combiné: vérifie la permission de validation"""
    return require_permission('peut_valider')


def require_close_permission():
    """Décorateur combiné: vérifie la permission de clôture"""
    return require_permission('peut_cloturer')


def require_admin_role():
    """Décorateur combiné: vérifie le rôle ADMIN"""
    return require_role('ADMIN')


# ==================== EXEMPLE D'UTILISATION ====================

"""
Exemples d'utilisation des décorateurs:

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
        user: User,
        exercice: Exercice,
        ecriture: Ecriture
    ) -> Tuple[bool, str, Optional[int]]:
        # La méthode sera exécutée seulement si:
        # 1. L'utilisateur a la permission 'peut_creer'
        # 2. L'exercice n'est pas clôturé
        # 3. L'action sera automatiquement loggée dans l'audit

        ecriture_id = self.dao.create(ecriture)
        return True, "Écriture créée", ecriture_id

    @require_admin_role()
    @audit_action('DELETE', 'USER')
    def delete_user(
        self,
        user: User,  # L'utilisateur qui effectue l'action
        target_user_id: int
    ) -> Tuple[bool, str]:
        # Seulement les ADMIN peuvent supprimer des utilisateurs
        self.dao.delete(target_user_id)
        return True, "Utilisateur supprimé"

    @require_close_permission()
    @audit_action('CLOSE', 'EXERCICE')
    def close_exercice(
        self,
        user: User,
        exercice_id: int
    ) -> Tuple[bool, str, int]:
        self.dao.cloturer(exercice_id)
        return True, "Exercice clôturé", exercice_id
"""
