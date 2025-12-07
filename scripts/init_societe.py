"""
Script d'initialisation d'une nouvelle société avec VALIDATION des types de comptes
Vérifie systématiquement la cohérence entre numéro de compte et type (actif/passif/charge/produit/tva)
"""
from datetime import date, timedelta
from decimal import Decimal
from src.infrastructure.factories import create_db_manager, create_service
from src.infrastructure.persistence.setup_repository import SetupRepository
from src.domain.models import Societe, Exercice, Journal, Compte, Taxe


class ValidationError(Exception):
    """Exception levée en cas d'erreur de validation"""
    pass


class ValidateurCompte:
    """Classe pour valider la cohérence des comptes"""
    
    # Règles de validation par classe de compte
    REGLES_VALIDATION = {
        '1': {
            'types_autorises': ['actif', 'passif'],
            'description': 'Capitaux (actif ou passif selon le compte)',
            'regles_specifiques': {
                # Comptes de capital et réserves - PASSIF (créditeurs)
                '101': 'passif',  # Capital social
                '103': 'passif',  # Primes
                '106': 'passif',  # Réserves
                '108': {  # Compte exploitant
                    '1081': 'passif',  # Apports
                    '1089': 'actif',   # Prélèvements
                },
                '110': 'passif',  # RAN créditeur
                '119': 'actif',   # RAN débiteur
                '120': 'passif',  # Résultat bénéfice
                '129': 'actif',   # Résultat perte
                '13': 'passif',   # Subventions
                '14': 'passif',   # Provisions réglementées
                '15': 'passif',   # Provisions pour risques
                '16': {  # Emprunts
                    '164': 'passif',
                    '165': 'passif',
                    '166': 'passif',
                    '167': 'passif',
                    '168': 'passif',
                    '169': 'actif',  # Primes de remboursement
                },
            }
        },
        '2': {
            'types_autorises': ['actif'],
            'description': 'Immobilisations (toujours actif)',
            'validation': lambda compte: 'actif'
        },
        '3': {
            'types_autorises': ['actif'],
            'description': 'Stocks (toujours actif)',
            'validation': lambda compte: 'actif'
        },
        '4': {
            'types_autorises': ['actif', 'passif', 'tva'],
            'description': 'Tiers (actif, passif ou tva selon le compte)',
            'regles_specifiques': {
                '401': 'passif',  # Fournisseurs
                '403': 'passif',
                '404': 'passif',
                '405': 'passif',
                '408': 'passif',
                '409': 'actif',   # Fournisseurs débiteurs
                '411': 'actif',   # Clients
                '413': 'actif',
                '416': 'actif',
                '417': 'actif',
                '418': 'actif',
                '419': 'passif',  # Clients créditeurs
                '421': 'passif',  # Personnel - Rémunérations
                '422': 'passif',
                '424': 'passif',
                '425': 'actif',   # Personnel - Avances
                '426': 'passif',
                '427': 'passif',
                '428': 'passif',
                '429': 'actif',
                '43': 'passif',   # Sécurité sociale
                '441': 'actif',   # État - Subventions à recevoir
                '442': 'actif',   # État - Impôts recouvrables
                '443': 'actif',
                '444': {  # État - Impôt sur bénéfices
                    '4441': 'passif',  # Impôt à payer
                    '4442': 'actif',   # Avances et acomptes versés
                },
                '4451': 'actif',  # TVA crédit
                '4452': 'passif', # TVA due
                '4455': 'passif', # TVA à décaisser
                '4456': 'actif',  # TVA déductible
                '4457': 'passif', # TVA collectée
                '4458': 'tva',    # TVA à régulariser
                '447': 'passif',  # Autres impôts
                '448': 'passif',
                '451': 'passif',  # Groupe (dettes intra-groupe)
                '455': 'passif',  # Associés CC
                '456': 'passif',
                '457': 'passif',
                '458': 'passif',  # Opérations faites en commun (dette par défaut)
                '462': 'actif',
                '464': 'passif',
                '465': 'actif',
                '467': 'actif',
                '468': 'passif',  # Charges à payer / produits à recevoir (clé de répartition)
                '471': 'actif',
                '472': 'passif',
                '476': 'actif',
                '477': 'passif',
                '481': 'actif',
                '486': 'actif',
                '487': 'passif',
                '488': 'passif',  # Comptes de répartition périodique des charges/produits
                '489': 'actif',
                '491': 'actif',
                '496': 'actif',
            }
        },
        '5': {
            'types_autorises': ['actif', 'passif'],
            'description': 'Financiers (actif sauf exceptions)',
            'regles_specifiques': {
                '50': 'actif',   # VMP
                '509': 'passif', # Versements restant à effectuer
                '51': 'actif',   # Banques
                '519': 'passif', # Concours bancaires
                '53': 'actif',   # Caisse
                '54': 'actif',   # Instruments de trésorerie
                '58': 'actif',   # Virements internes
                '59': 'actif',   # Dépréciations
            }
        },
        '6': {
            'types_autorises': ['charge'],
            'description': 'Charges (toujours charge)',
            'validation': lambda compte: 'charge'
        },
        '7': {
            'types_autorises': ['produit'],
            'description': 'Produits (toujours produit)',
            'validation': lambda compte: 'produit'
        },
    }
    
    @classmethod
    def valider_compte(cls, numero_compte: str, type_declare: str) -> tuple[bool, str]:
        """
        Valide qu'un compte a le bon type selon sa classe
        
        Args:
            numero_compte: Numéro de compte (ex: '401000')
            type_declare: Type déclaré ('actif', 'passif', 'charge', 'produit', 'tva')
            
        Returns:
            (True, '') si valide
            (False, 'message d\'erreur') si invalide
        """
        if not numero_compte or len(numero_compte) < 1:
            return False, "Numéro de compte invalide"
        
        classe = numero_compte[0]
        
        if classe not in cls.REGLES_VALIDATION:
            return False, f"Classe {classe} non reconnue"
        
        regles = cls.REGLES_VALIDATION[classe]
        
        # Vérifier si le type est autorisé pour cette classe
        if type_declare not in regles['types_autorises']:
            return False, (
                f"Type '{type_declare}' non autorisé pour la classe {classe}. "
                f"Types autorisés : {', '.join(regles['types_autorises'])}"
            )
        
        # Si validation simple (fonction)
        if 'validation' in regles:
            type_attendu = regles['validation'](numero_compte)
            if type_attendu != type_declare:
                return False, (
                    f"Le compte {numero_compte} devrait être de type '{type_attendu}' "
                    f"(déclaré : '{type_declare}')"
                )
            return True, ''
        
        # Si règles spécifiques
        if 'regles_specifiques' in regles:
            # Chercher la règle la plus spécifique
            for prefixe in sorted(regles['regles_specifiques'].keys(), key=len, reverse=True):
                if numero_compte.startswith(prefixe):
                    regle = regles['regles_specifiques'][prefixe]
                    
                    # Si la règle est un dict, chercher plus en détail
                    if isinstance(regle, dict):
                        for sous_prefixe, type_attendu in regle.items():
                            if numero_compte.startswith(sous_prefixe):
                                if type_attendu != type_declare:
                                    return False, (
                                        f"Le compte {numero_compte} devrait être de type '{type_attendu}' "
                                        f"(déclaré : '{type_declare}')"
                                    )
                                return True, ''
                    else:
                        # La règle est directement le type
                        if regle != type_declare:
                            return False, (
                                f"Le compte {numero_compte} devrait être de type '{regle}' "
                                f"(déclaré : '{type_declare}')"
                            )
                        return True, ''
        
        # Si pas de règle spécifique trouvée, c'est OK tant que le type est autorisé
        return True, ''
    
    @classmethod
    def afficher_regles(cls):
        """Affiche les règles de validation"""
        print("\n" + "="*70)
        print("RÈGLES DE VALIDATION DES COMPTES")
        print("="*70)
        
        for classe, regles in cls.REGLES_VALIDATION.items():
            print(f"\n📊 Classe {classe}: {regles['description']}")
            print(f"   Types autorisés: {', '.join(regles['types_autorises'])}")
            
            if 'regles_specifiques' in regles:
                print("   Règles spécifiques:")
                for prefixe, regle in sorted(regles['regles_specifiques'].items()):
                    if isinstance(regle, dict):
                        print(f"      {prefixe}*:")
                        for sous_prefixe, type_compte in regle.items():
                            print(f"         {sous_prefixe}* → {type_compte}")
                    else:
                        print(f"      {prefixe}* → {regle}")


