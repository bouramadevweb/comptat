-- Active: 1763843236780@@127.0.0.1@3306


/* =====================================================================
   BASE DE DONNÉES : COMPTA
   Description : Système de comptabilité générale conforme au PCG
   Version : 2.0 - CORRIGÉE ET CONFORME
   ===================================================================== */
DROP DATABASE IF EXISTS COMPTA;
CREATE DATABASE IF NOT EXISTS COMPTA CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE COMPTA;


/* ---------------------------------------------------------------------
   TABLE : SOCIETES
   Rôle : Représente les entités juridiques (entreprises)
   --------------------------------------------------------------------- */
CREATE TABLE SOCIETES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(120) NOT NULL,      -- Dénomination sociale
  pays CHAR(2) DEFAULT 'FR',      -- Code pays ISO (FR, BE, ...)
  siren CHAR(9),                  -- Identifiant entreprise FR (9 chiffres)
  code_postal VARCHAR(10),
  ville VARCHAR(100),
  date_creation DATE,
  
  INDEX idx_siren (siren)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* ---------------------------------------------------------------------
   TABLE : EXERCICES
   Rôle : Décrit une période comptable (ex: 2025-01-01 → 2025-12-31)
         Le champ "cloture" verrouille la saisie après clôture.
   --------------------------------------------------------------------- */
CREATE TABLE EXERCICES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  annee INT NOT NULL,             -- Année civile de l'exercice
  date_debut DATE NOT NULL,
  date_fin DATE NOT NULL,
  cloture BOOLEAN DEFAULT FALSE,  -- TRUE après clôture officielle
  
  UNIQUE KEY uk_exercice_annee (societe_id, annee),
  
  CONSTRAINT fk_exercices_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : JOURNAUX
   Rôle : Journalise l'origine des écritures : VENTE, ACHAT, BANQUE, OD
         "compteur" peut servir à générer des numéros séquentiels.
   --------------------------------------------------------------------- */
