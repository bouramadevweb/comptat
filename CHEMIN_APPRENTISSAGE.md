# Chemin d’apprentissage – Comptabilité Python

## Objectifs
- Comprendre le schéma de données comptable (PCG) et les procédures stockées.
- Manipuler la base en SQL et via Python (DAO, services).
- Maîtriser l’architecture en couches (domaine, application, infrastructure, présentation).
- Écrire des tests simples (intégration).

## Pré-requis
- MySQL/MariaDB installé, accès à la base `COMPTA`.
- Python 3 et `pip install -r requirements.txt`.
- Scripts SQL alignés (entity.sql + procedures_stockees.sql + fix_all_procedures.sql appliqués).

---

## Étape 1 : Modèle de données & SQL
- **Lire** `sql/entity.sql` : tables SOCIETES, EXERCICES, JOURNAUX, COMPTES, TIERS, ECRITURES, MOUVEMENTS, BALANCE.
- **Lire** `sql/procedures_stockees.sql` : procédures de clôture, FEC, tests de cohérence.
- **Exercices** :
  1. Rejouer `entity.sql` puis `procedures_stockees.sql` sur une base de test (`SOURCE ...`).
  2. Insérer en SQL une société, un exercice, des journaux (VENTE/ACHAT), un compte client 411000, un compte fournisseur 401000, une vente simple (2 lignes équilibrées).
  3. Appeler `CALL Calculer_Balance(...);` et vérifier `BALANCE`.

## Étape 2 : Python & DAO
- **Lire** `src/infrastructure/persistence/database.py` (DatabaseManager) et `src/domain/models.py` (dataclasses).
- **Lire** `src/infrastructure/persistence/dao.py` : méthodes SocieteDAO, EcritureDAO, etc.
- **Exercice** :
  1. Écrire un petit script (hors UI) qui liste les journaux (`get_journaux`) et poste une écriture simple via `EcritureDAO`.
  2. Vérifier en SQL que l’écriture est créée.

## Étape 3 : Services & cas d’usage
- **Lire** `src/application/services.py` : orchestration avec validation/constantes.
- **Lire** `src/domain/repositories.py` : interfaces utilisées par les services.
- **Exercice** :
  1. Ajouter une méthode simple (ex. `get_journaux_par_type`) : interface → implémentation DAO → exposition dans le service → appel depuis un petit script.
  2. Tester `creer_ecriture_vente` et `creer_ecriture_achat` en script, voir les messages en cas de comptes manquants.

## Étape 4 : Présentation & UI
- **Lire** `src/presentation/gui_main.py`, `gui_vente.py`, `gui_achat.py`.
- **Exercice** :
  1. Lancer l’UI (`python main.py`), vérifier la liste des journaux/tiers, saisir une vente et un achat.
  2. Ouvrir le Grand Livre (`gui_grand_livre.py`) et afficher “Tous les comptes”.

## Étape 5 : Tests & cohérence
- **Lire** `tests/test_services.py` (si présent) et voir comment instancier le service.
- **Exercice** :
  1. Écrire un test d’intégration qui crée une vente, une achat, appelle `Calculer_Balance` et vérifie le total charges/produits.
  2. Appeler `Tester_Comptabilite_Avancee` et afficher son résultat.

## Étape 6 : Sécurité & audits (optionnel)
- **Lire** `src/infrastructure/security/auth_service.py`, `audit_service.py`, `decorators.py`.
- **Exercice** :
  1. Ajouter un décorateur simple qui logge les appels de service.
  2. Simuler un utilisateur/role et contrôler l’accès à une méthode (exemple pédagogique).

---

## Rappels pratiques
- Recharger des procédures corrigées : `mysql -u <user> -p -h <host> -D COMPTA -e "SOURCE /chemin/procedures_stockees.sql"`
- Vérifier les procédures : `SHOW PROCEDURE STATUS WHERE Db = 'COMPTA';`
- Vérifier le plan comptable : `SELECT compte, intitule FROM COMPTES WHERE societe_id=1;`
- Logs appli : `compta.log` (root du projet).

## Prochaines idées
- Ajouter des types de journaux supplémentaires (CAISSE/AN) si besoin (mettre à jour l’ENUM dans entity.sql et les constantes).
- Ajouter un export grand livre en CSV/Excel global.
- Mettre en place une suite de tests automatisés (pytest) pour les services clés.
