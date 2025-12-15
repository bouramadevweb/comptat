#!/usr/bin/env python3
"""
Script d'initialisation d'une nouvelle société
Crée automatiquement :
- La société
- L'exercice comptable
- Le plan comptable général (PCG)
- Les journaux standards
- Les taux de TVA
- Des tiers exemples
"""

import sys
from datetime import date
from decimal import Decimal
from src.infrastructure.persistence.database import DatabaseManager
from src.domain.models import Societe, Exercice, Journal, Compte, Taxe, Tiers


class InitialisationSociete:
    """Classe pour initialiser une société complète"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def creer_societe_complete(
        self,
        nom_societe: str,
        siren: str,
        adresse: str,
        code_postal: str,
        ville: str,
        annee_exercice: int = None
    ):
        """
        Crée une société complète avec tous ses éléments

        Returns:
            Tuple (societe_id, exercice_id, message)
        """
        if annee_exercice is None:
            annee_exercice = date.today().year

        try:
            self.db.connect()

            print("\n🏢 Création de la société...")
            societe_id = self._creer_societe(nom_societe, siren, adresse, code_postal, ville)
            print(f"   ✅ Société créée (ID: {societe_id})")

            print("\n📅 Création de l'exercice comptable...")
            exercice_id = self._creer_exercice(societe_id, annee_exercice)
            print(f"   ✅ Exercice créé (ID: {exercice_id})")

            print("\n📚 Création des journaux...")
            self._creer_journaux(societe_id)
            print("   ✅ Journaux créés (VE, AC, BQ, OD)")

            print("\n📊 Création du plan comptable...")
            nb_comptes = self._creer_plan_comptable(societe_id)
            print(f"   ✅ {nb_comptes} comptes créés")

            print("\n💰 Création des taux de TVA...")
            self._creer_taux_tva(societe_id)
            print("   ✅ Taux TVA créés (20%, 10%, 5.5%, 2.1%)")

            print("\n👥 Création des tiers exemples...")
            self._creer_tiers_exemples(societe_id)
            print("   ✅ Tiers exemples créés")

            message = f"✅ SOCIÉTÉ INITIALISÉE AVEC SUCCÈS !\n\n"
            message += f"📊 Société : {nom_societe}\n"
            message += f"📅 Exercice : {annee_exercice}\n"
            message += f"🏢 ID Société : {societe_id}\n"
            message += f"📆 ID Exercice : {exercice_id}\n"

            return societe_id, exercice_id, message

        except Exception as e:
            return None, None, f"❌ Erreur lors de l'initialisation : {str(e)}"
        finally:
            self.db.disconnect()

    def _creer_societe(self, nom, siren, adresse, code_postal, ville):
        """Crée la société dans la base"""
        query = """
            INSERT INTO SOCIETES (nom, pays, siren, code_postal, ville, date_creation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (nom, 'FR', siren, code_postal, ville, date.today()))
            return cursor.lastrowid

    def _creer_exercice(self, societe_id, annee):
        """Crée l'exercice comptable"""
        date_debut = date(annee, 1, 1)
        date_fin = date(annee, 12, 31)

        query = """
            INSERT INTO EXERCICES (societe_id, annee, date_debut, date_fin, cloture)
            VALUES (%s, %s, %s, %s, %s)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (societe_id, annee, date_debut, date_fin, False))
            return cursor.lastrowid

    def _creer_journaux(self, societe_id):
        """Crée les journaux standards"""
        journaux = [
            ('VE', 'Journal des ventes', 'VENTE'),
            ('AC', 'Journal des achats', 'ACHAT'),
            ('BQ', 'Journal de banque', 'BANQUE'),
            ('OD', 'Opérations diverses', 'OD'),
        ]

        query = """
            INSERT INTO JOURNAUX (societe_id, code, libelle, type, compteur)
            VALUES (%s, %s, %s, %s, 0)
        """

        with self.db.get_cursor() as cursor:
            for code, libelle, type_journal in journaux:
                cursor.execute(query, (societe_id, code, libelle, type_journal))

    def _creer_plan_comptable(self, societe_id):
        """Crée le plan comptable général"""
        comptes = self._get_plan_comptable_complet()

        query = """
            INSERT INTO COMPTES (societe_id, compte, intitule, classe, type_compte, lettrable)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        with self.db.get_cursor() as cursor:
            for compte_data in comptes:
                cursor.execute(query, (societe_id, *compte_data))

        return len(comptes)

    def _get_plan_comptable_complet(self):
        """Retourne le plan comptable complet"""
        return [
            # CLASSE 1 : CAPITAUX
            ('101000', 'Capital social', '1', 'passif', False),
            ('106000', 'Réserves', '1', 'passif', False),
            ('108000', 'Compte de l\'exploitant', '1', 'passif', False),
            ('110000', 'Report à nouveau (solde créditeur)', '1', 'passif', False),
            ('119000', 'Report à nouveau (solde débiteur)', '1', 'passif', False),
            ('120000', 'Résultat de l\'exercice (bénéfice)', '1', 'passif', False),
            ('129000', 'Résultat de l\'exercice (perte)', '1', 'passif', False),
            ('151000', 'Provisions pour risques', '1', 'passif', False),
            ('164000', 'Emprunts auprès des établissements de crédit', '1', 'passif', False),
            ('168000', 'Autres emprunts et dettes', '1', 'passif', False),

            # CLASSE 2 : IMMOBILISATIONS
            ('201000', 'Frais d\'établissement', '2', 'actif', False),
            ('205000', 'Concessions et droits similaires', '2', 'actif', False),
            ('206000', 'Droit au bail', '2', 'actif', False),
            ('207000', 'Fonds commercial', '2', 'actif', False),
            ('208000', 'Autres immobilisations incorporelles', '2', 'actif', False),
            ('211000', 'Terrains', '2', 'actif', False),
            ('213000', 'Constructions', '2', 'actif', False),
            ('215000', 'Installations techniques, matériel et outillage', '2', 'actif', False),
            ('218100', 'Matériel de transport', '2', 'actif', False),
            ('218300', 'Matériel de bureau et informatique', '2', 'actif', False),
            ('218400', 'Mobilier', '2', 'actif', False),
            ('218500', 'Matériel et outillage', '2', 'actif', False),
            ('261000', 'Titres de participation', '2', 'actif', False),
            ('271000', 'Titres immobilisés', '2', 'actif', False),
            ('275000', 'Dépôts et cautionnements versés', '2', 'actif', False),
            ('280000', 'Amortissements des immobilisations incorporelles', '2', 'passif', False),
            ('281000', 'Amortissements des immobilisations corporelles', '2', 'passif', False),
            ('290000', 'Dépréciation des immobilisations incorporelles', '2', 'actif', False),
            ('291000', 'Dépréciation des immobilisations corporelles', '2', 'actif', False),

            # CLASSE 3 : STOCKS
            ('311000', 'Matières premières', '3', 'actif', False),
            ('321000', 'Matières consommables', '3', 'actif', False),
            ('355000', 'Produits finis', '3', 'actif', False),
            ('371000', 'Stocks de marchandises', '3', 'actif', False),
            ('391000', 'Dépréciation des stocks', '3', 'actif', False),

            # CLASSE 4 : TIERS
            ('400000', 'Fournisseurs et comptes rattachés', '4', 'passif', False),
            ('401000', 'Fournisseurs', '4', 'passif', True),
            ('408000', 'Fournisseurs - Factures non parvenues', '4', 'passif', False),
            ('409000', 'Fournisseurs débiteurs', '4', 'actif', False),
            ('410000', 'Clients et comptes rattachés', '4', 'actif', False),
            ('411000', 'Clients', '4', 'actif', True),
            ('416000', 'Clients douteux ou litigieux', '4', 'actif', False),
            ('418000', 'Clients - Produits à recevoir', '4', 'actif', False),
            ('419000', 'Clients créditeurs', '4', 'passif', False),
            ('421000', 'Personnel - Rémunérations dues', '4', 'passif', False),
            ('422000', 'Comités d\'entreprise', '4', 'passif', False),
            ('424000', 'Participation des salariés', '4', 'passif', False),
            ('425000', 'Personnel - Avances et acomptes', '4', 'actif', False),
            ('427000', 'Personnel - Oppositions', '4', 'passif', False),
            ('428000', 'Personnel - Charges à payer', '4', 'passif', False),
            ('431000', 'Sécurité sociale', '4', 'passif', False),
            ('437000', 'Autres organismes sociaux', '4', 'passif', False),
            ('438000', 'Organismes sociaux - Charges à payer', '4', 'passif', False),
            ('441000', 'État - Subventions à recevoir', '4', 'actif', False),
            ('442000', 'État - Impôts et taxes recouvrables', '4', 'actif', False),
            ('443000', 'Opérations particulières avec l\'État', '4', 'actif', False),
            ('444000', 'État - Impôts sur les bénéfices', '4', 'passif', False),
            ('445100', 'TVA à décaisser', '4', 'passif', False),
            ('445510', 'TVA à décaisser', '4', 'passif', False),
            ('445620', 'TVA sur immobilisations', '4', 'actif', False),
            ('445660', 'TVA déductible sur autres biens et services', '4', 'actif', False),
            ('445710', 'TVA collectée', '4', 'passif', False),
            ('445800', 'Taxes sur le chiffre d\'affaires à régulariser', '4', 'tva', False),
            ('447000', 'Autres impôts, taxes et versements assimilés', '4', 'passif', False),
            ('455000', 'Associés - Comptes courants', '4', 'passif', False),
            ('456000', 'Associés - Opérations sur le capital', '4', 'passif', False),
            ('457000', 'Associés - Dividendes à payer', '4', 'passif', False),
            ('462000', 'Créances douteuses', '4', 'actif', False),
            ('467000', 'Autres comptes débiteurs ou créditeurs', '4', 'actif', False),
            ('471000', 'Comptes d\'attente', '4', 'actif', False),
            ('486000', 'Charges constatées d\'avance', '4', 'actif', False),
            ('487000', 'Produits constatés d\'avance', '4', 'passif', False),
            ('491000', 'Dépréciation des comptes clients', '4', 'actif', False),

            # CLASSE 5 : FINANCIERS
            ('508000', 'Autres valeurs mobilières de placement', '5', 'actif', False),
            ('511000', 'Valeurs à l\'encaissement', '5', 'actif', False),
            ('512000', 'Banque', '5', 'actif', True),
            ('514000', 'Chèques postaux', '5', 'actif', False),
            ('530000', 'Caisse', '5', 'actif', False),
            ('531000', 'Caisse en euros', '5', 'actif', False),
            ('540000', 'Régies d\'avances et accréditifs', '5', 'actif', False),
            ('590000', 'Dépréciation des valeurs mobilières', '5', 'actif', False),

            # CLASSE 6 : CHARGES
            ('601000', 'Achats stockés - Matières premières', '6', 'charge', False),
            ('602000', 'Achats stockés - Autres approvisionnements', '6', 'charge', False),
            ('606000', 'Achats non stockés de matières et fournitures', '6', 'charge', False),
            ('607000', 'Achats de marchandises', '6', 'charge', False),
            ('608000', 'Frais accessoires d\'achat', '6', 'charge', False),
            ('609000', 'Rabais, remises et ristournes obtenus', '6', 'charge', False),
            ('611000', 'Sous-traitance générale', '6', 'charge', False),
            ('612000', 'Redevances de crédit-bail', '6', 'charge', False),
            ('613000', 'Locations', '6', 'charge', False),
            ('613200', 'Locations immobilières', '6', 'charge', False),
            ('613500', 'Locations mobilières', '6', 'charge', False),
            ('614000', 'Charges locatives et de copropriété', '6', 'charge', False),
            ('615000', 'Entretien et réparations', '6', 'charge', False),
            ('616000', 'Primes d\'assurance', '6', 'charge', False),
            ('618000', 'Divers', '6', 'charge', False),
            ('621000', 'Personnel extérieur à l\'entreprise', '6', 'charge', False),
            ('622000', 'Rémunérations d\'intermédiaires et honoraires', '6', 'charge', False),
            ('622200', 'Honoraires', '6', 'charge', False),
            ('623000', 'Publicité, publications, relations publiques', '6', 'charge', False),
            ('624000', 'Transports de biens et transport collectif du personnel', '6', 'charge', False),
            ('625000', 'Déplacements, missions et réceptions', '6', 'charge', False),
            ('626000', 'Frais postaux et de télécommunications', '6', 'charge', False),
            ('627000', 'Services bancaires et assimilés', '6', 'charge', False),
            ('628000', 'Divers', '6', 'charge', False),
            ('631000', 'Impôts, taxes et versements assimilés sur rémunérations', '6', 'charge', False),
            ('633000', 'Impôts, taxes et versements assimilés sur rémunérations', '6', 'charge', False),
            ('635000', 'Autres impôts, taxes et versements assimilés', '6', 'charge', False),
            ('637000', 'Autres impôts, taxes et versements assimilés', '6', 'charge', False),
            ('641000', 'Rémunérations du personnel', '6', 'charge', False),
            ('645000', 'Charges de sécurité sociale et de prévoyance', '6', 'charge', False),
            ('646000', 'Cotisations sociales personnelles de l\'exploitant', '6', 'charge', False),
            ('647000', 'Autres charges sociales', '6', 'charge', False),
            ('648000', 'Autres charges de personnel', '6', 'charge', False),
            ('651000', 'Redevances pour concessions, brevets, licences', '6', 'charge', False),
            ('661000', 'Charges d\'intérêts', '6', 'charge', False),
            ('665000', 'Escomptes accordés', '6', 'charge', False),
            ('667000', 'Charges nettes sur cessions de valeurs mobilières', '6', 'charge', False),
            ('668000', 'Autres charges financières', '6', 'charge', False),
            ('671000', 'Charges exceptionnelles sur opérations de gestion', '6', 'charge', False),
            ('675000', 'Valeurs comptables des éléments d\'actif cédés', '6', 'charge', False),
            ('678000', 'Autres charges exceptionnelles', '6', 'charge', False),
            ('681000', 'Dotations aux amortissements', '6', 'charge', False),
            ('686000', 'Dotations aux dépréciations', '6', 'charge', False),
            ('687000', 'Dotations aux provisions', '6', 'charge', False),
            ('691000', 'Participation des salariés', '6', 'charge', False),
            ('695000', 'Impôts sur les bénéfices', '6', 'charge', False),
            ('697000', 'Imposition forfaitaire annuelle', '6', 'charge', False),
            ('699000', 'Produits - Reports en arrière des déficits', '6', 'charge', False),

            # CLASSE 7 : PRODUITS
            ('701000', 'Ventes de produits finis', '7', 'produit', False),
            ('703000', 'Ventes de produits résiduels', '7', 'produit', False),
            ('706000', 'Prestations de services', '7', 'produit', False),
            ('707000', 'Ventes de marchandises', '7', 'produit', False),
            ('708000', 'Produits des activités annexes', '7', 'produit', False),
            ('709000', 'Rabais, remises et ristournes accordés', '7', 'produit', False),
            ('713000', 'Variation des stocks (en-cours de production)', '7', 'produit', False),
            ('721000', 'Production immobilisée - Immobilisations incorporelles', '7', 'produit', False),
            ('722000', 'Production immobilisée - Immobilisations corporelles', '7', 'produit', False),
            ('740000', 'Subventions d\'exploitation', '7', 'produit', False),
            ('754000', 'Ristournes perçues des coopératives', '7', 'produit', False),
            ('755000', 'Quotes-parts de résultat sur opérations faites en commun', '7', 'produit', False),
            ('758000', 'Produits divers de gestion courante', '7', 'produit', False),
            ('761000', 'Produits de participations', '7', 'produit', False),
            ('762000', 'Produits des autres immobilisations financières', '7', 'produit', False),
            ('764000', 'Revenus des valeurs mobilières de placement', '7', 'produit', False),
            ('765000', 'Escomptes obtenus', '7', 'produit', False),
            ('767000', 'Produits nets sur cessions de valeurs mobilières', '7', 'produit', False),
            ('768000', 'Autres produits financiers', '7', 'produit', False),
            ('771000', 'Produits exceptionnels sur opérations de gestion', '7', 'produit', False),
            ('775000', 'Produits des cessions d\'éléments d\'actif', '7', 'produit', False),
            ('777000', 'Quote-part des subventions d\'investissement', '7', 'produit', False),
            ('778000', 'Autres produits exceptionnels', '7', 'produit', False),
            ('781000', 'Reprises sur amortissements et provisions', '7', 'produit', False),
            ('786000', 'Reprises sur dépréciations', '7', 'produit', False),
            ('787000', 'Reprises sur provisions', '7', 'produit', False),
            ('791000', 'Transferts de charges d\'exploitation', '7', 'produit', False),
            ('796000', 'Transferts de charges financières', '7', 'produit', False),
            ('797000', 'Transferts de charges exceptionnelles', '7', 'produit', False),
        ]

    def _creer_taux_tva(self, societe_id):
        """Crée les taux de TVA standards"""
        # D'abord récupérer les IDs des comptes de TVA
        query_compte = "SELECT id FROM COMPTES WHERE societe_id = %s AND compte = %s"

        with self.db.get_cursor() as cursor:
            # Compte TVA collectée
            cursor.execute(query_compte, (societe_id, '445710'))
            compte_collecte = cursor.fetchone()
            compte_collecte_id = compte_collecte['id'] if compte_collecte else None

            # Compte TVA déductible
            cursor.execute(query_compte, (societe_id, '445660'))
            compte_deductible = cursor.fetchone()
            compte_deductible_id = compte_deductible['id'] if compte_deductible else None

        # Créer les taux de TVA
        taux_tva = [
            ('TVA20', 'TVA 20%', Decimal('0.200')),
            ('TVA10', 'TVA 10%', Decimal('0.100')),
            ('TVA055', 'TVA 5.5%', Decimal('0.055')),
            ('TVA021', 'TVA 2.1%', Decimal('0.021')),
        ]

        query = """
            INSERT INTO TAXES (societe_id, code, nom, taux, compte_collecte_id, compte_deductible_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        with self.db.get_cursor() as cursor:
            for code, nom, taux in taux_tva:
                cursor.execute(query, (
                    societe_id, code, nom, taux,
                    compte_collecte_id, compte_deductible_id
                ))

    def _creer_tiers_exemples(self, societe_id):
        """Crée quelques tiers exemples"""
        tiers = [
            ('CLT0001', 'Client Exemple 1', 'CLIENT', '123 Rue de Paris', 'Paris'),
            ('CLT0002', 'Client Exemple 2', 'CLIENT', '45 Avenue Lyon', 'Lyon'),
            ('FRN0001', 'Fournisseur Exemple 1', 'FOURNISSEUR', '78 Bd Marseille', 'Marseille'),
            ('FRN0002', 'Fournisseur Exemple 2', 'FOURNISSEUR', '90 Place Toulouse', 'Toulouse'),
        ]

        query = """
            INSERT INTO TIERS (societe_id, code_aux, nom, type, adresse, ville, pays)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        with self.db.get_cursor() as cursor:
            for code_aux, nom, type_tiers, adresse, ville in tiers:
                cursor.execute(query, (societe_id, code_aux, nom, type_tiers, adresse, ville, 'FR'))