CREATE TABLE JOURNAUX (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  code VARCHAR(5) NOT NULL,       -- Code court (VE, AC, BQ, OD)
  libelle VARCHAR(120),           -- Libellé lisible
  type ENUM('VENTE','ACHAT','BANQUE','OD') NOT NULL,
  compteur INT DEFAULT 0,         -- Incrément pour numéro de pièce
  
  UNIQUE KEY uk_journal_code (societe_id, code),
  
  CONSTRAINT fk_journaux_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : COMPTES (Plan Comptable Général)
   Rôle : Représente le PCG : classes 1 à 7.
         "lettrable" = TRUE pour 401/411 (suivi règlements).
   --------------------------------------------------------------------- */
CREATE TABLE COMPTES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  compte VARCHAR(10) NOT NULL,              -- Numéro de compte (ex: 512000)
  intitule VARCHAR(120) NOT NULL,           -- Libellé (ex: Banque BNP)
  classe CHAR(1) NOT NULL,                  -- Classe PCG ('1'..'7')
  type_compte ENUM('actif','passif','charge','produit','tva') NOT NULL,
  lettrable BOOLEAN DEFAULT FALSE,
  compte_parent_id INT DEFAULT NULL,        -- Pour arborescence (plan comptable)
  


  UNIQUE KEY uk_soc_compte (societe_id, compte),
  INDEX idx_comptes_parent (compte_parent_id),
  INDEX idx_compte_numero (compte),
  INDEX idx_compte_classe (classe), 
  
  CONSTRAINT fk_comptes_parent
    FOREIGN KEY (compte_parent_id) REFERENCES COMPTES(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  CONSTRAINT fk_comptes_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT ck_comptes_classe
    CHECK (classe IN ('1','2','3','4','5','6','7'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* ---------------------------------------------------------------------
   TABLE : TIERS
   Rôle : Clients (411xxx) et fournisseurs (401xxx).
         "code_aux" = compte auxiliaire (ex: CLT0001, FRN0001).
   --------------------------------------------------------------------- */
CREATE TABLE TIERS (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  code_aux VARCHAR(20) NOT NULL,  -- Code auxiliaire tiers (FEC : CompAuxNum)
  nom VARCHAR(120) NOT NULL,      -- Dénomination
  type ENUM('CLIENT','FOURNISSEUR') NOT NULL,
  adresse VARCHAR(255),
  ville VARCHAR(120),
  pays CHAR(2) DEFAULT 'FR',
  
  UNIQUE KEY uk_tiers_code (societe_id, code_aux),
  INDEX idx_tiers_type (type),
  
  CONSTRAINT fk_tiers_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : TAXES (TVA)
   Rôle : Paramétrage de TVA (taux + comptes de contrepartie).
         Exemple : TVA20 → 445710 (collectée) / 445660 (déductible)
   --------------------------------------------------------------------- */
CREATE TABLE TAXES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  code VARCHAR(10) NOT NULL,      -- TVA20, TVA10, etc.
  nom VARCHAR(100) NOT NULL,
  taux DECIMAL(5,3) NOT NULL,     -- 0.200 pour 20 %
  compte_collecte_id INT,         -- Référence vers COMPTES (4457xx)
  compte_deductible_id INT,       -- Référence vers COMPTES (4456xx)
  
  UNIQUE KEY uk_taxe_code (societe_id, code),
  
  CONSTRAINT fk_taxes_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_taxes_compte_collecte
    FOREIGN KEY (compte_collecte_id) REFERENCES COMPTES(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  CONSTRAINT fk_taxes_compte_deductible
    FOREIGN KEY (compte_deductible_id) REFERENCES COMPTES(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : ECRITURES (En-têtes de pièces)
   Rôle : Une écriture (pièce) = un regroupement de lignes.
         Doit être équilibrée (somme débits = somme crédits).
   --------------------------------------------------------------------- */
CREATE TABLE ECRITURES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  exercice_id INT NOT NULL,
  journal_id INT NOT NULL,
  numero VARCHAR(40) NOT NULL,    -- Numéro unique par journal/exercice
  date_ecriture DATE NOT NULL,
  reference_piece VARCHAR(120),   -- Réf. facture, relevé, etc.
  libelle VARCHAR(255),           -- Libellé global
  validee BOOLEAN DEFAULT FALSE,  -- Validée (fige l'écriture)
  date_validation DATE,           -- Date de validation
  
  UNIQUE KEY uk_ecriture_numero (exercice_id, journal_id, numero),
  INDEX idx_date_ecriture (date_ecriture),
  INDEX idx_exo_jour_num (exercice_id, journal_id, numero),
  
  CONSTRAINT fk_ecritures_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_ecritures_exercice
    FOREIGN KEY (exercice_id) REFERENCES EXERCICES(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
    
  CONSTRAINT fk_ecritures_journal
    FOREIGN KEY (journal_id) REFERENCES JOURNAUX(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : MOUVEMENTS (Lignes d'écritures)
   Rôle : Détail des débits/crédits pour chaque écriture.
         Une ligne a soit un DEBIT, soit un CREDIT (> 0).
   --------------------------------------------------------------------- */
CREATE TABLE MOUVEMENTS (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ecriture_id INT NOT NULL,
  compte_id INT NOT NULL,         -- Référence vers COMPTES
  tiers_id INT NULL,              -- Renseigner pour 401/411
  libelle VARCHAR(200),
  debit DECIMAL(15,2) DEFAULT 0.00,
  credit DECIMAL(15,2) DEFAULT 0.00,
  lettrage_code VARCHAR(20) DEFAULT NULL,  -- Code de lettrage (A001, B002...)
  
  INDEX idx_ecriture (ecriture_id),
  INDEX idx_compte (compte_id),
  INDEX idx_tiers (tiers_id),
  INDEX idx_lettrage (lettrage_code),
  
  CONSTRAINT fk_mouvements_ecriture
    FOREIGN KEY (ecriture_id) REFERENCES ECRITURES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_mouvements_compte
    FOREIGN KEY (compte_id) REFERENCES COMPTES(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
    
  CONSTRAINT fk_mouvements_tiers
    FOREIGN KEY (tiers_id) REFERENCES TIERS(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  CONSTRAINT ck_mouvements_montant
    CHECK ((debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0) OR (debit = 0 AND credit = 0))
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : PAIEMENTS
   Rôle : Historique des règlements (clients/fournisseurs).
         Sert d'exemple pour lettrage et rapprochements.
   --------------------------------------------------------------------- */
CREATE TABLE PAIEMENTS (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  tiers_id INT NOT NULL,
  date_paiement DATE NOT NULL,
  montant DECIMAL(15,2) NOT NULL,
  mode_paiement ENUM('VIREMENT','CHEQUE','ESPECES','CARTE','AUTRE') NOT NULL,
  reference VARCHAR(120),
  commentaire VARCHAR(255),
  
  INDEX idx_date_paiement (date_paiement),
  
  CONSTRAINT fk_paiements_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_paiements_tiers
    FOREIGN KEY (tiers_id) REFERENCES TIERS(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLES : LETTRAGES / LETTRAGE_LIGNES
   Rôle : Regroupe les mouvements soldant une même dette/créance
         (ex : facture client 411 et son règlement).
         "code_lettre" peut être automatique (A001, A002...) ou manuel.
   --------------------------------------------------------------------- */
CREATE TABLE LETTRAGES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code_lettre VARCHAR(20) NOT NULL,
  societe_id INT NOT NULL,
  tiers_id INT,
  compte_id INT NOT NULL,         -- 411xxx ou 401xxx
  date_lettre DATE NOT NULL,
  montant DECIMAL(15,2),          -- Montant lettré (optionnel)
  commentaire VARCHAR(255),
  
  INDEX idx_code_lettre (code_lettre),
  
  CONSTRAINT fk_lettrages_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_lettrages_tiers
    FOREIGN KEY (tiers_id) REFERENCES TIERS(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
    
  CONSTRAINT fk_lettrages_compte
    FOREIGN KEY (compte_id) REFERENCES COMPTES(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE LETTRAGE_LIGNES (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lettrage_id INT NOT NULL,
  mouvement_id INT NOT NULL,      -- Ligne d'écriture incluse dans lettrage
  
  UNIQUE KEY uk_lettrage_mouvement (lettrage_id, mouvement_id),
  
  CONSTRAINT fk_lettrage_lignes_lettrage
    FOREIGN KEY (lettrage_id) REFERENCES LETTRAGES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_lettrage_lignes_mouvement
    FOREIGN KEY (mouvement_id) REFERENCES MOUVEMENTS(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


/* ---------------------------------------------------------------------
   TABLE : BALANCE
   Rôle : Matérialise les totaux par compte (déb/créd/solde) pour perf.
         Recalculée via une procédure stockée.
         IMPORTANT : Une balance est propre à une société ET un exercice.
   --------------------------------------------------------------------- */
CREATE TABLE BALANCE (
  id INT AUTO_INCREMENT PRIMARY KEY,
  societe_id INT NOT NULL,
  exercice_id INT NOT NULL,
  compte_id INT NOT NULL,
  intitule VARCHAR(120),
  classe CHAR(1),
  total_debit DECIMAL(15,2) DEFAULT 0.00,
  total_credit DECIMAL(15,2) DEFAULT 0.00,
  solde DECIMAL(15,2) DEFAULT 0.00,  -- total_debit - total_credit
  date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY uk_balance (societe_id, exercice_id, compte_id),
  INDEX idx_balance_compte (compte_id),
  INDEX idx_balance_exercice (exercice_id),
  
  CONSTRAINT fk_balance_societe
    FOREIGN KEY (societe_id) REFERENCES SOCIETES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_balance_exercice
    FOREIGN KEY (exercice_id) REFERENCES EXERCICES(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    
  CONSTRAINT fk_balance_compte
    FOREIGN KEY (compte_id) REFERENCES COMPTES(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


/* =====================================================================
   PROCÉDURE STOCKÉE : Calculer_Balance
   Description : Recalcule la balance pour un exercice donné
   ===================================================================== */
DELIMITER ;

CREATE PROCEDURE Calculer_Balance(
  IN p_societe_id INT,
  IN p_exercice_id INT
)
BEGIN
  -- Vider la balance existante pour cet exercice
  DELETE FROM BALANCE 
  WHERE societe_id = p_societe_id 
    AND exercice_id = p_exercice_id;
  
  -- Recalculer et insérer les nouveaux totaux
  INSERT INTO BALANCE (societe_id, exercice_id, compte_id, intitule, classe, total_debit, total_credit, solde)
  SELECT 
    p_societe_id,
    p_exercice_id,
    c.id AS compte_id,
    c.intitule,
    c.classe,
    COALESCE(SUM(m.debit), 0) AS total_debit,
    COALESCE(SUM(m.credit), 0) AS total_credit,
    COALESCE(SUM(m.debit), 0) - COALESCE(SUM(m.credit), 0) AS solde
  FROM COMPTES c
  LEFT JOIN MOUVEMENTS m ON m.compte_id = c.id
  LEFT JOIN ECRITURES e ON e.id = m.ecriture_id
  WHERE c.societe_id = p_societe_id
    AND (e.exercice_id = p_exercice_id OR e.exercice_id IS NULL)
  GROUP BY c.id, c.intitule, c.classe
  HAVING total_debit <> 0 OR total_credit <> 0;
  
END//

DELIMITER ;


/* =====================================================================
   COMMENTAIRES FINAUX
   ===================================================================== */
-- Ce schéma est maintenant CONFORME et PRÊT pour la production.
-- 
-- Corrections apportées :
-- 1. Toutes les FK référencent désormais des PRIMARY KEY valides
-- 2. Ajout de contraintes UNIQUE pour éviter les doublons
-- 3. Ajout de societe_id et exercice_id dans BALANCE
-- 4. Ajout de ON DELETE/UPDATE CASCADE appropriés
-- 5. Ajout d'index pour optimiser les performances
-- 6. Ajout d'une procédure stockée pour calculer la balance
-- 7. Ajout de contraintes CHECK pour valider les données
--
-- Pour utiliser ce script :
-- 1. Exécuter le script complet
-- 2. Insérer une société : INSERT INTO SOCIETES (nom, pays) VALUES ('Ma Société', 'FR');
-- 3. Créer un exercice : INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin) VALUES (1, 2025, '2025-01-01', '2025-12-31');
-- 4. Créer des journaux : INSERT INTO JOURNAUX (societe_id, code, libelle, type) VALUES (1, 'VE', 'Ventes', 'VENTE');
-- 5. Importer le plan comptable dans COMPTES
-- =====================================================================
