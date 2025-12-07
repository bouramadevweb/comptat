-- ============================================================
-- SCRIPT D'OPTIMISATION DE LA BASE DE DONNÉES COMPTABLE
-- ============================================================
-- Ce script ajoute des index pour améliorer les performances
-- et optimise la structure de la base de données
-- ============================================================

USE COMPTA;

-- ============================================================
-- 1. AJOUT D'INDEX POUR AMÉLIORER LES PERFORMANCES
-- ============================================================

-- Index sur les sociétés
ALTER TABLE SOCIETES
    ADD INDEX idx_siren (SIREN),
    ADD INDEX idx_nom (Nom);

-- Index sur les exercices
ALTER TABLE EXERCICES
    ADD INDEX idx_societe_annee (SocieteCode, Annee),
    ADD INDEX idx_cloture (Cloture),
    ADD INDEX idx_dates (DateDebut, DateFin);

-- Index sur les journaux
ALTER TABLE JOURNAUX
    ADD INDEX idx_societe_code (SocieteCode, Code),
    ADD INDEX idx_type (Type);

-- Index sur les comptes
ALTER TABLE COMPTES
    ADD INDEX idx_societe_numero (SocieteCode, Numero),
    ADD INDEX idx_classe (Classe),
    ADD INDEX idx_type (TypeCompte),
    ADD INDEX idx_lettrable (Lettrable),
    ADD INDEX idx_numero (Numero);

-- Index sur les tiers
ALTER TABLE TIERS
    ADD INDEX idx_societe_code (SocieteCode, Code),
    ADD INDEX idx_type (Type),
    ADD INDEX idx_nom (Nom),
    ADD INDEX idx_societe_type (SocieteCode, Type);

-- Index sur les écritures (TRÈS IMPORTANT pour les performances)
ALTER TABLE ECRITURES
    ADD INDEX idx_societe_exercice (SocieteCode, ExerciceId),
    ADD INDEX idx_journal (JournalId),
    ADD INDEX idx_date (DateEcriture),
    ADD INDEX idx_numero (Numero),
    ADD INDEX idx_valide (Valide),
    ADD INDEX idx_societe_journal_date (SocieteCode, JournalId, DateEcriture);

-- Index sur les mouvements (TRÈS IMPORTANT pour les performances)
ALTER TABLE MOUVEMENTS
    ADD INDEX idx_ecriture (EcritureId),
    ADD INDEX idx_compte (CompteNumero),
    ADD INDEX idx_tiers (TiersCode),
    ADD INDEX idx_lettrage (Lettrage),
    ADD INDEX idx_date_lettrage (DateLettrage),
    ADD INDEX idx_compte_tiers (CompteNumero, TiersCode),
    ADD INDEX idx_ecriture_compte (EcritureId, CompteNumero);

-- Index sur la balance
ALTER TABLE BALANCE
    ADD INDEX idx_societe_exercice (SocieteCode, ExerciceAnnee),
    ADD INDEX idx_compte (CompteNumero),
    ADD INDEX idx_societe_exercice_compte (SocieteCode, ExerciceAnnee, CompteNumero);

-- ============================================================
-- 2. OPTIMISATION DES COLONNES POUR LES RECHERCHES
-- ============================================================

-- Analyser les tables pour mettre à jour les statistiques
ANALYZE TABLE SOCIETES, EXERCICES, JOURNAUX, COMPTES, TIERS, ECRITURES, MOUVEMENTS, BALANCE;

-- ============================================================
-- 3. VUES MATÉRIALISÉES (Simulées avec des tables)
-- ============================================================

-- Vue: Soldes des comptes tiers
CREATE OR REPLACE VIEW V_SOLDES_TIERS AS
SELECT
    t.SocieteCode,
    t.Code as TiersCode,
    t.Nom as TiersNom,
    t.Type as TiersType,
    m.CompteNumero,
    c.Libelle as CompteLibelle,
    SUM(m.Debit) as TotalDebit,
    SUM(m.Credit) as TotalCredit,
    SUM(m.Debit - m.Credit) as Solde,
    COUNT(DISTINCT e.Id) as NbEcritures,
    MAX(e.DateEcriture) as DerniereEcriture
FROM TIERS t
JOIN MOUVEMENTS m ON m.TiersCode = t.Code
JOIN ECRITURES e ON e.Id = m.EcritureId
JOIN COMPTES c ON c.Numero = m.CompteNumero
WHERE e.Valide = 1
GROUP BY t.SocieteCode, t.Code, t.Nom, t.Type, m.CompteNumero, c.Libelle;

