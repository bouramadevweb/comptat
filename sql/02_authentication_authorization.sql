-- ==========================================
-- AUTHENTIFICATION & AUTORISATION
-- Script de création des tables pour le système d'auth
-- Date: 23 novembre 2025
-- ==========================================

USE Comptabilite;

-- Table des rôles
CREATE TABLE IF NOT EXISTS ROLES (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    -- Permissions
    peut_creer BOOLEAN DEFAULT FALSE,
    peut_modifier BOOLEAN DEFAULT FALSE,
    peut_supprimer BOOLEAN DEFAULT FALSE,
    peut_valider BOOLEAN DEFAULT FALSE,
    peut_cloturer BOOLEAN DEFAULT FALSE,
    peut_gerer_users BOOLEAN DEFAULT FALSE,
    -- Métadonnées
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS USERS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    role_id INT NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_derniere_connexion TIMESTAMP NULL,
    tentatives_connexion INT DEFAULT 0,
    compte_bloque BOOLEAN DEFAULT FALSE,
    date_blocage TIMESTAMP NULL,
    -- Clés étrangères
    FOREIGN KEY (role_id) REFERENCES ROLES(id),
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_actif (actif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des sessions
CREATE TABLE IF NOT EXISTS SESSIONS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    ip_address VARCHAR(45),  -- Support IPv6
    user_agent TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_expiration TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    date_revocation TIMESTAMP NULL,
    -- Clés étrangères
    FOREIGN KEY (user_id) REFERENCES USERS(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expiration (date_expiration),
    INDEX idx_revoked (revoked)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table du journal d'audit
CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- CREATE, UPDATE, DELETE, VALIDATE, CLOSE, LOGIN, LOGOUT
    entity_type VARCHAR(50),      -- ECRITURE, SOCIETE, EXERCICE, USER, etc.
    entity_id INT,
    details JSON,                 -- Détails de l'action au format JSON
    ip_address VARCHAR(45),
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    -- Clés étrangères (optionnelles car l'utilisateur peut être supprimé)
    FOREIGN KEY (user_id) REFERENCES USERS(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_date_action (date_action),
    INDEX idx_action (action),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_success (success)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- DONNÉES INITIALES
-- ==========================================

-- Insertion des rôles par défaut
INSERT INTO ROLES (code, nom, description, peut_creer, peut_modifier, peut_supprimer, peut_valider, peut_cloturer, peut_gerer_users) VALUES
('ADMIN', 'Administrateur', 'Accès complet au système, gestion des utilisateurs', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
('COMPTABLE', 'Comptable', 'Peut créer, modifier et valider les écritures', TRUE, TRUE, FALSE, TRUE, FALSE, FALSE),
('LECTEUR', 'Lecteur', 'Accès en lecture seule aux données comptables', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)
ON DUPLICATE KEY UPDATE nom=VALUES(nom);

-- Création de l'utilisateur admin par défaut
-- Mot de passe: admin123 (À CHANGER EN PRODUCTION!)
-- Hash bcrypt généré avec: bcrypt.hashpw(b'admin123', bcrypt.gensalt())
INSERT INTO USERS (username, email, password_hash, nom, prenom, role_id, actif)
SELECT
    'admin',
    'admin@comptabilite.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY0oA6jVEGXTKge',  -- admin123
    'Administrateur',
    'Système',
    (SELECT id FROM ROLES WHERE code = 'ADMIN'),
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM USERS WHERE username = 'admin');

-- ==========================================
-- PROCÉDURES STOCKÉES
-- ==========================================

DELIMITER //

-- Procédure pour nettoyer les sessions expirées
CREATE PROCEDURE IF NOT EXISTS CleanExpiredSessions()
BEGIN
    DELETE FROM SESSIONS
    WHERE date_expiration < NOW()
       OR (revoked = TRUE AND date_revocation < DATE_SUB(NOW(), INTERVAL 7 DAY));

    SELECT ROW_COUNT() as sessions_supprimees;
END //

-- Procédure pour révoquer toutes les sessions d'un utilisateur
CREATE PROCEDURE IF NOT EXISTS RevokeUserSessions(
    IN p_user_id INT
)
BEGIN
    UPDATE SESSIONS
    SET revoked = TRUE,
        date_revocation = NOW()
    WHERE user_id = p_user_id
      AND revoked = FALSE;

    SELECT ROW_COUNT() as sessions_revoquees;
END //

-- Procédure pour logger une action dans l'audit
CREATE PROCEDURE IF NOT EXISTS LogAudit(
    IN p_user_id INT,
    IN p_username VARCHAR(50),
    IN p_action VARCHAR(50),
    IN p_entity_type VARCHAR(50),
    IN p_entity_id INT,
    IN p_details JSON,
    IN p_ip_address VARCHAR(45),
    IN p_success BOOLEAN,
    IN p_error_message TEXT
)
BEGIN
    INSERT INTO AUDIT_LOG (
        user_id, username, action, entity_type, entity_id,
        details, ip_address, success, error_message
    ) VALUES (
        p_user_id, p_username, p_action, p_entity_type, p_entity_id,
        p_details, p_ip_address, p_success, p_error_message
    );

    SELECT LAST_INSERT_ID() as audit_id;
END //

-- Procédure pour obtenir les permissions d'un utilisateur
CREATE PROCEDURE IF NOT EXISTS GetUserPermissions(
    IN p_user_id INT
)
BEGIN
    SELECT
        u.id as user_id,
        u.username,
        u.actif,
        u.compte_bloque,
        r.code as role_code,
        r.nom as role_nom,
        r.peut_creer,
        r.peut_modifier,
        r.peut_supprimer,
        r.peut_valider,
        r.peut_cloturer,
        r.peut_gerer_users
    FROM USERS u
    INNER JOIN ROLES r ON u.role_id = r.id
    WHERE u.id = p_user_id;
END //

-- Procédure pour archiver les anciens logs d'audit
CREATE PROCEDURE IF NOT EXISTS ArchiveOldAuditLogs(
    IN p_days_to_keep INT
)
BEGIN
    DECLARE rows_deleted INT;

    -- Supprimer les logs de plus de X jours (sauf les actions critiques)
    DELETE FROM AUDIT_LOG
    WHERE date_action < DATE_SUB(NOW(), INTERVAL p_days_to_keep DAY)
      AND action NOT IN ('DELETE', 'CLOSE', 'LOGIN_FAILED');

    SET rows_deleted = ROW_COUNT();

    SELECT rows_deleted as logs_archives;
END //

-- Procédure pour bloquer un utilisateur après trop de tentatives
CREATE PROCEDURE IF NOT EXISTS BlockUserAfterFailedAttempts(
    IN p_username VARCHAR(50),
    IN p_max_attempts INT
)
BEGIN
    UPDATE USERS
    SET compte_bloque = TRUE,
        date_blocage = NOW()
    WHERE username = p_username
      AND tentatives_connexion >= p_max_attempts
      AND compte_bloque = FALSE;

    IF ROW_COUNT() > 0 THEN
        SELECT TRUE as user_blocked, 'Compte bloqué après trop de tentatives' as message;
    ELSE
        SELECT FALSE as user_blocked, 'Aucun blocage nécessaire' as message;
    END IF;
END //

DELIMITER ;

-- ==========================================
-- VUES UTILES
-- ==========================================

-- Vue des utilisateurs actifs avec leurs rôles
CREATE OR REPLACE VIEW v_users_actifs AS
SELECT
    u.id,
    u.username,
    u.email,
    u.nom,
    u.prenom,
    r.code as role_code,
    r.nom as role_nom,
    u.date_creation,
    u.date_derniere_connexion,
    u.compte_bloque
FROM USERS u
INNER JOIN ROLES r ON u.role_id = r.id
WHERE u.actif = TRUE;

-- Vue des sessions actives
CREATE OR REPLACE VIEW v_sessions_actives AS
SELECT
    s.id,
    s.user_id,
    u.username,
    u.email,
    s.ip_address,
    s.date_creation,
    s.date_expiration,
    TIMESTAMPDIFF(MINUTE, NOW(), s.date_expiration) as minutes_restantes
FROM SESSIONS s
INNER JOIN USERS u ON s.user_id = u.id
WHERE s.revoked = FALSE
  AND s.date_expiration > NOW();

-- Vue de l'activité récente (dernières 24h)
CREATE OR REPLACE VIEW v_audit_recent AS
SELECT
    a.id,
    a.user_id,
    a.username,
    a.action,
    a.entity_type,
    a.entity_id,
    a.date_action,
    a.success,
    a.ip_address
FROM AUDIT_LOG a
WHERE a.date_action > DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY a.date_action DESC;

-- ==========================================
-- TRIGGERS
-- ==========================================

DELIMITER //

-- Trigger pour logger les modifications d'utilisateurs
CREATE TRIGGER IF NOT EXISTS trg_user_update_audit
AFTER UPDATE ON USERS
FOR EACH ROW
BEGIN
    IF OLD.actif != NEW.actif OR OLD.compte_bloque != NEW.compte_bloque THEN
        INSERT INTO AUDIT_LOG (
            user_id, username, action, entity_type, entity_id,
            details, success
        ) VALUES (
            NEW.id,
            NEW.username,
            'UPDATE',
            'USER',
            NEW.id,
            JSON_OBJECT(
                'actif', NEW.actif,
                'compte_bloque', NEW.compte_bloque,
                'old_actif', OLD.actif,
                'old_compte_bloque', OLD.compte_bloque
            ),
            TRUE
        );
    END IF;
END //

DELIMITER ;

-- ==========================================
-- INDEXES SUPPLÉMENTAIRES POUR PERFORMANCE
-- ==========================================

-- Index pour les recherches d'audit
CREATE INDEX idx_audit_user_date ON AUDIT_LOG(user_id, date_action DESC);
CREATE INDEX idx_audit_entity_date ON AUDIT_LOG(entity_type, entity_id, date_action DESC);

-- ==========================================
-- COMMENTAIRES
-- ==========================================

ALTER TABLE ROLES COMMENT = 'Définition des rôles et permissions du système';
ALTER TABLE USERS COMMENT = 'Utilisateurs de l\'application comptable';
ALTER TABLE SESSIONS COMMENT = 'Sessions utilisateurs actives avec tokens JWT';
ALTER TABLE AUDIT_LOG COMMENT = 'Journal d\'audit de toutes les actions système';

-- ==========================================
-- FIN DU SCRIPT
-- ==========================================

SELECT 'Tables d\'authentification créées avec succès!' as message;
SELECT COUNT(*) as nb_roles FROM ROLES;
SELECT COUNT(*) as nb_users FROM USERS;