class InitialisationSociete:
    """Classe pour initialiser une nouvelle société avec validation"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.repo = SetupRepository(db_manager)
        self.service = create_service(db_manager)
        self.erreurs_validation = []
    
    def creer_societe_complete(
        self,
        nom_societe: str,
        siren: str,
        adresse: str,
        code_postal: str,
        ville: str,
        annee_exercice: int = None,
        mode_strict: bool = True
    ):
        """
        Crée une société complète avec validation stricte
        
        Args:
            mode_strict: Si True, bloque en cas d'erreur. Si False, affiche des warnings.
        """
        print("\n" + "="*60)
        print("🏢 CRÉATION D'UNE NOUVELLE SOCIÉTÉ (MODE VALIDÉ)")
        print("="*60)
        
        # 1. Créer la société
        print("\n1️⃣ Création de la société...")
        societe_id = self._creer_societe(
            nom_societe, siren, adresse, code_postal, ville
        )
        print(f"✅ Société créée (ID: {societe_id})")
        
        # 2. Créer l'exercice comptable
        print("\n2️⃣ Création de l'exercice comptable...")
        if annee_exercice is None:
            annee_exercice = date.today().year
        
        exercice_id = self._creer_exercice(societe_id, annee_exercice)
        print(f"✅ Exercice {annee_exercice} créé (ID: {exercice_id})")
        
        # 3. Créer les journaux
        print("\n3️⃣ Création des journaux comptables...")
        self._creer_journaux(societe_id)
        print("✅ 4 journaux créés (VE, AC, BQ, OD)")
        
        # 4. Créer le plan comptable avec validation
        print("\n4️⃣ Création du plan comptable PCG (avec validation)...")
        nb_comptes = self._creer_plan_comptable_valide(societe_id, mode_strict)
        
        if self.erreurs_validation:
            print(f"\n⚠️ {len(self.erreurs_validation)} erreur(s) de validation détectée(s)")
            if mode_strict:
                print("❌ Création annulée en mode strict")
                raise ValidationError(
                    f"{len(self.erreurs_validation)} comptes invalides détectés"
                )
        else:
            print(f"✅ {nb_comptes} comptes créés et validés")
        
        # 5. Créer les taux de TVA
        print("\n5️⃣ Création des taux de TVA...")
        self._creer_taux_tva(societe_id)
        print("✅ Taux de TVA créés (20%, 10%, 5.5%, 2.1%)")
        
        # 6. Créer quelques tiers exemples
        print("\n6️⃣ Création de tiers exemples...")
        self._creer_tiers_exemples(societe_id)
        print("✅ Tiers exemples créés")
        
        print("\n" + "="*60)
        print("✅ SOCIÉTÉ INITIALISÉE AVEC SUCCÈS !")
        print("="*60)
        print(f"\n📊 Société : {nom_societe}")
        print(f"📅 Exercice : {annee_exercice}")
        print(f"🏢 ID Société : {societe_id}")
        print(f"📆 ID Exercice : {exercice_id}")
        print("\n👉 Vous pouvez maintenant lancer l'application :")
        print("   python main.py")
        print("="*60 + "\n")
        
        return societe_id, exercice_id, "Société créée avec succès"
    
    def _creer_societe(self, nom, siren, adresse, code_postal, ville):
        """Crée la société dans la base"""
        return self.repo.create_societe(nom, siren, adresse, code_postal, ville)
    
    def _creer_exercice(self, societe_id, annee):
        """Crée l'exercice comptable"""
        return self.repo.create_exercice(societe_id, annee)
    
    def _creer_journaux(self, societe_id):
        """Crée les journaux standards"""
        journaux = [
            ('VE', 'Journal des ventes', 'VENTE'),
            ('AC', 'Journal des achats', 'ACHAT'),
            ('BQ', 'Journal de banque', 'BANQUE'),
            ('OD', 'Opérations diverses', 'OD')
        ]
        self.repo.create_journaux(societe_id, journaux)
    
    def _creer_plan_comptable_valide(self, societe_id, mode_strict=True):
        """
        Crée le plan comptable avec validation stricte de chaque compte
        
        Args:
            societe_id: ID de la société
            mode_strict: Si True, bloque l'insertion en cas d'erreur
            
        Returns:
            Nombre de comptes créés
        """
        comptes = self._obtenir_liste_comptes()
        
        print(f"\n📝 Validation de {len(comptes)} comptes...")
        
        comptes_valides = []
        self.erreurs_validation = []
        
        # Phase 1: Validation
        for compte, intitule, classe, type_compte, lettrable in comptes:
            est_valide, message_erreur = ValidateurCompte.valider_compte(compte, type_compte)
            
            if est_valide:
                comptes_valides.append((compte, intitule, classe, type_compte, lettrable))
            else:
                erreur = f"❌ Compte {compte} ({intitule}): {message_erreur}"
                self.erreurs_validation.append(erreur)
                print(erreur)
        
        # Afficher le résumé
        print(f"\n✅ Comptes valides: {len(comptes_valides)}/{len(comptes)}")
        if self.erreurs_validation:
            print(f"❌ Comptes invalides: {len(self.erreurs_validation)}")
            
            if mode_strict:
                print("\n⚠️ MODE STRICT: Aucun compte ne sera inséré")
                return 0
            else:
                print("\n⚠️ MODE PERMISSIF: Seuls les comptes valides seront insérés")
        
        # Phase 2: Insertion des comptes valides
        self.repo.insert_comptes(societe_id, comptes_valides)
        
        return len(comptes_valides)
    
    def _obtenir_liste_comptes(self):
        """Retourne la liste complète des comptes du PCG"""
        return [
            # ========================================
            # CLASSE 1 : COMPTES DE CAPITAUX
            # ========================================
            ('101000', 'Capital social', '1', 'passif', True),
            ('103000', 'Primes d\'émission, de fusion, d\'apport', '1', 'passif', True),
            ('106000', 'Réserves', '1', 'passif', True),
            ('106100', 'Réserve légale', '1', 'passif', True),
            ('106800', 'Autres réserves', '1', 'passif', True),
            ('108000', 'Compte de l\'exploitant', '1', 'passif', True),
            ('108100', 'Compte de l\'exploitant - Apports', '1', 'passif', True),
            ('108900', 'Compte de l\'exploitant - Prélèvements', '1', 'actif', False),
            ('110000', 'Report à nouveau (solde créditeur)', '1', 'passif', True),
            ('119000', 'Report à nouveau (solde débiteur)', '1', 'actif', False),
            ('120000', 'Résultat de l\'exercice (bénéfice)', '1', 'passif', True),
            ('129000', 'Résultat de l\'exercice (perte)', '1', 'actif', False),
            ('131000', 'Subventions d\'équipement', '1', 'passif', True),
            ('138000', 'Autres subventions d\'investissement', '1', 'passif', True),
            ('142000', 'Provisions réglementées relatives aux immobilisations', '1', 'passif', True),
            ('143000', 'Provisions réglementées relatives aux stocks', '1', 'passif', True),
            ('145000', 'Amortissements dérogatoires', '1', 'passif', True),
            ('151000', 'Provisions pour risques', '1', 'passif', True),
            ('153000', 'Provisions pour pensions et obligations similaires', '1', 'passif', True),
            ('155000', 'Provisions pour charges', '1', 'passif', True),
            ('156000', 'Provisions pour impôts', '1', 'passif', True),
            ('157000', 'Provisions pour charges à répartir sur plusieurs exercices', '1', 'passif', True),
            ('158000', 'Autres provisions pour charges', '1', 'passif', True),
            ('164000', 'Emprunts auprès des établissements de crédit', '1', 'passif', True),
            ('165000', 'Dépôts et cautionnements reçus', '1', 'passif', True),
            ('166000', 'Participation des salariés aux résultats', '1', 'passif', True),
            ('167000', 'Emprunts et dettes assortis de conditions particulières', '1', 'passif', True),
            ('168000', 'Autres emprunts et dettes assimilées', '1', 'passif', True),
            ('168500', 'Emprunts participatifs', '1', 'passif', True),
            ('169000', 'Primes de remboursement des emprunts', '1', 'actif', False),
            
            # ========================================
            # CLASSE 2 : COMPTES D'IMMOBILISATIONS
            # ========================================
            ('201000', 'Frais d\'établissement', '2', 'actif', False),
            ('203000', 'Frais de recherche et développement', '2', 'actif', False),
            ('205000', 'Concessions et droits similaires, brevets', '2', 'actif', False),
            ('206000', 'Droit au bail', '2', 'actif', False),
            ('207000', 'Fonds commercial', '2', 'actif', False),
            ('208000', 'Autres immobilisations incorporelles', '2', 'actif', False),
            ('211000', 'Terrains', '2', 'actif', False),
            ('212000', 'Agencements et aménagements de terrains', '2', 'actif', False),
            ('213000', 'Constructions', '2', 'actif', False),
            ('214000', 'Constructions sur sol d\'autrui', '2', 'actif', False),
            ('215000', 'Installations techniques, matériel et outillage', '2', 'actif', False),
            ('218000', 'Autres immobilisations corporelles', '2', 'actif', False),
            ('218100', 'Installations générales, agencements', '2', 'actif', False),
            ('218300', 'Matériel de bureau et informatique', '2', 'actif', False),
            ('218400', 'Mobilier', '2', 'actif', False),
            ('218500', 'Matériel de transport', '2', 'actif', False),
            ('231000', 'Immobilisations corporelles en cours', '2', 'actif', False),
            ('232000', 'Immobilisations incorporelles en cours', '2', 'actif', False),
            ('261000', 'Titres de participation', '2', 'actif', False),
            ('266000', 'Autres formes de participation', '2', 'actif', False),
            ('267000', 'Créances rattachées à des participations', '2', 'actif', False),
            ('271000', 'Titres immobilisés (autres que TIAP)', '2', 'actif', False),
            ('272000', 'Titres immobilisés (droit de propriété)', '2', 'actif', False),
            ('273000', 'Titres immobilisés de l\'activité de portefeuille', '2', 'actif', False),
            ('274000', 'Prêts', '2', 'actif', False),
            ('275000', 'Dépôts et cautionnements versés', '2', 'actif', False),
            ('276000', 'Autres créances immobilisées', '2', 'actif', False),
            ('280500', 'Amortissements des concessions et droits similaires', '2', 'actif', False),
            ('281000', 'Amortissements des immobilisations incorporelles', '2', 'actif', False),
            ('281100', 'Amortissements des frais d\'établissement', '2', 'actif', False),
            ('281300', 'Amortissements des constructions', '2', 'actif', False),
            ('281500', 'Amortissements installations techniques', '2', 'actif', False),
            ('281800', 'Amortissements autres immobilisations', '2', 'actif', False),
            ('282000', 'Amortissements des immobilisations corporelles', '2', 'actif', False),
            ('290000', 'Dépréciations des immobilisations incorporelles', '2', 'actif', False),
            ('291000', 'Dépréciations des immobilisations corporelles', '2', 'actif', False),
            ('296000', 'Provisions pour dépréciations des participations', '2', 'actif', False),
            ('297000', 'Provisions pour dépréciations des autres immobilisations financières', '2', 'actif', False),
            
            # ========================================
            # CLASSE 3 : COMPTES DE STOCKS
            # ========================================
            ('311000', 'Matières premières', '3', 'actif', False),
            ('312000', 'Matières et fournitures consommables', '3', 'actif', False),
            ('317000', 'Fournitures stockées', '3', 'actif', False),
            ('321000', 'Matières consommables', '3', 'actif', False),
            ('331000', 'En-cours de production de biens', '3', 'actif', False),
            ('335000', 'En-cours de production de services', '3', 'actif', False),
            ('355000', 'Produits finis', '3', 'actif', False),
            ('358000', 'Produits intermédiaires', '3', 'actif', False),
            ('371000', 'Stocks de marchandises', '3', 'actif', False),
            ('375000', 'Stocks mis en dépôt ou en consignation', '3', 'actif', False),
            ('380000', 'Stocks en cours de route', '3', 'actif', False),
            ('391000', 'Provisions pour dépréciation des matières premières', '3', 'actif', False),
            ('392000', 'Provisions pour dépréciation des autres approvisionnements', '3', 'actif', False),
            ('393000', 'Provisions pour dépréciation des en-cours', '3', 'actif', False),
            ('395000', 'Provisions pour dépréciation des produits', '3', 'actif', False),
            ('397000', 'Provisions pour dépréciation des marchandises', '3', 'actif', False),
            
            # ========================================
            # CLASSE 4 : COMPTES DE TIERS
            # ========================================
            ('401000', 'Fournisseurs', '4', 'passif', True),
            ('403000', 'Fournisseurs - Effets à payer', '4', 'passif', False),
            ('404000', 'Fournisseurs d\'immobilisations', '4', 'passif', True),
            ('405000', 'Fournisseurs d\'immobilisations - Effets à payer', '4', 'passif', False),
            ('408000', 'Fournisseurs - Factures non parvenues', '4', 'passif', False),
            ('409000', 'Fournisseurs débiteurs', '4', 'actif', False),
            ('409700', 'Fournisseurs - Autres avoirs', '4', 'actif', False),
            ('409800', 'Rabais, remises, ristournes à obtenir', '4', 'actif', False),
            ('411000', 'Clients', '4', 'actif', True),
            ('413000', 'Clients - Effets à recevoir', '4', 'actif', True),
            ('416000', 'Clients douteux', '4', 'actif', True),
            ('417000', 'Créances sur travaux non encore facturables', '4', 'actif', False),
            ('418000', 'Clients - Produits à recevoir', '4', 'actif', False),
            ('419000', 'Clients créditeurs', '4', 'passif', False),
            ('419700', 'Clients - Autres avoirs', '4', 'passif', False),
            ('419800', 'Rabais, remises, ristournes à accorder', '4', 'passif', False),
            ('421000', 'Personnel - Rémunérations dues', '4', 'passif', True),
            ('422000', 'Comités d\'entreprises, d\'établissement', '4', 'passif', False),
            ('424000', 'Participation des salariés aux résultats', '4', 'passif', False),
            ('425000', 'Personnel - Avances et acomptes', '4', 'actif', False),
            ('426000', 'Personnel - Dépôts reçus', '4', 'passif', False),
            ('427000', 'Personnel - Oppositions', '4', 'passif', False),
            ('428000', 'Personnel - Charges à payer', '4', 'passif', False),
            ('429000', 'Déficits et débets des comptables et régisseurs', '4', 'actif', False),
            ('431000', 'Sécurité sociale', '4', 'passif', False),
            ('437000', 'Autres organismes sociaux', '4', 'passif', False),
            ('438000', 'Organismes sociaux - Charges à payer', '4', 'passif', False),
            ('441000', 'État - Subventions à recevoir', '4', 'actif', False),
            ('442000', 'État - Impôts et taxes recouvrables', '4', 'actif', False),
            ('443000', 'Opérations particulières avec l\'État', '4', 'actif', False),
            ('444000', 'État - Impôt sur les bénéfices', '4', 'passif', False),
            ('444100', 'État - Impôt sur les bénéfices à payer', '4', 'passif', False),
            ('444200', 'État - Impôt sur les bénéfices - Avances et acomptes', '4', 'actif', False),
            ('445000', 'État - Taxes sur le chiffre d\'affaires', '4', 'tva', False),
            ('445100', 'État - Crédit de TVA', '4', 'actif', False),
            ('445200', 'État - TVA due intracommunautaire', '4', 'passif', False),
            ('445510', 'TVA à décaisser', '4', 'passif', False),
            ('445620', 'TVA sur immobilisations', '4', 'actif', False),
            ('445660', 'TVA déductible sur biens et services', '4', 'actif', False),
            ('445670', 'TVA déductible (autre bien et services)', '4', 'actif', False),
            ('445710', 'TVA collectée', '4', 'passif', False),
            ('445800', 'TVA à régulariser ou en attente', '4', 'tva', False),
            ('447000', 'Autres impôts, taxes et versements assimilés', '4', 'passif', False),
            ('447100', 'Taxe professionnelle', '4', 'passif', False),
            ('447200', 'Taxe foncière', '4', 'passif', False),
            ('448000', 'État - Charges à payer', '4', 'passif', False),
            ('451000', 'Groupe', '4', 'passif', False),
            ('455000', 'Associés - Comptes courants', '4', 'passif', True),
            ('456000', 'Associés - Opérations sur le capital', '4', 'passif', False),
            ('457000', 'Associés - Dividendes à payer', '4', 'passif', False),
            ('458000', 'Associés - Opérations faites en commun', '4', 'passif', False),
            ('462000', 'Créances sur cessions d\'immobilisations', '4', 'actif', False),
            ('464000', 'Dettes sur acquisitions de valeurs mobilières', '4', 'passif', False),
            ('465000', 'Créances sur cessions de valeurs mobilières', '4', 'actif', False),
            ('467000', 'Autres comptes débiteurs ou créditeurs', '4', 'actif', False),
            ('468000', 'Divers - Charges à payer et produits à recevoir', '4', 'passif', False),
            ('471000', 'Comptes d\'attente', '4', 'actif', False),
            ('472000', 'Comptes d\'attente - Passif', '4', 'passif', False),
            ('476000', 'Différence de conversion - Actif', '4', 'actif', False),
            ('477000', 'Différence de conversion - Passif', '4', 'passif', False),
            ('481000', 'Charges à répartir sur plusieurs exercices', '4', 'actif', False),
            ('486000', 'Charges constatées d\'avance', '4', 'actif', False),
            ('487000', 'Produits constatés d\'avance', '4', 'passif', False),
            ('488000', 'Comptes de répartition périodique des charges et produits', '4', 'passif', False),
            ('489000', 'Quotas d\'émission alloués par l\'État', '4', 'actif', False),
            ('491000', 'Provisions pour dépréciations des comptes clients', '4', 'actif', False),
            ('496000', 'Provisions pour dépréciations des comptes de débiteurs divers', '4', 'actif', False),
            
            # ========================================
            # CLASSE 5 : COMPTES FINANCIERS
            # ========================================
            ('501000', 'Parts dans des entreprises liées', '5', 'actif', False),
            ('502000', 'Actions propres', '5', 'actif', False),
            ('503000', 'Actions', '5', 'actif', False),
            ('506000', 'Obligations', '5', 'actif', False),
            ('507000', 'Bons du Trésor et bons de caisse à court terme', '5', 'actif', False),
            ('508000', 'Autres valeurs mobilières de placement', '5', 'actif', False),
            ('509000', 'Versements restant à effectuer sur VMP non libérées', '5', 'passif', False),
            ('511000', 'Valeurs à l\'encaissement', '5', 'actif', False),
            ('512000', 'Banque', '5', 'actif', True),
            ('512100', 'Banque X', '5', 'actif', True),
            ('512200', 'Banque Y', '5', 'actif', True),
            ('512800', 'Banques - Comptes en devises', '5', 'actif', False),
            ('514000', 'Chèques postaux', '5', 'actif', True),
            ('515000', 'Caisse nationale d\'épargne', '5', 'actif', False),
            ('517000', 'Autres organismes financiers', '5', 'actif', False),
            ('518000', 'Intérêts courus', '5', 'actif', False),
            ('519000', 'Concours bancaires courants', '5', 'passif', False),
            ('530000', 'Caisse', '5', 'actif', False),
            ('531000', 'Caisse en euros', '5', 'actif', False),
            ('532000', 'Caisse en devises', '5', 'actif', False),
            ('540000', 'Instruments de trésorerie', '5', 'actif', False),
            ('541000', 'Régie d\'avances', '5', 'actif', False),
            ('542000', 'Accréditifs', '5', 'actif', False),
            ('580000', 'Virements internes', '5', 'actif', False),
            ('581000', 'Virements de fonds', '5', 'actif', False),
            ('588000', 'Autres virements internes', '5', 'actif', False),
            ('590000', 'Dépréciations des valeurs mobilières de placement', '5', 'actif', False),
            
            # ========================================
            # CLASSE 6 : COMPTES DE CHARGES
            # ========================================
            ('601000', 'Achats stockés - Matières premières', '6', 'charge', False),
            ('602000', 'Achats stockés - Autres approvisionnements', '6', 'charge', False),
            ('603000', 'Variations des stocks', '6', 'charge', False),
            ('604000', 'Achats d\'études et prestations de services', '6', 'charge', False),
            ('605000', 'Achats de matériels, équipements et travaux', '6', 'charge', False),
            ('606000', 'Achats non stockés de matières et fournitures', '6', 'charge', False),
            ('606100', 'Fournitures non stockables (eau, énergie)', '6', 'charge', False),
            ('606300', 'Fournitures d\'entretien', '6', 'charge', False),
            ('606400', 'Fournitures administratives', '6', 'charge', False),
            ('606500', 'Équipements de bureau', '6', 'charge', False),
            ('607000', 'Achats de marchandises', '6', 'charge', False),
            ('608000', 'Frais accessoires d\'achats', '6', 'charge', False),
            ('609000', 'Rabais, remises, ristournes obtenus sur achats', '6', 'charge', False),
            ('611000', 'Sous-traitance générale', '6', 'charge', False),
            ('612000', 'Redevances de crédit-bail', '6', 'charge', False),
            ('613000', 'Locations', '6', 'charge', False),
            ('613200', 'Locations immobilières', '6', 'charge', False),
            ('613500', 'Locations mobilières', '6', 'charge', False),
            ('614000', 'Charges locatives et de copropriété', '6', 'charge', False),
            ('615000', 'Entretien et réparations', '6', 'charge', False),
            ('615200', 'Entretien et réparations sur biens immobiliers', '6', 'charge', False),
            ('615500', 'Entretien et réparations sur biens mobiliers', '6', 'charge', False),
            ('616000', 'Primes d\'assurance', '6', 'charge', False),
            ('616100', 'Assurances multirisques', '6', 'charge', False),
            ('616200', 'Assurances matériel de transport', '6', 'charge', False),
            ('616400', 'Assurances risques d\'exploitation', '6', 'charge', False),
            ('617000', 'Études et recherches', '6', 'charge', False),
            ('618000', 'Divers', '6', 'charge', False),
            ('619000', 'Rabais, remises, ristournes obtenus sur services extérieurs', '6', 'charge', False),
            ('621000', 'Personnel extérieur à l\'entreprise', '6', 'charge', False),
            ('622000', 'Rémunérations d\'intermédiaires et honoraires', '6', 'charge', False),
            ('622100', 'Commissions et courtages', '6', 'charge', False),
            ('622200', 'Honoraires', '6', 'charge', False),
            ('622600', 'Honoraires ne constituant pas des rétrocessions', '6', 'charge', False),
            ('622700', 'Frais d\'actes et de contentieux', '6', 'charge', False),
            ('623000', 'Publicité, publications, relations publiques', '6', 'charge', False),
            ('623100', 'Annonces et insertions', '6', 'charge', False),
            ('623200', 'Échantillons', '6', 'charge', False),
            ('623400', 'Cadeaux à la clientèle', '6', 'charge', False),
            ('623500', 'Primes', '6', 'charge', False),
            ('623800', 'Divers (pourboires, dons courants)', '6', 'charge', False),
            ('624000', 'Transports de biens et transports collectifs du personnel', '6', 'charge', False),
            ('624100', 'Transports sur achats', '6', 'charge', False),
            ('624200', 'Transports sur ventes', '6', 'charge', False),
            ('624800', 'Divers', '6', 'charge', False),
            ('625000', 'Déplacements, missions et réceptions', '6', 'charge', False),
            ('625100', 'Voyages et déplacements', '6', 'charge', False),
            ('625200', 'Missions', '6', 'charge', False),
            ('625500', 'Frais de déménagement', '6', 'charge', False),
            ('625600', 'Réceptions', '6', 'charge', False),
            ('626000', 'Frais postaux et de télécommunications', '6', 'charge', False),
            ('626100', 'Frais postaux', '6', 'charge', False),
            ('626200', 'Frais de téléphone', '6', 'charge', False),
            ('626300', 'Frais de télex et de télégrammes', '6', 'charge', False),
            ('626800', 'Frais d\'internet', '6', 'charge', False),
            ('627000', 'Services bancaires et assimilés', '6', 'charge', False),
            ('627100', 'Frais sur titres', '6', 'charge', False),
            ('627200', 'Commissions et frais sur émission d\'emprunts', '6', 'charge', False),
            ('627500', 'Frais sur effets de commerce', '6', 'charge', False),
            ('627800', 'Autres frais et commissions sur prestations de services', '6', 'charge', False),
            ('628000', 'Divers', '6', 'charge', False),
            ('628100', 'Concours divers (cotisations)', '6', 'charge', False),
            ('629000', 'Rabais, remises, ristournes obtenus sur autres services extérieurs', '6', 'charge', False),
            ('631000', 'Impôts, taxes et versements assimilés sur rémunérations', '6', 'charge', False),
            ('633000', 'Impôts, taxes et versements assimilés sur rémunérations (administrations)', '6', 'charge', False),
            ('633100', 'Taxe sur les salaires', '6', 'charge', False),
            ('633500', 'Taxe d\'apprentissage', '6', 'charge', False),
            ('635000', 'Autres impôts, taxes et versements assimilés', '6', 'charge', False),
            ('635100', 'Taxe foncière', '6', 'charge', False),
            ('635200', 'Contribution économique territoriale', '6', 'charge', False),
            ('635300', 'Autres impôts locaux', '6', 'charge', False),
            ('635400', 'Taxes sur les véhicules', '6', 'charge', False),
            ('637000', 'Autres impôts, taxes et versements assimilés (administration des impôts)', '6', 'charge', False),
            ('637100', 'Contribution sociale de solidarité à la charge des sociétés', '6', 'charge', False),
            ('641000', 'Rémunérations du personnel', '6', 'charge', False),
            ('641100', 'Salaires, appointements', '6', 'charge', False),
            ('641200', 'Congés payés', '6', 'charge', False),
            ('641300', 'Primes et gratifications', '6', 'charge', False),
            ('641400', 'Indemnités et avantages divers', '6', 'charge', False),
            ('641600', 'Supplément familial', '6', 'charge', False),
            ('644000', 'Rémunérations du travail de l\'exploitant', '6', 'charge', False),
            ('645000', 'Charges de sécurité sociale et de prévoyance', '6', 'charge', False),
            ('645100', 'Cotisations à l\'URSSAF', '6', 'charge', False),
            ('645200', 'Cotisations aux mutuelles', '6', 'charge', False),
            ('645300', 'Cotisations aux caisses de retraite', '6', 'charge', False),
            ('645400', 'Cotisations aux ASSEDIC', '6', 'charge', False),
            ('645500', 'Cotisations aux autres organismes sociaux', '6', 'charge', False),
            ('645800', 'Autres charges sociales', '6', 'charge', False),
            ('646000', 'Cotisations sociales personnelles de l\'exploitant', '6', 'charge', False),
            ('647000', 'Autres charges sociales', '6', 'charge', False),
            ('648000', 'Autres charges de personnel', '6', 'charge', False),
            ('651000', 'Redevances pour concessions, brevets, licences', '6', 'charge', False),
            ('651100', 'Redevances pour concessions, brevets, licences, marques', '6', 'charge', False),
            ('651200', 'Redevances pour logiciels', '6', 'charge', False),
            ('651600', 'Droits d\'auteur et de reproduction', '6', 'charge', False),
            ('653000', 'Jetons de présence', '6', 'charge', False),
            ('654000', 'Pertes sur créances irrécouvrables', '6', 'charge', False),
            ('655000', 'Quote-part de résultat sur opérations faites en commun', '6', 'charge', False),
            ('658000', 'Charges diverses de gestion courante', '6', 'charge', False),
            ('661000', 'Charges d\'intérêts', '6', 'charge', False),
            ('661100', 'Intérêts des emprunts et dettes', '6', 'charge', False),
            ('661600', 'Intérêts bancaires', '6', 'charge', False),
            ('661700', 'Intérêts des comptes courants et des dépôts créditeurs', '6', 'charge', False),
            ('664000', 'Pertes sur créances liées à des participations', '6', 'charge', False),
            ('665000', 'Escomptes accordés', '6', 'charge', False),
            ('666000', 'Pertes de change', '6', 'charge', False),
            ('667000', 'Charges nettes sur cessions de valeurs mobilières', '6', 'charge', False),
            ('668000', 'Autres charges financières', '6', 'charge', False),
            ('671000', 'Charges exceptionnelles sur opérations de gestion', '6', 'charge', False),
            ('672000', 'Charges sur exercices antérieurs', '6', 'charge', False),
            ('675000', 'Valeurs comptables des éléments d\'actif cédés', '6', 'charge', False),
            ('678000', 'Autres charges exceptionnelles', '6', 'charge', False),
            ('681000', 'Dotations aux amortissements et aux provisions', '6', 'charge', False),
            ('681100', 'Dotations aux amortissements sur immobilisations incorporelles', '6', 'charge', False),
            ('681200', 'Dotations aux amortissements sur immobilisations corporelles', '6', 'charge', False),
            ('681500', 'Dotations aux provisions pour risques et charges d\'exploitation', '6', 'charge', False),
            ('681700', 'Dotations aux provisions pour dépréciation des actifs circulants', '6', 'charge', False),
            ('686000', 'Dotations aux provisions', '6', 'charge', False),
            ('686100', 'Dotations pour risques et charges financiers', '6', 'charge', False),
            ('686500', 'Dotations aux provisions pour risques et charges exceptionnels', '6', 'charge', False),
            ('687000', 'Dotations aux amortissements, provisions et dépréciations - Charges exceptionnelles', '6', 'charge', False),
            ('691000', 'Participation des salariés aux résultats', '6', 'charge', False),
            ('695000', 'Impôts sur les bénéfices', '6', 'charge', False),
            ('695100', 'Imposition forfaitaire annuelle des sociétés', '6', 'charge', False),
            ('695200', 'Contribution additionnelle à l\'impôt sur les sociétés', '6', 'charge', False),
            ('695500', 'Impôt sur les sociétés', '6', 'charge', False),
            ('696000', 'Suppléments d\'impôt sur les sociétés liés aux distributions', '6', 'charge', False),
            ('697000', 'Imposition différée', '6', 'charge', False),
            ('698000', 'Intégration fiscale', '6', 'charge', False),
            ('699000', 'Produits - Report en arrière des déficits', '6', 'charge', False),
            
            # ========================================
            # CLASSE 7 : COMPTES DE PRODUITS
            # ========================================
            ('701000', 'Ventes de produits finis', '7', 'produit', False),
            ('702000', 'Ventes de produits intermédiaires', '7', 'produit', False),
            ('703000', 'Ventes de produits résiduels', '7', 'produit', False),
            ('704000', 'Travaux', '7', 'produit', False),
            ('705000', 'Études', '7', 'produit', False),
            ('706000', 'Prestations de services', '7', 'produit', False),
            ('707000', 'Ventes de marchandises', '7', 'produit', False),
            ('708000', 'Produits des activités annexes', '7', 'produit', False),
            ('708100', 'Produits des services exploités dans l\'intérêt du personnel', '7', 'produit', False),
            ('708200', 'Commissions et courtages', '7', 'produit', False),
            ('708500', 'Ports et frais accessoires facturés', '7', 'produit', False),
            ('709000', 'Rabais, remises, ristournes accordés par l\'entreprise', '7', 'produit', False),
            ('713000', 'Variation des stocks (en-cours de production, produits)', '7', 'produit', False),
            ('713100', 'Variation des en-cours de production de biens', '7', 'produit', False),
            ('713500', 'Variation des en-cours de production de services', '7', 'produit', False),
            ('715000', 'Variation des stocks de produits', '7', 'produit', False),
            ('721000', 'Production immobilisée - Immobilisations incorporelles', '7', 'produit', False),
            ('722000', 'Production immobilisée - Immobilisations corporelles', '7', 'produit', False),
            ('740000', 'Subventions d\'exploitation', '7', 'produit', False),
            ('741000', 'Subventions d\'équilibre', '7', 'produit', False),
            ('748000', 'Autres subventions d\'exploitation', '7', 'produit', False),
            ('751000', 'Redevances pour concessions, brevets, licences', '7', 'produit', False),
            ('752000', 'Revenus des immeubles non affectés à l\'exploitation', '7', 'produit', False),
            ('753000', 'Jetons de présence et rémunérations d\'administrateurs', '7', 'produit', False),
            ('754000', 'Ristournes perçues des coopératives', '7', 'produit', False),
            ('755000', 'Quotes-parts de résultat sur opérations faites en commun', '7', 'produit', False),
            ('758000', 'Produits divers de gestion courante', '7', 'produit', False),
            ('761000', 'Produits de participations', '7', 'produit', False),
            ('762000', 'Produits des autres immobilisations financières', '7', 'produit', False),
            ('763000', 'Revenus des autres créances', '7', 'produit', False),
            ('764000', 'Revenus des valeurs mobilières de placement', '7', 'produit', False),
            ('765000', 'Escomptes obtenus', '7', 'produit', False),
            ('766000', 'Gains de change', '7', 'produit', False),
            ('767000', 'Produits nets sur cessions de valeurs mobilières', '7', 'produit', False),
            ('768000', 'Autres produits financiers', '7', 'produit', False),
            ('771000', 'Produits exceptionnels sur opérations de gestion', '7', 'produit', False),
            ('772000', 'Produits sur exercices antérieurs', '7', 'produit', False),
            ('775000', 'Produits des cessions d\'éléments d\'actif', '7', 'produit', False),
            ('777000', 'Quote-part des subventions d\'investissement virée au résultat', '7', 'produit', False),
            ('778000', 'Autres produits exceptionnels', '7', 'produit', False),
            ('781000', 'Reprises sur amortissements et provisions', '7', 'produit', False),
            ('781100', 'Reprises sur amortissements des immobilisations incorporelles', '7', 'produit', False),
            ('781200', 'Reprises sur amortissements des immobilisations corporelles', '7', 'produit', False),
            ('781500', 'Reprises sur provisions pour risques et charges d\'exploitation', '7', 'produit', False),
            ('781700', 'Reprises sur dépréciations des actifs circulants', '7', 'produit', False),
            ('786000', 'Reprises sur provisions pour risques', '7', 'produit', False),
            ('786100', 'Reprises sur provisions pour risques et charges financiers', '7', 'produit', False),
            ('786500', 'Reprises sur provisions pour risques et charges exceptionnels', '7', 'produit', False),
            ('787000', 'Reprises sur provisions - Charges exceptionnelles', '7', 'produit', False),
            ('791000', 'Transferts de charges d\'exploitation', '7', 'produit', False),
            ('796000', 'Transferts de charges financières', '7', 'produit', False),
            ('797000', 'Transferts de charges exceptionnelles', '7', 'produit', False),
        ]
    
    def _creer_taux_tva(self, societe_id):
        """Crée les taux de TVA standards"""
        compte_collecte_id = self.repo.get_compte_id(societe_id, '445710')
        compte_deductible_id = self.repo.get_compte_id(societe_id, '445660')
        
        if not compte_collecte_id or not compte_deductible_id:
            print("⚠️ Comptes de TVA non trouvés")
            return
        
        taux_tva = [
            ('TVA20', 'TVA 20%', 0.200),
            ('TVA10', 'TVA 10%', 0.100),
            ('TVA055', 'TVA 5.5%', 0.055),
            ('TVA021', 'TVA 2.1%', 0.021),
        ]
        
        self.repo.create_tva(societe_id, taux_tva, compte_collecte_id, compte_deductible_id)
    
    def _creer_tiers_exemples(self, societe_id):
        """Crée quelques tiers exemples"""
        tiers = [
            ('CLT0001', 'Client Exemple 1', 'CLIENT', '10 Rue de la Paix', 'Paris'),
            ('CLT0002', 'Client Exemple 2', 'CLIENT', '22 Avenue des Champs', 'Lyon'),
            ('FRN0001', 'Fournisseur Exemple 1', 'FOURNISSEUR', '3 Rue du Commerce', 'Marseille'),
            ('FRN0002', 'Fournisseur Exemple 2', 'FOURNISSEUR', '8 Boulevard Victor Hugo', 'Toulouse'),
        ]
        
        self.repo.create_tiers(societe_id, tiers)


