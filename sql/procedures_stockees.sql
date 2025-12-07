-- ============================================================
-- PROCÉDURES STOCKÉES - SYSTÈME DE COMPTABILITÉ
-- ============================================================
-- Ce fichier contient toutes les procédures stockées nécessaires
-- pour le fonctionnement complet du système de comptabilité
-- ============================================================

USE COMPTA;

DELIMITER $$

-- ============================================================
-- 1. Cloturer_Exercice
-- ============================================================
-- Procédure de clôture d'un exercice comptable
-- - Calcule le résultat (Produits - Charges)
-- - Crée l'écriture de résultat (120000 bénéfice / 129000 perte)
-- - Crée le nouvel exercice
-- - Génère le Report À Nouveau (RAN)
-- ============================================================

DROP PROCEDURE IF EXISTS Cloturer_Exercice$$

CREATE PROCEDURE Cloturer_Exercice(
    IN p_societe_code VARCHAR(10),
    IN p_exercice_annee INT
)
BEGIN
    DECLARE v_total_produits DECIMAL(15,2) DEFAULT 0;
    DECLARE v_total_charges DECIMAL(15,2) DEFAULT 0;
    DECLARE v_resultat DECIMAL(15,2) DEFAULT 0;
    DECLARE v_compte_resultat VARCHAR(10);
    DECLARE v_ecriture_id INT;
    DECLARE v_exercice_id INT;
    DECLARE v_nouveau_exercice_id INT;
    DECLARE v_journal_od_id INT;
    DECLARE v_date_cloture DATE;
    DECLARE v_exercice_existe INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Récupérer l'ID de l'exercice
    SELECT Id INTO v_exercice_id
    FROM EXERCICES
    WHERE societe_id = p_societe_code AND Annee = p_exercice_annee;
    
    IF v_exercice_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Exercice introuvable';
    END IF;
    
    -- Vérifier que l'exercice n'est pas déjà clôturé
    SELECT COUNT(*) INTO v_exercice_existe
    FROM EXERCICES
    WHERE Id = v_exercice_id AND Cloture = 1;
    
    IF v_exercice_existe > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Exercice déjà clôturé';
    END IF;
    
    SET v_date_cloture = CONCAT(p_exercice_annee, '-12-31');
    
    -- Calculer les produits (Classe 7)
    SELECT COALESCE(SUM(Credit - Debit), 0) INTO v_total_produits
    FROM BALANCE
    WHERE societe_id = p_societe_code 
    AND exercice_annee = p_exercice_annee
    AND LEFT(compte_id, 1) = '7';
    
    -- Calculer les charges (Classe 6)
    SELECT COALESCE(SUM(Debit - Credit), 0) INTO v_total_charges
    FROM BALANCE
    WHERE societe_id = p_societe_code 
    AND exercice_annee = p_exercice_annee
    AND LEFT(compte_id, 1) = '6';
    
    -- Calculer le résultat
    SET v_resultat = v_total_produits - v_total_charges;
    
    -- Choisir le compte de résultat
    IF v_resultat >= 0 THEN
        SET v_compte_resultat = '120000'; -- Bénéfice
    ELSE
        SET v_compte_resultat = '129000'; -- Perte
        SET v_resultat = -v_resultat; -- Convertir en positif
    END IF;
    
    -- Récupérer le journal OD
    SELECT Id INTO v_journal_od_id
    FROM JOURNAUX
    WHERE societe_id = p_societe_code AND Code = 'OD'
    LIMIT 1;
    
    -- Créer l'écriture de clôture
    INSERT INTO ECRITURES (
        societe_id, exercice_id, journal_id, date_ecriture, 
        Reference, libelle, Valide
    ) VALUES (
        p_societe_code, v_exercice_id, v_journal_od_id, v_date_cloture,
        CONCAT('CLO-', p_exercice_annee), 
        CONCAT('Clôture exercice ', p_exercice_annee),
        1
    );
    
    SET v_ecriture_id = LAST_INSERT_ID();
    
    -- Solder les comptes de charges (Crédit classe 6)
    INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, Debit, Credit)
    SELECT 
        v_ecriture_id,
        compte_id,
        CONCAT('Solde charges ', p_exercice_annee),
        0,
        Debit - Credit
    FROM BALANCE
    WHERE societe_id = p_societe_code 
    AND exercice_annee = p_exercice_annee
    AND LEFT(compte_id, 1) = '6'
    AND (Debit - Credit) > 0;
    
    -- Solder les comptes de produits (Débit classe 7)
    INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, Debit, Credit)
    SELECT 
        v_ecriture_id,
        compte_id,
        CONCAT('Solde produits ', p_exercice_annee),
        Credit - Debit,
        0
    FROM BALANCE
    WHERE societe_id = p_societe_code 
    AND exercice_annee = p_exercice_annee
    AND LEFT(compte_id, 1) = '7'
    AND (Credit - Debit) > 0;
    
    -- Enregistrer le résultat
    IF v_resultat > 0 THEN
        IF v_compte_resultat = '120000' THEN
            -- Bénéfice : Crédit au compte 120000
            INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, Debit, Credit)
            VALUES (v_ecriture_id, '120000', CONCAT('Bénéfice ', p_exercice_annee), 0, v_resultat);
        ELSE
            -- Perte : Débit au compte 129000
            INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, Debit, Credit)
            VALUES (v_ecriture_id, '129000', CONCAT('Perte ', p_exercice_annee), v_resultat, 0);
        END IF;
    END IF;
    
    -- Marquer l'exercice comme clôturé
    UPDATE EXERCICES
    SET Cloture = 1, DateCloture = v_date_cloture
    WHERE Id = v_exercice_id;
    
    -- Créer le nouvel exercice
    INSERT INTO EXERCICES (societe_id, Annee, DateDebut, DateFin, Cloture)
    VALUES (
        p_societe_code,
        p_exercice_annee + 1,
        CONCAT(p_exercice_annee + 1, '-01-01'),
        CONCAT(p_exercice_annee + 1, '-12-31'),
        0
    );
    
    SET v_nouveau_exercice_id = LAST_INSERT_ID();
    
    -- Créer l'écriture de Report À Nouveau (RAN)
    INSERT INTO ECRITURES (
        societe_id, exercice_id, journal_id, date_ecriture,
        Reference, libelle, Valide
    ) VALUES (
        p_societe_code, v_nouveau_exercice_id, v_journal_od_id,
        CONCAT(p_exercice_annee + 1, '-01-01'),
        CONCAT('RAN-', p_exercice_annee + 1),
        CONCAT('Report à nouveau exercice ', p_exercice_annee + 1),
        1
    );
    
    SET v_ecriture_id = LAST_INSERT_ID();
    
    -- Reporter les soldes des comptes de bilan (Classes 1 à 5)
    INSERT INTO MOUVEMENTS (ecriture_id, compte_id, tiers_id, libelle, Debit, Credit)
    SELECT
        v_ecriture_id,
        b.compte_id,
        NULL,
        CONCAT('RAN ', p_exercice_annee),
        IF((b.Debit - b.Credit) > 0, b.Debit - b.Credit, 0),
        IF((b.Credit - b.Debit) > 0, b.Credit - b.Debit, 0)
    FROM BALANCE b
    WHERE b.societe_id = p_societe_code
    AND b.exercice_annee = p_exercice_annee
    AND LEFT(b.compte_id, 1) IN ('1', '2', '3', '4', '5')
    AND (b.Debit - b.Credit) <> 0;
    
    -- Recalculer la balance pour le nouvel exercice
    CALL Calculer_Balance(p_societe_code, p_exercice_annee + 1);
    
    COMMIT;
    
    SELECT 
        v_resultat AS Resultat,
        v_compte_resultat AS CompteResultat,
        v_total_produits AS TotalProduits,
        v_total_charges AS TotalCharges,
        p_exercice_annee + 1 AS NouvelExercice;
        