-- Vue: Écritures non lettrées par compte
CREATE OR REPLACE VIEW V_MOUVEMENTS_NON_LETTRES AS
SELECT
    e.SocieteCode,
    ex.Annee as ExerciceAnnee,
    m.CompteNumero,
    c.Libelle as CompteLibelle,
    m.TiersCode,
    t.Nom as TiersNom,
    e.DateEcriture,
    e.Numero as EcritureNumero,
    e.Reference,
    m.Libelle,
    m.Debit,
    m.Credit,
    (m.Debit - m.Credit) as Solde,
    m.Id as MouvementId
FROM MOUVEMENTS m
JOIN ECRITURES e ON e.Id = m.EcritureId
JOIN EXERCICES ex ON ex.Id = e.ExerciceId
JOIN COMPTES c ON c.Numero = m.CompteNumero
LEFT JOIN TIERS t ON t.Code = m.TiersCode
WHERE (m.Lettrage IS NULL OR m.Lettrage = '')
AND e.Valide = 1
AND c.Lettrable = 1;

-- Vue: Récapitulatif TVA par mois
CREATE OR REPLACE VIEW V_TVA_PAR_MOIS AS
SELECT
    e.SocieteCode,
    ex.Annee as Annee,
    MONTH(e.DateEcriture) as Mois,
    DATE_FORMAT(e.DateEcriture, '%Y-%m') as PeriodeMois,
    SUM(CASE WHEN LEFT(m.CompteNumero, 4) = '4457' THEN m.Credit - m.Debit ELSE 0 END) as TVACollectee,
    SUM(CASE WHEN LEFT(m.CompteNumero, 4) = '4456' THEN m.Debit - m.Credit ELSE 0 END) as TVADeductible,
    SUM(CASE WHEN LEFT(m.CompteNumero, 4) = '4457' THEN m.Credit - m.Debit ELSE 0 END) -
    SUM(CASE WHEN LEFT(m.CompteNumero, 4) = '4456' THEN m.Debit - m.Credit ELSE 0 END) as TVAAPayer
FROM MOUVEMENTS m
JOIN ECRITURES e ON e.Id = m.EcritureId
JOIN EXERCICES ex ON ex.Id = e.ExerciceId
WHERE e.Valide = 1
AND LEFT(m.CompteNumero, 3) = '445'
GROUP BY e.SocieteCode, ex.Annee, MONTH(e.DateEcriture), DATE_FORMAT(e.DateEcriture, '%Y-%m');

-- Vue: Tableau de bord
CREATE OR REPLACE VIEW V_DASHBOARD_STATS AS
SELECT
    e.SocieteCode,
    ex.Annee as ExerciceAnnee,
    COUNT(DISTINCT e.Id) as NbEcritures,
    COUNT(DISTINCT m.Id) as NbMouvements,
    SUM(CASE WHEN LEFT(m.CompteNumero, 1) = '6' THEN m.Debit - m.Credit ELSE 0 END) as TotalCharges,
    SUM(CASE WHEN LEFT(m.CompteNumero, 1) = '7' THEN m.Credit - m.Debit ELSE 0 END) as TotalProduits,
    SUM(CASE WHEN LEFT(m.CompteNumero, 1) = '7' THEN m.Credit - m.Debit ELSE 0 END) -
    SUM(CASE WHEN LEFT(m.CompteNumero, 1) = '6' THEN m.Debit - m.Credit ELSE 0 END) as Resultat,
    SUM(CASE WHEN m.CompteNumero LIKE '411%' AND (m.Debit - m.Credit) > 0 THEN m.Debit - m.Credit ELSE 0 END) as CreancesClients,
    SUM(CASE WHEN m.CompteNumero LIKE '401%' AND (m.Credit - m.Debit) > 0 THEN m.Credit - m.Debit ELSE 0 END) as DettesFournisseurs,
    SUM(CASE WHEN m.CompteNumero LIKE '512%' THEN m.Debit - m.Credit ELSE 0 END) as SoldeBanque,
    SUM(CASE WHEN m.CompteNumero LIKE '530%' THEN m.Debit - m.Credit ELSE 0 END) as SoldeCaisse
FROM ECRITURES e
JOIN EXERCICES ex ON ex.Id = e.ExerciceId
JOIN MOUVEMENTS m ON m.EcritureId = e.Id
WHERE e.Valide = 1
GROUP BY e.SocieteCode, ex.Annee;

-- ============================================================
-- 4. CONTRAINTES D'INTÉGRITÉ SUPPLÉMENTAIRES
-- ============================================================

