-- ==========================================
-- CORRECTION DES PROCÉDURES STOCKÉES
-- Mise à jour PascalCase → snake_case
-- Date: 23 novembre 2025
-- ==========================================

USE Comptabilite;

DELIMITER //

-- ==========================================
-- PROCÉDURE: TesterComptabilite (CORRIGÉE)
-- ==========================================

DROP PROCEDURE IF EXISTS TesterComptabilite //

CREATE PROCEDURE TesterComptabilite(
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

    -- Test 1 : Écritures équilibrées (CORRIGÉ: EcritureId → ecriture_id)
    SELECT COUNT(DISTINCT e.id) INTO v_nb_ecritures_desequilibrees
    FROM ECRITURES e
    INNER JOIN (
        SELECT ecriture_id, SUM(debit) AS total_debit, SUM(credit) AS total_credit
        FROM MOUVEMENTS
        GROUP BY ecriture_id
        HAVING ABS(SUM(debit) - SUM(credit)) > 0.01
    ) m ON e.id = m.ecriture_id
    WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code)
    AND e.exercice_id IN (SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code) AND annee = p_exercice_annee);

    IF v_nb_ecritures_desequilibrees = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 2 : Comptes valides (CORRIGÉ)
    SELECT COUNT(*) INTO v_nb_comptes_invalides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code)
    AND e.exercice_id IN (SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code) AND annee = p_exercice_annee)
    AND m.compte_id NOT IN (SELECT id FROM COMPTES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code));

    IF v_nb_comptes_invalides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 3 : Classes comptables valides (CORRIGÉ)
    SELECT COUNT(*) INTO v_nb_classes_invalides
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    INNER JOIN COMPTES c ON m.compte_id = c.id
    WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code)
    AND e.exercice_id IN (SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code) AND annee = p_exercice_annee)
    AND LEFT(c.compte, 1) NOT IN ('1', '2', '3', '4', '5', '6', '7');

    IF v_nb_classes_invalides = 0 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 4 : Balance équilibrée (CORRIGÉ)
    SELECT
        COALESCE(SUM(m.debit), 0),
        COALESCE(SUM(m.credit), 0)
    INTO v_balance_debit, v_balance_credit
    FROM MOUVEMENTS m
    INNER JOIN ECRITURES e ON m.ecriture_id = e.id
    WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code)
    AND e.exercice_id IN (SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code) AND annee = p_exercice_annee)
    AND e.validee = 1;

    IF ABS(v_balance_debit - v_balance_credit) < 0.01 THEN
        SET v_tests_ok = v_tests_ok + 1;
    END IF;

    -- Test 5 : Champs obligatoires (CORRIGÉ)
    SELECT COUNT(*) INTO v_nb_champs_vides
    FROM ECRITURES e
    WHERE e.societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code)
    AND e.exercice_id IN (SELECT id FROM EXERCICES WHERE societe_id = (SELECT id FROM SOCIETES WHERE code = p_societe_code) AND annee = p_exercice_annee)
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
END //

DELIMITER ;

-- ==========================================
-- VÉRIFICATION
-- ==========================================

SELECT 'Procédures stockées corrigées avec succès!' as message;

-- Test rapide si vous avez des données
-- CALL TesterComptabilite('SOC001', 2025);