END$$

-- ============================================================
-- 2. Exporter_FEC_Exercice
-- ============================================================
-- Export du Fichier des Écritures Comptables (FEC)
-- Format conforme aux spécifications de l'administration fiscale
-- ============================================================

DROP PROCEDURE IF EXISTS Exporter_FEC_Exercice$$

CREATE PROCEDURE Exporter_FEC_Exercice(
    IN p_societe_code VARCHAR(10),
    IN p_exercice_annee INT,
    IN p_fichier_path VARCHAR(500)
)
BEGIN
    DECLARE v_siren VARCHAR(9);
    DECLARE v_fichier VARCHAR(500);
    
    -- Récupérer le SIREN
    SELECT SIREN INTO v_siren
    FROM SOCIETES
    WHERE Code = p_societe_code;
    
    IF v_siren IS NULL THEN
        SET v_siren = '000000000';
    END IF;
    
    -- Construire le nom du fichier si non fourni
    IF p_fichier_path IS NULL OR p_fichier_path = '' THEN
        SET v_fichier = CONCAT('/tmp/FEC_', v_siren, '_', p_exercice_annee, '.txt');
    ELSE
        SET v_fichier = p_fichier_path;
    END IF;
    
    -- Exporter les données au format FEC
    SET @sql = CONCAT(
        "SELECT ",
        "j.Code AS JournalCode, ",
        "j.libelle AS JournalLib, ",
        "e.Numero AS EcritureNum, ",
        "DATE_FORMAT(e.date_ecriture, '%Y%m%d') AS EcritureDate, ",
        "m.compte_id AS CompteNum, ",
        "c.libelle AS CompteLib, ",
        "IFNULL(m.tiers_id, '') AS CompAuxNum, ",
        "IFNULL(t.Nom, '') AS CompAuxLib, ",
        "e.Reference AS piece_ref, ",
        "DATE_FORMAT(e.date_ecriture, '%Y%m%d') AS piece_date, ",
        "m.libelle AS EcritureLib, ",
        "FORMAT(m.Debit, 2) AS Debit, ",
        "FORMAT(m.Credit, 2) AS Credit, ",
        "IFNULL(m.Lettrage, '') AS EcritureLet, ",
        "IFNULL(DATE_FORMAT(m.DateLettrage, '%Y%m%d'), '') AS DateLet, ",
        "DATE_FORMAT(e.DateCreation, '%Y%m%d') AS ValidDate, ",
        "'' AS MontantDevise, ",
        "'' AS Idevise ",
        "INTO OUTFILE '", v_fichier, "' ",
        "FIELDS TERMINATED BY '|' ",
        "LINES TERMINATED BY '\n' ",
        "FROM MOUVEMENTS m ",
        "INNER JOIN ECRITURES e ON m.ecriture_id = e.Id ",
        "INNER JOIN JOURNAUX j ON e.journal_id = j.Id ",
        "INNER JOIN COMPTES c ON m.compte_id = c.Id ",
        "LEFT JOIN TIERS t ON m.tiers_id = t.Code ",
        "WHERE e.societe_id = '", p_societe_code, "' ",
        "AND e.exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = '", p_societe_code, "' AND Annee = ", p_exercice_annee, ") ",
        "ORDER BY j.Code, e.date_ecriture, e.Numero, m.Id"
    );
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    SELECT 
        v_fichier AS FichierExporte,
        v_siren AS SIREN,
        p_exercice_annee AS Exercice,
        'FEC généré avec succès' AS Message;
        