def main():
    """Fonction principale - Mode interactif"""
    print("\n" + "="*70)
    print(" "*10 + "🏢 INITIALISATION DE SOCIÉTÉ (MODE VALIDÉ)")
    print("="*70)
    
    # Afficher les règles de validation
    reponse = input("\nAfficher les règles de validation ? (o/N) : ").strip().lower()
    if reponse == 'o':
        ValidateurCompte.afficher_regles()
        input("\nAppuyez sur Entrée pour continuer...")
    
    # Connexion à la base
    try:
        db = create_db_manager()
        print("\n✅ Connexion à la base de données établie")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return
    
    init = InitialisationSociete(db)
    
    # Collecte des informations
    print("\n📝 Veuillez saisir les informations de la société :\n")
    
    nom_societe = input("Nom de la société : ").strip()
    if not nom_societe:
        print("❌ Le nom est obligatoire")
        return
    
    siren = input("SIREN (9 chiffres) : ").strip()
    if len(siren) != 9 or not siren.isdigit():
        print("⚠️ SIREN invalide, un SIREN fictif sera généré")
        siren = "999999999"
    
    adresse = input("Adresse : ").strip() or "Adresse non renseignée"
    code_postal = input("Code postal : ").strip() or "00000"
    ville = input("Ville : ").strip() or "Ville non renseignée"
    
    annee_str = input(f"Année de l'exercice (Enter = {date.today().year}) : ").strip()
    annee_exercice = int(annee_str) if annee_str and annee_str.isdigit() else date.today().year
    
    # Mode de validation
    print("\n🔧 Mode de validation :")
    print("  [1] Mode STRICT : Bloque si erreur de validation")
    print("  [2] Mode PERMISSIF : Insère uniquement les comptes valides")
    choix = input("Votre choix (1/2) [1] : ").strip() or "1"
    mode_strict = choix == "1"
    
    # Confirmation
    print("\n" + "-"*70)
    print("📋 RÉCAPITULATIF :")
    print("-"*70)
    print(f"Société      : {nom_societe}")
    print(f"SIREN        : {siren}")
    print(f"Adresse      : {adresse}")
    print(f"Ville        : {code_postal} {ville}")
    print(f"Exercice     : {annee_exercice}")
    print(f"Validation   : {'STRICT' if mode_strict else 'PERMISSIF'}")
    print("-"*70)
    
    confirmation = input("\n✅ Confirmer la création ? (o/N) : ").strip().lower()
    
    if confirmation != 'o':
        print("❌ Création annulée")
        db.disconnect()
        return
    
    # Création
    try:
        societe_id, exercice_id, message = init.creer_societe_complete(
            nom_societe=nom_societe,
            siren=siren,
            adresse=adresse,
            code_postal=code_postal,
            ville=ville,
            annee_exercice=annee_exercice,
            mode_strict=mode_strict
        )
        
        print(f"\n✅ {message}")
        print(f"\n💾 Société ID : {societe_id}")
        print(f"💾 Exercice ID : {exercice_id}")
        
    except ValidationError as e:
        print(f"\n❌ Erreur de validation : {e}")
        print("Les comptes invalides doivent être corrigés avant insertion")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création : {e}")
    finally:
        db.disconnect()
        print("\n🔌 Connexion fermée")


if __name__ == "__main__":
    main()
