-- Active: 1763843236780@@127.0.0.1@3306@COMPTA
-- ==========================================
-- CORRECTION COMPLÈTE DES PROCÉDURES STOCKÉES
-- Conversion pour utiliser IDs au lieu de Codes
-- Date: 23 novembre 2025
-- ==========================================

USE COMPTA;

DELIMITER //

-- ==========================================
-- PROCÉDURE: Tester_Comptabilite_Avancee
-- CORRIGÉE pour utiliser societe_id et exercice_id
-- ==========================================

DROP PROCEDURE IF EXISTS Tester_Comptabilite_Avancee  ;

CREATE PROCEDURE Tester_Comptabilite_Avancee(
    IN p_societe_id INT,
    IN p_exercice_id INT
)
BEGIN
    DECLARE v_nb_ecritures_desequilibrees INT DEFAULT 0;
    DECLARE v_nb_comptes_invalides INT DEFAULT 0;
    DECLARE v_nb_classes_invalides INT DEFAULT 0;
    DECLARE v_balance_debit DECIMAL(15,2) DEFAULT 0;
    DECLARE v_balance_credit DECIMAL(15,2) DEFAULT 0;
    DECLARE v_nb_champs_vides INT DEFAULT 0;
    DECLARE v_total_tests INT DEFAULT 5;
    DECLARE v_tests_ok INT DEFAULT 0;

    -- Test 1 : Écritures équilibrées
    SELECT COUNT(DISTINCT e.id) INTO v_nb_ecritures_desequilibrees
    FROM ECRITURES e
    INNER JOIN (
        SELECT ecriture_id, SUM(debit) AS total_debit, SUM(credit) AS total_credit
        FROM MOUVEMENTS
        GROUP BY ecriture_id
        HAVING ABS(SUM(debit) - SUM(credit)) > 0.01
    ) m ON e.id = m.ecriture_id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id;

    IF v_nb_ecritures_desequilibrees = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 2 : Comptes valides
    SELECT COUNT(*) INTO v_nb_comptes_invalides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND m.compte_id NOT IN (SELECT id FROM COMPTES WHERE societe_id = p_societe_id);

    IF v_nb_comptes_invalides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 3 : Classes comptables valides
    SELECT COUNT(*) INTO v_nb_classes_invalides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    INNER JOIN COMPTES c ON m.compte_id = c.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND LEFT(c.compte, 1) NOT IN ('1', '2', '3', '4', '5', '6', '7');

    IF v_nb_classes_invalides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 4 : Balance équilibrée
    SELECT
        COALESCE(SUM(m.debit), 0),
        COALESCE(SUM(m.credit), 0)
    INTO v_balance_debit, v_balance_credit
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND e.validee = 1;

    IF ABS(v_balance_debit - v_balance_credit) < 0.01 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 5 : Champs obligatoires
    SELECT COUNT(*) INTO v_nb_champs_vides
    FROM ECRITURES e
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND (
          e.numero IS NULL OR e.numero = '' OR
          e.date_ecriture IS NULL OR
          e.journal_id IS NULL
      );

    IF v_nb_champs_vides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Résultat des tests
    SELECT
        'Tests de cohérence comptable' as test,
        v_tests_ok as tests_reussis,
        v_total_tests as tests_total,
        CASE WHEN v_tests_ok = v_total_tests THEN 'OK' ELSE 'ERREURS' END as resultat,
        CONCAT(
            'Écritures déséquilibrées: ', v_nb_ecritures_desequilibrees, ' | ',
            'Comptes invalides: ', v_nb_comptes_invalides, ' | ',
            'Classes invalides: ', v_nb_classes_invalides, ' | ',
            'Balance (D/C): ', v_balance_debit, '/', v_balance_credit, ' | ',
            'Champs vides: ', v_nb_champs_vides
        ) as details;
END ;

-- ==========================================
-- PROCÉDURE: Cloturer_Exercice
-- CORRIGÉE pour utiliser IDs
-- ==========================================

DROP PROCEDURE IF EXISTS Cloturer_Exercice ;