END$$

-- ============================================================
-- 3. Tester_Comptabilite_Avancee
-- ============================================================
-- Tests de cohérence comptable avancés
-- Vérifie l'équilibre, la TVA, les comptes, etc.
-- ============================================================

DROP PROCEDURE IF EXISTS Tester_Comptabilite_Avancee$$

CREATE PROCEDURE Tester_Comptabilite_Avancee(
    IN p_societe_code VARCHAR(10),
    IN p_exercice_annee INT
)
BEGIN
    DECLARE v_nb_ecritures_desequilibrees INT DEFAULT 0;
    DECLARE v_nb_comptes_invalides INT DEFAULT 0;
    DECLARE v_nb_classes_invalides INT DEFAULT 0;
    DECLARE v_balance_debit DECIMAL(15,2) DEFAULT 0;
    DECLARE v_balance_credit DECIMAL(15,2) DEFAULT 0;
    DECLARE v_tva_collectee DECIMAL(15,2) DEFAULT 0;
    DECLARE v_tva_deductible DECIMAL(15,2) DEFAULT 0;
    DECLARE v_nb_champs_vides INT DEFAULT 0;
    DECLARE v_total_tests INT DEFAULT 5;
    DECLARE v_tests_ok INT DEFAULT 0;
    
    -- Test 1 : Écritures équilibrées
    SELECT COUNT(DISTINCT e.Id) INTO v_nb_ecritures_desequilibrees
    FROM ECRITURES e
    INNER JOIN (
        SELECT ecriture_id, SUM(Debit) AS TotalDebit, SUM(Credit) AS TotalCredit
        FROM MOUVEMENTS
        GROUP BY ecriture_id
        HAVING ABS(SUM(Debit) - SUM(Credit)) > 0.01
    ) m ON e.Id = m.ecriture_id
    WHERE e.societe_id = p_societe_code
    AND e.exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee);
    
    IF v_nb_ecritures_desequilibrees = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;
    
    -- Test 2 : Comptes valides
    SELECT COUNT(*) INTO v_nb_comptes_invalides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.Id
    LEFT JOIN COMPTES c ON m.compte_id = c.Id AND c.societe_id = p_societe_code
    WHERE e.societe_id = p_societe_code
    AND e.exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee)
    AND c.Id IS NULL;
    
    IF v_nb_comptes_invalides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;
    
    -- Test 3 : Classes de comptes valides (1 à 7)
    SELECT COUNT(*) INTO v_nb_classes_invalides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.Id
    WHERE e.societe_id = p_societe_code
    AND e.exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee)
    AND LEFT(m.compte_id, 1) NOT IN ('1', '2', '3', '4', '5', '6', '7');
    
    IF v_nb_classes_invalides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;
    
    -- Test 4 : Cohérence de la TVA
    SELECT COALESCE(SUM(Credit - Debit), 0) INTO v_tva_collectee
    FROM BALANCE
    WHERE societe_id = p_societe_code
    AND exercice_annee = p_exercice_annee
    AND LEFT(compte_id, 4) = '4457';
    
    SELECT COALESCE(SUM(Debit - Credit), 0) INTO v_tva_deductible
    FROM BALANCE
    WHERE societe_id = p_societe_code
    AND exercice_annee = p_exercice_annee
    AND LEFT(compte_id, 4) = '4456';
    
    IF v_tva_collectee >= 0 AND v_tva_deductible >= 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;
    
    -- Test 5 : Champs obligatoires du FEC
    SELECT COUNT(*) INTO v_nb_champs_vides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.Id
    INNER JOIN JOURNAUX j ON e.journal_id = j.Id
    WHERE e.societe_id = p_societe_code
    AND e.exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee)
    AND (
        j.Code IS NULL OR j.Code = '' OR
        e.Numero IS NULL OR
        e.date_ecriture IS NULL OR
        m.compte_id IS NULL OR m.compte_id = '' OR
        e.Reference IS NULL OR e.Reference = '' OR
        m.libelle IS NULL OR m.libelle = ''
    );
    
    IF v_nb_champs_vides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;
    
    -- Récupérer les totaux de la balance
    SELECT 
        COALESCE(SUM(Debit), 0),
        COALESCE(SUM(Credit), 0)
    INTO v_balance_debit, v_balance_credit
    FROM BALANCE
    WHERE societe_id = p_societe_code
    AND exercice_annee = p_exercice_annee;
    
    -- Retourner les résultats
    SELECT
        v_tests_ok AS TestsOK,
        v_total_tests AS TestsTotal,
        v_nb_ecritures_desequilibrees AS EcrituresDesequilibrees,
        v_nb_comptes_invalides AS ComptesInvalides,
        v_nb_classes_invalides AS ClassesInvalides,
        v_tva_collectee AS TVACollectee,
        v_tva_deductible AS TVADeductible,
        v_nb_champs_vides AS ChampsFECVides,
        v_balance_debit AS BalanceDebit,
        v_balance_credit AS BalanceCredit,
        IF(v_tests_ok = v_total_tests, 'TOUS LES TESTS OK ✅', 'CERTAINS TESTS ONT ÉCHOUÉ ❌') AS Statut;
        
