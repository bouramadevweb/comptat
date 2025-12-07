"""
Service d'audit trail - Traçabilité de toutes les actions
"""
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from src.domain.models import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service de journalisation d'audit"""

    def __init__(self, db_manager):
        """
        Initialize audit service
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    # ==================== LOGGING D'ACTIONS ====================

    def log_action(
        self,
        user_id: Optional[int],
        username: str,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> int:
        """
        Enregistre une action dans le journal d'audit
        Args:
            user_id: ID de l'utilisateur (None pour actions système)
            username: Nom d'utilisateur
            action: Type d'action (CREATE, UPDATE, DELETE, VALIDATE, CLOSE, etc.)
            entity_type: Type d'entité (ECRITURE, SOCIETE, USER, etc.)
            entity_id: ID de l'entité affectée
            details: Détails supplémentaires au format dict (sera converti en JSON)
            ip_address: Adresse IP du client
            success: Si l'action a réussi
            error_message: Message d'erreur si échec
        Returns:
            ID du log d'audit créé
        """
        try:
            # Convertir les détails en JSON
            details_json = None
            if details:
                details_json = json.dumps(details, default=self._json_serializer, ensure_ascii=False)

            # Insérer dans la base
            result = self.db.call_procedure('LogAudit', (
                user_id,
                username,
                action,
                entity_type,
                entity_id,
                details_json,
                ip_address,
                success,
                error_message
            ))

            audit_id = result[0]['audit_id'] if result else None

            if success:
                logger.info(f"✅ Audit logged: {username} - {action} {entity_type} #{entity_id}")
            else:
                logger.warning(f"⚠️  Audit logged (échec): {username} - {action} {entity_type} - {error_message}")

            return audit_id

        except Exception as e:
            logger.error(f"❌ Erreur logging audit: {e}", exc_info=True)
            return 0

    # ==================== ACTIONS SPÉCIFIQUES ====================

    def log_ecriture_created(
        self,
        user_id: int,
        username: str,
        ecriture_id: int,
        numero: str,
        montant_total: Decimal,
        ip_address: Optional[str] = None
    ):
        """Enregistre la création d'une écriture"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action='CREATE',
            entity_type='ECRITURE',
            entity_id=ecriture_id,
            details={
                'numero': numero,
                'montant_total': str(montant_total)
            },
            ip_address=ip_address,
            success=True
        )

    def log_ecriture_validated(
        self,
        user_id: int,
        username: str,
        ecriture_id: int,
        numero: str,
        ip_address: Optional[str] = None
    ):
        """Enregistre la validation d'une écriture"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action='VALIDATE',
            entity_type='ECRITURE',
            entity_id=ecriture_id,
            details={'numero': numero},
            ip_address=ip_address,
            success=True
        )

    def log_ecriture_deleted(
        self,
        user_id: int,
        username: str,
        ecriture_id: int,
        numero: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Enregistre la suppression d'une écriture"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action='DELETE',
            entity_type='ECRITURE',
            entity_id=ecriture_id,
            details={
                'numero': numero,
                'reason': reason or 'Non spécifiée'
            },
            ip_address=ip_address,
            success=True
        )

    def log_exercice_closed(
        self,
        user_id: int,
        username: str,
        exercice_id: int,
        annee: int,
        ip_address: Optional[str] = None
    ):
        """Enregistre la clôture d'un exercice"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action='CLOSE',
            entity_type='EXERCICE',
            entity_id=exercice_id,
            details={'annee': annee},
            ip_address=ip_address,
            success=True
        )

    def log_lettrage(
        self,
        user_id: int,
        username: str,
        compte_numero: str,
        code_lettrage: str,
        nb_mouvements: int,
        ip_address: Optional[str] = None
    ):
        """Enregistre un lettrage"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action='LETTRAGE',
            entity_type='MOUVEMENT',
            details={
                'compte': compte_numero,
                'code_lettrage': code_lettrage,
                'nb_mouvements': nb_mouvements
            },
            ip_address=ip_address,
            success=True
        )

    def log_export_fec(
        self,
        user_id: int,
        username: str,
        societe_id: int,
        exercice_id: int,
        nb_lignes: int,
        ip_address: Optional[str] = None
    ):
        """Enregistre un export FEC"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action='EXPORT_FEC',
            entity_type='EXERCICE',
            entity_id=exercice_id,
            details={
                'societe_id': societe_id,
                'nb_lignes': nb_lignes
            },
            ip_address=ip_address,
            success=True
        )

    def log_user_created(
        self,
        admin_user_id: int,
        admin_username: str,
        new_user_id: int,
        new_username: str,
        role_code: str,
        ip_address: Optional[str] = None
    ):
        """Enregistre la création d'un utilisateur"""
        return self.log_action(
            user_id=admin_user_id,
            username=admin_username,
            action='CREATE',
            entity_type='USER',
            entity_id=new_user_id,
            details={
                'new_username': new_username,
                'role': role_code
            },
            ip_address=ip_address,
            success=True
        )

    def log_permission_denied(
        self,
        user_id: int,
        username: str,
        action: str,
        entity_type: str,
        reason: str,
        ip_address: Optional[str] = None
    ):
        """Enregistre un refus de permission"""
        return self.log_action(
            user_id=user_id,
            username=username,
            action=f'{action}_DENIED',
            entity_type=entity_type,
            details={'reason': reason},
            ip_address=ip_address,
            success=False,
            error_message=f"Permission refusée: {reason}"
        )

    # ==================== CONSULTATION DES LOGS ====================

    def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Récupère les logs d'audit avec filtres
        Args:
            user_id: Filtrer par utilisateur
            action: Filtrer par type d'action
            entity_type: Filtrer par type d'entité
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre max de résultats
            offset: Offset pour pagination
        Returns:
            Liste des logs d'audit
        """
        try:
            where_clauses = []
            params = []

            if user_id:
                where_clauses.append("user_id = %s")
                params.append(user_id)

            if action:
                where_clauses.append("action = %s")
                params.append(action)

            if entity_type:
                where_clauses.append("entity_type = %s")
                params.append(entity_type)

            if start_date:
                where_clauses.append("DATE(date_action) >= %s")
                params.append(start_date)

            if end_date:
                where_clauses.append("DATE(date_action) <= %s")
                params.append(end_date)

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            query = f"""
                SELECT *
                FROM AUDIT_LOG
                WHERE {where_clause}
                ORDER BY date_action DESC
                LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])

            results = self.db.execute_query(query, tuple(params))

            logs = []
            for row in results:
                # Parser le JSON des détails
                details = None
                if row.get('details'):
                    try:
                        details = json.loads(row['details'])
                    except:
                        details = row['details']

                log = AuditLog(
                    id=row['id'],
                    user_id=row.get('user_id'),
                    username=row['username'],
                    action=row['action'],
                    entity_type=row.get('entity_type'),
                    entity_id=row.get('entity_id'),
                    details=details,
                    ip_address=row.get('ip_address'),
                    date_action=row['date_action'],
                    success=bool(row['success']),
                    error_message=row.get('error_message')
                )
                logs.append(log)

            return logs

        except Exception as e:
            logger.error(f"Erreur récupération logs d'audit: {e}")
            return []

    def get_user_activity(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtient un résumé de l'activité d'un utilisateur
        Args:
            user_id: ID de l'utilisateur
            days: Nombre de jours à analyser
        Returns:
            Dictionnaire avec statistiques d'activité
        """
        try:
            query = """
                SELECT
                    action,
                    entity_type,
                    COUNT(*) as count,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failure_count
                FROM AUDIT_LOG
                WHERE user_id = %s
                  AND date_action >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY action, entity_type
                ORDER BY count DESC
            """

            results = self.db.execute_query(query, (user_id, days))

            activity = {
                'user_id': user_id,
                'period_days': days,
                'actions': []
            }

            total_actions = 0
            total_success = 0
            total_failures = 0

            for row in results:
                action_stat = {
                    'action': row['action'],
                    'entity_type': row['entity_type'],
                    'total': row['count'],
                    'success': row['success_count'],
                    'failures': row['failure_count']
                }
                activity['actions'].append(action_stat)

                total_actions += row['count']
                total_success += row['success_count']
                total_failures += row['failure_count']

            activity['summary'] = {
                'total_actions': total_actions,
                'total_success': total_success,
                'total_failures': total_failures,
                'success_rate': round(total_success / total_actions * 100, 2) if total_actions > 0 else 0
            }

            return activity

        except Exception as e:
            logger.error(f"Erreur récupération activité utilisateur: {e}")
            return {}

    def get_entity_history(
        self,
        entity_type: str,
        entity_id: int
    ) -> List[AuditLog]:
        """
        Obtient l'historique complet d'une entité
        Args:
            entity_type: Type d'entité (ECRITURE, USER, etc.)
            entity_id: ID de l'entité
        Returns:
            Liste chronologique des actions sur cette entité
        """
        query = """
            SELECT *
            FROM AUDIT_LOG
            WHERE entity_type = %s
              AND entity_id = %s
            ORDER BY date_action ASC
        """

        results = self.db.execute_query(query, (entity_type, entity_id))

        logs = []
        for row in results:
            details = None
            if row.get('details'):
                try:
                    details = json.loads(row['details'])
                except:
                    details = row['details']

            log = AuditLog(
                id=row['id'],
                user_id=row.get('user_id'),
                username=row['username'],
                action=row['action'],
                entity_type=row.get('entity_type'),
                entity_id=row.get('entity_id'),
                details=details,
                ip_address=row.get('ip_address'),
                date_action=row['date_action'],
                success=bool(row['success']),
                error_message=row.get('error_message')
            )
            logs.append(log)

        return logs

    # ==================== NETTOYAGE ====================

    def clean_old_logs(self, days_to_keep: int = 365) -> int:
        """
        Nettoie les anciens logs d'audit
        Args:
            days_to_keep: Nombre de jours à conserver
        Returns:
            Nombre de logs supprimés
        """
        try:
            result = self.db.call_procedure('ArchiveOldAuditLogs', (days_to_keep,))
            deleted_count = result[0]['logs_archives'] if result else 0

            logger.info(f"✅ {deleted_count} logs d'audit archivés (> {days_to_keep} jours)")
            return deleted_count

        except Exception as e:
            logger.error(f"Erreur nettoyage logs d'audit: {e}")
            return 0

    # ==================== UTILITAIRES ====================

    @staticmethod
    def _json_serializer(obj):
        """Sérialiseur JSON custom pour Decimal et date"""
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} non sérialisable")