-- S'assurer que les dates d'exercice sont cohérentes
DELIMITER $$

DROP TRIGGER IF EXISTS check_exercice_dates$$

CREATE TRIGGER check_exercice_dates
BEFORE INSERT ON EXERCICES
FOR EACH ROW
BEGIN
    IF NEW.DateFin <= NEW.DateDebut THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La date de fin doit être postérieure à la date de début';
    END IF;
END$$

-- S'assurer que les écritures sont dans la période de l'exercice
DROP TRIGGER IF EXISTS check_ecriture_date$$

CREATE TRIGGER check_ecriture_date
BEFORE INSERT ON ECRITURES
FOR EACH ROW
BEGIN
    DECLARE v_date_debut DATE;
    DECLARE v_date_fin DATE;
    DECLARE v_cloture BOOLEAN;

    SELECT DateDebut, DateFin, Cloture INTO v_date_debut, v_date_fin, v_cloture
    FROM EXERCICES
    WHERE Id = NEW.ExerciceId;

    IF v_cloture = 1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Impossible de créer une écriture sur un exercice clôturé';
    END IF;

    IF NEW.DateEcriture < v_date_debut OR NEW.DateEcriture > v_date_fin THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La date de l\'écriture doit être dans la période de l\'exercice';
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- 5. PROCÉDURES D'ANALYSE ET DE MAINTENANCE
-- ============================================================

DELIMITER $$

-- Procédure d'optimisation des tables
DROP PROCEDURE IF EXISTS Optimiser_Tables$$

CREATE PROCEDURE Optimiser_Tables()
BEGIN
    -- Optimiser toutes les tables
    OPTIMIZE TABLE SOCIETES, EXERCICES, JOURNAUX, COMPTES, TIERS, ECRITURES, MOUVEMENTS, BALANCE;

    -- Analyser les tables pour mettre à jour les statistiques
    ANALYZE TABLE SOCIETES, EXERCICES, JOURNAUX, COMPTES, TIERS, ECRITURES, MOUVEMENTS, BALANCE;

    SELECT 'Optimisation terminée' as Status;
END$$

-- Procédure de diagnostic des performances
DROP PROCEDURE IF EXISTS Diagnostiquer_Performances$$

CREATE PROCEDURE Diagnostiquer_Performances()
BEGIN
    -- Statistiques des tables
    SELECT
        TABLE_NAME as TableName,
        TABLE_ROWS as NbLignes,
        ROUND(DATA_LENGTH / 1024 / 1024, 2) as TailleMB,
        ROUND(INDEX_LENGTH / 1024 / 1024, 2) as TailleIndexMB,
        ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as TailleTotaleMB
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = 'COMPTA'
    ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC;
END$$

-- Procédure pour lister les index manquants potentiels
DROP PROCEDURE IF EXISTS Suggerer_Index$$

CREATE PROCEDURE Suggerer_Index()
BEGIN
    -- Cette procédure suggère des index basés sur les requêtes lentes
    SELECT
        'Vérifiez le slow query log pour identifier les requêtes lentes' as Suggestion
    UNION
    SELECT
        'Utilisez EXPLAIN sur vos requêtes fréquentes pour voir si elles utilisent les index' as Suggestion
    UNION
    SELECT
        'Consultez information_schema.INDEX_STATISTICS pour voir les index inutilisés' as Suggestion;
END$$

DELIMITER ;

-- ============================================================
-- 6. PARAMÈTRES DE CONFIGURATION MYSQL RECOMMANDÉS
-- ============================================================

-- Ces paramètres doivent être ajustés dans le fichier my.cnf ou my.ini

/*
[mysqld]
# Taille du buffer pool (ajuster selon la RAM disponible)
innodb_buffer_pool_size = 2G

# Taille du log file
innodb_log_file_size = 256M

# Flush log
innodb_flush_log_at_trx_commit = 2

# Connexions simultanées
max_connections = 100

# Query cache (désactivé par défaut en MySQL 8.0+)
# query_cache_type = 1
# query_cache_size = 64M

# Logs lents pour identifier les requêtes à optimiser
slow_query_log = 1
long_query_time = 2
slow_query_log_file = /var/log/mysql/slow-query.log

# Optimisation InnoDB
innodb_file_per_table = 1
innodb_flush_method = O_DIRECT
*/

-- ============================================================
-- RÉSULTAT DE L'OPTIMISATION
-- ============================================================

SELECT '✅ Script d\'optimisation exécuté avec succès !' AS Status;

-- Afficher les statistiques
CALL Diagnostiquer_Performances();