def main():
    """Fonction principale en mode interactif"""
    print("=" * 60)
    print("   INITIALISATION D'UNE NOUVELLE SOCIÉTÉ")
    print("=" * 60)
    print()

    # Demander les informations
    nom_societe = input("Nom de la société : ").strip()
    if not nom_societe:
        print("❌ Le nom de la société est obligatoire")
        sys.exit(1)

    siren = input("SIREN (9 chiffres) : ").strip()
    adresse = input("Adresse : ").strip()
    code_postal = input("Code postal : ").strip()
    ville = input("Ville : ").strip()

    annee_input = input(f"Année de l'exercice (Enter = {date.today().year}) : ").strip()
    annee_exercice = int(annee_input) if annee_input else date.today().year

    # Afficher un résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Société      : {nom_societe}")
    print(f"SIREN        : {siren}")
    print(f"Adresse      : {adresse}")
    print(f"Code postal  : {code_postal}")
    print(f"Ville        : {ville}")
    print(f"Exercice     : {annee_exercice} (du 01/01/{annee_exercice} au 31/12/{annee_exercice})")
    print("=" * 60)

    confirmation = input("\n✅ Confirmer la création ? (o/N) : ").strip().lower()
    if confirmation != 'o':
        print("❌ Création annulée")
        sys.exit(0)

    # Créer la société
    print("\n🚀 Initialisation en cours...\n")

    db = DatabaseManager()
    init = InitialisationSociete(db)

    societe_id, exercice_id, message = init.creer_societe_complete(
        nom_societe=nom_societe,
        siren=siren,
        adresse=adresse,
        code_postal=code_postal,
        ville=ville,
        annee_exercice=annee_exercice
    )

    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)

    if societe_id:
        print("\n👉 Vous pouvez maintenant lancer l'application :")
        print("   python main.py")
        print()


if __name__ == "__main__":
    main()