CREATE PROCEDURE Cloturer_Exercice(
    IN p_societe_id INT,
    IN p_exercice_id INT
)
BEGIN
    DECLARE v_total_produits DECIMAL(15,2) DEFAULT 0;
    DECLARE v_total_charges DECIMAL(15,2) DEFAULT 0;
    DECLARE v_resultat DECIMAL(15,2) DEFAULT 0;
    DECLARE v_compte_resultat_id INT;
    DECLARE v_ecriture_id INT;
    DECLARE v_nouveau_exercice_id INT;
    DECLARE v_journal_od_id INT;
    DECLARE v_date_cloture DATE;
    DECLARE v_exercice_annee INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Récupérer l'année de l'exercice
    SELECT annee, date_fin
    INTO v_exercice_annee, v_date_cloture
    FROM EXERCICES
    WHERE id = p_exercice_id;

    -- Vérifier que l'exercice n'est pas déjà clôturé
    IF EXISTS (SELECT 1 FROM EXERCICES WHERE id = p_exercice_id AND cloture = 1) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Exercice déjà clôturé';
    END IF;

    -- Calculer le résultat (Produits - Charges)
    SELECT
        COALESCE(SUM(CASE WHEN LEFT(c.compte, 1) = '7' THEN m.credit - m.debit ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN LEFT(c.compte, 1) = '6' THEN m.debit - m.credit ELSE 0 END), 0)
    INTO v_total_produits, v_total_charges
    FROM MOUVEMENTS m
    JOIN ECRITURES e ON m.ecriture_id = e.id
    JOIN COMPTES c ON m.compte_id = c.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND e.validee = 1;

    SET v_resultat = v_total_produits - v_total_charges;

    -- Récupérer le journal OD
    SELECT id INTO v_journal_od_id
    FROM JOURNAUX
    WHERE societe_id = p_societe_id
      AND type = 'od'
    LIMIT 1;

    -- Créer l'écriture de clôture
    INSERT INTO ECRITURES (
        societe_id, exercice_id, journal_id, date_ecriture,
        reference_piece, libelle, validee
    ) VALUES (
        p_societe_id,
        p_exercice_id,
        v_journal_od_id,
        v_date_cloture,
        CONCAT('CLOT', v_exercice_annee),
        CONCAT('Clôture exercice ', v_exercice_annee),
        1
    );

    SET v_ecriture_id = LAST_INSERT_ID();

    -- Solder les comptes de charges (Crédit classe 6)
    INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, debit, credit)
    SELECT
        v_ecriture_id,
        c.id,
        CONCAT('Solde ', c.compte),
        0,
        SUM(m.debit - m.credit)
    FROM MOUVEMENTS m
    JOIN ECRITURES e ON m.ecriture_id = e.id
    JOIN COMPTES c ON m.compte_id = c.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND e.validee = 1
      AND LEFT(c.compte, 1) = '6'
    GROUP BY c.id
    HAVING SUM(m.debit - m.credit) > 0;

    -- Solder les comptes de produits (Débit classe 7)
    INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, debit, credit)
    SELECT
        v_ecriture_id,
        c.id,
        CONCAT('Solde ', c.compte),
        SUM(m.credit - m.debit),
        0
    FROM MOUVEMENTS m
    JOIN ECRITURES e ON m.ecriture_id = e.id
    JOIN COMPTES c ON m.compte_id = c.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND e.validee = 1
      AND LEFT(c.compte, 1) = '7'
    GROUP BY c.id
    HAVING SUM(m.credit - m.debit) > 0;

    -- Inscrire le résultat (120000 pour bénéfice, 129000 pour perte)
    IF v_resultat >= 0 THEN
        SELECT id INTO v_compte_resultat_id FROM COMPTES WHERE societe_id = p_societe_id AND compte = '120000' LIMIT 1;
        INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, debit, credit)
        VALUES (v_ecriture_id, v_compte_resultat_id, CONCAT('Bénéfice ', v_exercice_annee), 0, v_resultat);
    ELSE
        SELECT id INTO v_compte_resultat_id FROM COMPTES WHERE societe_id = p_societe_id AND compte = '129000' LIMIT 1;
        INSERT INTO MOUVEMENTS (ecriture_id, compte_id, libelle, debit, credit)
        VALUES (v_ecriture_id, v_compte_resultat_id, CONCAT('Perte ', v_exercice_annee), ABS(v_resultat), 0);
    END IF;

    -- Marquer l'exercice comme clôturé
    UPDATE EXERCICES SET cloture = 1 WHERE id = p_exercice_id;

    COMMIT;

    SELECT 'Exercice clôturé avec succès' as message, v_resultat as resultat;
END ;

-- ==========================================
-- PROCÉDURE: Exporter_FEC
-- CORRIGÉE pour utiliser IDs
-- ==========================================

DROP PROCEDURE IF EXISTS Exporter_FEC ;

CREATE PROCEDURE Exporter_FEC(
    IN p_societe_id INT,
    IN p_exercice_id INT
)
BEGIN
    SELECT
        j.code as JournalCode,
        j.libelle as JournalLib,
        e.numero as EcritureNum,
        DATE_FORMAT(e.date_ecriture, '%Y%m%d') as EcritureDate,
        c.compte as CompteNum,
        c.intitule as CompteLib,
        COALESCE(t.code_aux, '') as CompAuxNum,
        COALESCE(t.nom, '') as CompAuxLib,
        COALESCE(e.reference_piece, '') as PieceRef,
        DATE_FORMAT(e.date_ecriture, '%Y%m%d') as PieceDate,
        m.libelle as EcritureLib,
        FORMAT(m.debit, 2, 'fr_FR') as Debit,
        FORMAT(m.credit, 2, 'fr_FR') as Credit,
        COALESCE(m.lettrage_code, '') as EcritureLet,
        '' as DateLet,
        DATE_FORMAT(e.date_validation, '%Y%m%d') as ValidDate,
        '' as Montantdevise,
        '' as Idevise
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    INNER JOIN JOURNAUX j ON e.journal_id = j.id
    INNER JOIN COMPTES c ON m.compte_id = c.id
    LEFT JOIN TIERS t ON m.tiers_id = t.id
    WHERE e.societe_id = p_societe_id
      AND e.exercice_id = p_exercice_id
      AND e.validee = 1
    ORDER BY e.date_ecriture, e.numero, m.id;
END ;

DELIMITER ;

-- ==========================================
-- VÉRIFICATION
-- ==========================================

SELECT 'Toutes les procédures stockées ont été corrigées avec succès!' as message;
SHOW PROCEDURE STATUS WHERE Db = 'COMPTA';