END$$

-- ============================================================
-- 4. AutoAudit_Cloture
-- ============================================================
-- Audit automatique avant clôture
-- Vérifie que tout est en ordre pour clôturer
-- ============================================================

DROP PROCEDURE IF EXISTS AutoAudit_Cloture$$

CREATE PROCEDURE AutoAudit_Cloture(
    IN p_societe_code VARCHAR(10),
    IN p_exercice_annee INT
)
BEGIN
    DECLARE v_nb_ecritures INT DEFAULT 0;
    DECLARE v_nb_ecritures_non_validees INT DEFAULT 0;
    DECLARE v_nb_ecritures_desequilibrees INT DEFAULT 0;
    DECLARE v_exercice_deja_cloture INT DEFAULT 0;
    DECLARE v_balance_ok INT DEFAULT 0;
    DECLARE v_total_checks INT DEFAULT 5;
    DECLARE v_checks_ok INT DEFAULT 0;
    DECLARE v_peut_cloturer BOOLEAN DEFAULT FALSE;
    
    -- Vérification 1 : Exercice non déjà clôturé
    SELECT COUNT(*) INTO v_exercice_deja_cloture
    FROM EXERCICES
    WHERE societe_id = p_societe_code
    AND Annee = p_exercice_annee
    AND Cloture = 1;
    
    IF v_exercice_deja_cloture = 0 THEN
        SET v_checks_ok = v_checks_ok + 1;
    END IF;
    
    -- Vérification 2 : Présence d'écritures
    SELECT COUNT(*) INTO v_nb_ecritures
    FROM ECRITURES
    WHERE societe_id = p_societe_code
    AND exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee);
    
    IF v_nb_ecritures > 0 THEN
        SET v_checks_ok = v_checks_ok + 1;
    END IF;
    
    -- Vérification 3 : Toutes les écritures validées
    SELECT COUNT(*) INTO v_nb_ecritures_non_validees
    FROM ECRITURES
    WHERE societe_id = p_societe_code
    AND exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee)
    AND Valide = 0;
    
    IF v_nb_ecritures_non_validees = 0 THEN
        SET v_checks_ok = v_checks_ok + 1;
    END IF;
    
    -- Vérification 4 : Écritures équilibrées
    SELECT COUNT(DISTINCT e.Id) INTO v_nb_ecritures_desequilibrees
    FROM ECRITURES e
    INNER JOIN (
        SELECT ecriture_id, SUM(Debit) AS TotalDebit, SUM(Credit) AS TotalCredit
        FROM MOUVEMENTS
        GROUP BY ecriture_id
        HAVING ABS(SUM(Debit) - SUM(Credit)) > 0.01
    ) m ON e.Id = m.ecriture_id
    WHERE e.societe_id = p_societe_code
    AND e.exercice_id IN (SELECT Id FROM EXERCICES WHERE societe_id = p_societe_code AND Annee = p_exercice_annee);
    
    IF v_nb_ecritures_desequilibrees = 0 THEN
        SET v_checks_ok = v_checks_ok + 1;
    END IF;
    
    -- Vérification 5 : Balance équilibrée
    SELECT COUNT(*) INTO v_balance_ok
    FROM (
        SELECT
            SUM(Debit) AS TotalDebit,
            SUM(Credit) AS TotalCredit,
            ABS(SUM(Debit) - SUM(Credit)) AS Difference
        FROM BALANCE
        WHERE societe_id = p_societe_code
        AND exercice_annee = p_exercice_annee
    ) b
    WHERE b.Difference < 0.01;
    
    IF v_balance_ok > 0 THEN
        SET v_checks_ok = v_checks_ok + 1;
    END IF;
    
    -- Déterminer si on peut clôturer
    SET v_peut_cloturer = (v_checks_ok = v_total_checks);
    
    -- Retourner les résultats
    SELECT
        v_checks_ok AS ChecksOK,
        v_total_checks AS ChecksTotal,
        v_peut_cloturer AS PeutCloturer,
        v_exercice_deja_cloture AS ExerciceDejaClot,
        v_nb_ecritures AS NombreEcritures,
        v_nb_ecritures_non_validees AS EcrituresNonValidees,
        v_nb_ecritures_desequilibrees AS EcrituresDesequilibrees,
        v_balance_ok AS BalanceOK,
        IF(v_peut_cloturer, '✅ PRÊT POUR LA CLÔTURE', '❌ CORRECTIONS NÉCESSAIRES') AS Statut,
        CASE
            WHEN v_exercice_deja_cloture > 0 THEN 'Exercice déjà clôturé'
            WHEN v_nb_ecritures = 0 THEN 'Aucune écriture à clôturer'
            WHEN v_nb_ecritures_non_validees > 0 THEN 'Certaines écritures non validées'
            WHEN v_nb_ecritures_desequilibrees > 0 THEN 'Certaines écritures déséquilibrées'
            WHEN v_balance_ok = 0 THEN 'Balance déséquilibrée'
            ELSE 'Toutes les vérifications OK'
        END AS Message;
        
END$$

DELIMITER ;

-- ============================================================
-- FIN DES PROCÉDURES STOCKÉES
-- ============================================================

SELECT '✅ Toutes les procédures stockées ont été créées avec succès !' AS Status;
