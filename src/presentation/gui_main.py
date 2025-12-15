"""
Interface graphique principale - Application de comptabilité
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from src.infrastructure.persistence.database import DatabaseManager
from src.infrastructure.persistence.dao import (
    SocieteDAO,
    ExerciceDAO,
    JournalDAO,
    CompteDAO,
    TiersDAO,
    EcritureDAO,
    BalanceDAO,
    ReportingDAO,
    ProcedureDAO,
)
from src.application.services import ComptabiliteService
from src.domain.models import *
from src.presentation.widgets import MenuBar, ToolBar, StatusBar
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComptaApp:
    """Application principale de comptabilité"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Comptabilité Générale v2.0")
        self.root.geometry("1400x800")
        
        # Initialisation de la base de données
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.connect()
            self.service = ComptabiliteService(
                db=self.db_manager,
                societe_repo=SocieteDAO(self.db_manager),
                exercice_repo=ExerciceDAO(self.db_manager),
                journal_repo=JournalDAO(self.db_manager),
                compte_repo=CompteDAO(self.db_manager),
                tiers_repo=TiersDAO(self.db_manager),
                ecriture_repo=EcritureDAO(self.db_manager),
                balance_repo=BalanceDAO(self.db_manager),
                reporting_repo=ReportingDAO(self.db_manager),
                procedure_repo=ProcedureDAO(self.db_manager),
            )
            logger.info("✅ Application démarrée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de se connecter à la base : {e}")
            root.destroy()
            return
        
        # Variables de session
        self.societe_courante: Optional[Societe] = None
        self.exercice_courant: Optional[Exercice] = None

        # Créer l'interface
        self._create_ui()
        self.load_initial_data()
    
    def _create_ui(self):
        """Crée l'interface utilisateur avec les widgets extraits"""
        # Créer les callbacks pour le menu et la toolbar
        menu_callbacks = {
            'afficher_dashboard': self.afficher_dashboard,
            'import_csv': self.import_csv,
            'exporter_fec': self.exporter_fec,
            'quit_app': self.quit_app,
            'nouvelle_ecriture': self.nouvelle_ecriture,
            'saisie_vente': self.saisie_vente,
            'saisie_achat': self.saisie_achat,
            'ouvrir_lettrage': self.ouvrir_lettrage,
            'calculer_balance': self.calculer_balance,
            'afficher_balance': self.afficher_balance,
            'afficher_grand_livre': self.afficher_grand_livre,
            'afficher_resultat': self.afficher_resultat,
            'afficher_bilan': self.afficher_bilan,
            'afficher_tva': self.afficher_tva,
            'tester_comptabilite': self.tester_comptabilite,
            'cloturer_exercice': self.cloturer_exercice,
            'gestion_tiers': self.gestion_tiers,
            'about': self.about,
        }

        # Créer la barre de menu
        self.menubar = MenuBar(self.root, menu_callbacks)
        self.menubar.attach_to(self.root)

        # Créer la toolbar et la positionner
        self.toolbar = ToolBar(self.root, menu_callbacks)
        self.toolbar.frame.grid(row=0, column=0, sticky=(tk.W, tk.E), columnspan=2)

        # Créer les widgets centraux
        self._create_central_widgets()

        # Créer la barre de statut et la positionner
        self.statusbar = StatusBar(self.root)
        self.statusbar.frame.grid(row=4, column=0, sticky=(tk.W, tk.E), columnspan=2)

    def _create_central_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame supérieur : informations société/exercice
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), columnspan=2)
        
        ttk.Label(top_frame, text="Société:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.lbl_societe = ttk.Label(top_frame, text="Non sélectionnée", foreground='red')
        self.lbl_societe.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(top_frame, text="Exercice:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=20)
        self.lbl_exercice = ttk.Label(top_frame, text="Non sélectionné", foreground='red')
        self.lbl_exercice.grid(row=0, column=3, sticky=tk.W, padx=10)
        
        # Séparateur
        ttk.Separator(self.root, orient='horizontal').grid(row=2, column=0, sticky=(tk.W, tk.E), columnspan=2)

        # Frame principal avec notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10, columnspan=2)
        
        # Onglets
        self.create_tab_ecritures()
        self.create_tab_plan_comptable()
        self.create_tab_tiers()
        self.create_tab_dashboard()
        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)  # Le notebook est maintenant à row=3
    
    def create_tab_ecritures(self):
        """Onglet des écritures"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📝 Écritures")
        
        # Frame filtres
        filter_frame = ttk.LabelFrame(frame, text="Filtres", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Journal:").grid(row=0, column=0, sticky=tk.W)
        self.cmb_journal_filtre = ttk.Combobox(filter_frame, state='readonly', width=30)
        self.cmb_journal_filtre.grid(row=0, column=1, padx=5)
        
        ttk.Button(filter_frame, text="Filtrer", command=self.load_ecritures).grid(row=0, column=2, padx=5)
        ttk.Button(filter_frame, text="Nouvelle écriture", command=self.nouvelle_ecriture).grid(row=0, column=3, padx=5)
        
        # TreeView écritures
        columns = ('numero', 'date', 'journal', 'reference', 'libelle', 'montant')
        self.tree_ecritures = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        
        self.tree_ecritures.heading('numero', text='N° Écriture')
        self.tree_ecritures.heading('date', text='Date')
        self.tree_ecritures.heading('journal', text='Journal')
        self.tree_ecritures.heading('reference', text='Référence')
        self.tree_ecritures.heading('libelle', text='Libellé')
        self.tree_ecritures.heading('montant', text='Montant')
        
        self.tree_ecritures.column('numero', width=120)
        self.tree_ecritures.column('date', width=100)
        self.tree_ecritures.column('journal', width=80)
        self.tree_ecritures.column('reference', width=120)
        self.tree_ecritures.column('libelle', width=300)
        self.tree_ecritures.column('montant', width=120, anchor=tk.E)
        
        self.tree_ecritures.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_ecritures.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_ecritures.configure(yscrollcommand=scrollbar.set)
        
        # Double-clic pour voir détails
        self.tree_ecritures.bind('<Double-1>', self.voir_details_ecriture)
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
    
    def create_tab_plan_comptable(self):
        """Onglet plan comptable"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📊 Plan Comptable")
        
        # Frame recherche
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Recherche:").grid(row=0, column=0, sticky=tk.W)
        self.entry_search_compte = ttk.Entry(search_frame, width=40)
        self.entry_search_compte.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Chercher", command=self.search_comptes).grid(row=0, column=2, padx=5)
        
        # TreeView comptes
        columns = ('compte', 'intitule', 'classe', 'type')
        self.tree_comptes = ttk.Treeview(frame, columns=columns, show='headings', height=25)
        
        self.tree_comptes.heading('compte', text='N° Compte')
        self.tree_comptes.heading('intitule', text='Intitulé')
        self.tree_comptes.heading('classe', text='Classe')
        self.tree_comptes.heading('type', text='Type')
        
        self.tree_comptes.column('compte', width=100)
        self.tree_comptes.column('intitule', width=400)
        self.tree_comptes.column('classe', width=80)
        self.tree_comptes.column('type', width=120)
        
        self.tree_comptes.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_comptes.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_comptes.configure(yscrollcommand=scrollbar.set)
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
    
    def create_tab_tiers(self):
        """Onglet tiers"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="👥 Tiers")
        
        # Frame filtres
        filter_frame = ttk.Frame(frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Type:").grid(row=0, column=0, sticky=tk.W)
        self.cmb_type_tiers = ttk.Combobox(filter_frame, values=['Tous', 'CLIENT', 'FOURNISSEUR'], 
                                           state='readonly', width=20)
        self.cmb_type_tiers.set('Tous')
        self.cmb_type_tiers.grid(row=0, column=1, padx=5)
        ttk.Button(filter_frame, text="Filtrer", command=self.load_tiers).grid(row=0, column=2, padx=5)
        
        # TreeView tiers
        columns = ('code', 'nom', 'type', 'ville')
        self.tree_tiers = ttk.Treeview(frame, columns=columns, show='headings', height=25)
        
        self.tree_tiers.heading('code', text='Code')
        self.tree_tiers.heading('nom', text='Nom')
        self.tree_tiers.heading('type', text='Type')
        self.tree_tiers.heading('ville', text='Ville')
        
        self.tree_tiers.column('code', width=100)
        self.tree_tiers.column('nom', width=300)
        self.tree_tiers.column('type', width=120)
        self.tree_tiers.column('ville', width=150)
        
        self.tree_tiers.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_tiers.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_tiers.configure(yscrollcommand=scrollbar.set)
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
    
    def create_tab_dashboard(self):
        """Onglet tableau de bord"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📈 Tableau de bord")
        
        # Indicateurs
        indicators_frame = ttk.LabelFrame(frame, text="Indicateurs clés", padding="15")
        indicators_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.lbl_nb_ecritures = ttk.Label(indicators_frame, text="Écritures: 0", font=('Arial', 12))
        self.lbl_nb_ecritures.grid(row=0, column=0, padx=20)
        
        self.lbl_solde_banque = ttk.Label(indicators_frame, text="Banque: 0.00 €", font=('Arial', 12))
        self.lbl_solde_banque.grid(row=0, column=1, padx=20)
        
        self.lbl_tva_payer = ttk.Label(indicators_frame, text="TVA à payer: 0.00 €", font=('Arial', 12))
        self.lbl_tva_payer.grid(row=0, column=2, padx=20)
        
        # Boutons actions rapides
        actions_frame = ttk.LabelFrame(frame, text="Actions rapides", padding="15")
        actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(actions_frame, text="📝 Nouvelle Vente", 
                  command=self.saisie_vente, width=20).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(actions_frame, text="🛒 Nouvel Achat", 
                  command=self.saisie_achat, width=20).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(actions_frame, text="💰 Encaissement", 
                  command=self.nouvelle_ecriture, width=20).grid(row=0, column=2, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="⚖️ Calculer Balance", 
                  command=self.calculer_balance, width=20).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(actions_frame, text="📊 Compte de résultat", 
                  command=self.afficher_resultat, width=20).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(actions_frame, text="🧪 Tester comptabilité", 
                  command=self.tester_comptabilite, width=20).grid(row=1, column=2, padx=10, pady=5)
        
        # Zone informations
        info_frame = ttk.LabelFrame(frame, text="Informations", padding="15")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.text_info = tk.Text(info_frame, height=15, wrap=tk.WORD, state='disabled')
        self.text_info.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.text_info.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_info.configure(yscrollcommand=scrollbar.set)
        
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
    
    def load_initial_data(self):
        """Charge les données initiales"""
        # Charger la première société
        societes = self.service.get_societes()
        if societes:
            self.societe_courante = societes[0]
            self.lbl_societe.config(text=self.societe_courante.nom, foreground='green')

            # Mettre à jour la barre de statut
            self.statusbar.update_societe(self.societe_courante.nom)

            # Charger l'exercice en cours
            exercice = self.service.get_exercice_courant(self.societe_courante.id)
            if exercice:
                self.exercice_courant = exercice
                self.lbl_exercice.config(
                    text=f"{exercice.annee} ({exercice.date_debut} → {exercice.date_fin})",
                    foreground='green'
                )

                # Mettre à jour la barre de statut
                self.statusbar.update_exercice(exercice.annee, exercice.cloture)

            # Charger les journaux
            self.load_journaux()

            # Charger les données des onglets
            self.load_ecritures()
            self.load_comptes()
            self.load_tiers()
            self.update_dashboard()

            # Statut final
            self.statusbar.update_status("Prêt")
    
    def load_journaux(self):
        """Charge les journaux dans le combobox"""
        if not self.societe_courante:
            return
        
        journaux = self.service.get_journaux(self.societe_courante.id)
        self.journaux = {j.code: j for j in journaux}
        
        values = ['Tous'] + [f"{j.code} - {j.libelle}" for j in journaux]
        self.cmb_journal_filtre['values'] = values
        self.cmb_journal_filtre.set('Tous')
    
    def load_ecritures(self):
        """Charge les écritures"""
        if not self.exercice_courant:
            return
        
        # Effacer les données existantes
        for item in self.tree_ecritures.get_children():
            self.tree_ecritures.delete(item)
        
        # Récupérer les écritures
        ecritures = self.service.get_ecritures(self.exercice_courant.id)
        
        for ecriture in ecritures:
            # Calculer le montant total
            ecriture_complete = self.service.get_ecriture(ecriture.id)
            montant = sum(mvt.debit for mvt in ecriture_complete.mouvements) if ecriture_complete else 0
            
            self.tree_ecritures.insert('', tk.END, values=(
                ecriture.numero,
                ecriture.date_ecriture,
                ecriture.journal_id,  # À améliorer avec le nom du journal
                ecriture.reference_piece or '',
                ecriture.libelle or '',
                f"{montant:.2f} €"
            ))

        self.statusbar.update_status(f"{len(ecritures)} écritures chargées")
    
    def load_comptes(self):
        """Charge les comptes"""
        if not self.societe_courante:
            return
        
        # Effacer les données existantes
        for item in self.tree_comptes.get_children():
            self.tree_comptes.delete(item)
        
        # Récupérer les comptes
        comptes = self.service.get_comptes(self.societe_courante.id)
        
        for compte in comptes:
            self.tree_comptes.insert('', tk.END, values=(
                compte.compte,
                compte.intitule,
                compte.classe,
                compte.type_compte
            ))
    
    def load_tiers(self):
        """Charge les tiers"""
        if not self.societe_courante:
            return
        
        # Effacer les données existantes
        for item in self.tree_tiers.get_children():
            self.tree_tiers.delete(item)
        
        # Récupérer les tiers
        type_filtre = self.cmb_type_tiers.get()
        type_param = None if type_filtre == 'Tous' else type_filtre
        
        tiers = self.service.get_tiers(self.societe_courante.id, type_param)
        
        for t in tiers:
            self.tree_tiers.insert('', tk.END, values=(
                t.code_aux,
                t.nom,
                t.type,
                t.ville or ''
            ))

        self.statusbar.update_status(f"{len(tiers)} tiers chargés")
    
    def search_comptes(self):
        """Recherche des comptes"""
        if not self.societe_courante:
            return
        
        search_term = self.entry_search_compte.get()
        if not search_term:
            self.load_comptes()
            return
        
        # Effacer les données existantes
        for item in self.tree_comptes.get_children():
            self.tree_comptes.delete(item)
        
        # Recherche
        comptes = self.service.search_comptes(self.societe_courante.id, search_term)
        
        for compte in comptes:
            self.tree_comptes.insert('', tk.END, values=(
                compte.compte,
                compte.intitule,
                compte.classe,
                compte.type_compte
            ))

        self.statusbar.update_status(f"{len(comptes)} comptes trouvés")
    
    def update_dashboard(self):
        """Met à jour le tableau de bord"""
        if not self.exercice_courant or not self.societe_courante:
            return
        
        # Nombre d'écritures
        ecritures = self.service.get_ecritures(self.exercice_courant.id)
        self.lbl_nb_ecritures.config(text=f"Écritures: {len(ecritures)}")
        
        # Récupérer les informations financières
        try:
            resultat = self.service.get_compte_resultat(
                self.societe_courante.id, 
                self.exercice_courant.id
            )
            tva = self.service.get_tva_recap(
                self.societe_courante.id,
                self.exercice_courant.id
            )
            
            self.lbl_tva_payer.config(text=f"TVA à payer: {tva['tva_a_payer']:.2f} €")
            
            # Afficher les informations dans la zone texte
            self.text_info.config(state='normal')
            self.text_info.delete(1.0, tk.END)
            
            info_text = f"""
╔══════════════════════════════════════════════════╗
║          RÉSUMÉ FINANCIER - {self.exercice_courant.annee}          ║
╚══════════════════════════════════════════════════╝

📊 COMPTE DE RÉSULTAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Produits:      {resultat['total_produits']:>12.2f} €
  Charges:       {resultat['total_charges']:>12.2f} €
  ─────────────────────────────────────────────────
  Résultat:      {resultat['resultat']:>12.2f} €

💶 TVA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TVA Collectée: {tva['tva_collectee']:>12.2f} €
  TVA Déductible:{tva['tva_deductible']:>12.2f} €
  ─────────────────────────────────────────────────
  TVA à payer:   {tva['tva_a_payer']:>12.2f} €

✅ Statut: {"Exercice clôturé" if self.exercice_courant.cloture else "Exercice en cours"}
"""
            self.text_info.insert(1.0, info_text)
            self.text_info.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Erreur mise à jour dashboard : {e}")
    
    def nouvelle_ecriture(self):
        """Ouvre la fenêtre de saisie d'écriture"""
        if not self.exercice_courant:
            messagebox.showwarning("Attention", "Aucun exercice sélectionné")
            return
        
        from src.presentation.gui_ecriture import EcritureWindow
        EcritureWindow(self.root, self.service, self.societe_courante, 
                      self.exercice_courant, callback=self.load_ecritures)
    
    def saisie_vente(self):
        """Ouvre la fenêtre de saisie de vente"""
        if not self.exercice_courant:
            messagebox.showwarning("Attention", "Aucun exercice sélectionné")
            return
        
        from src.presentation.gui_vente import VenteWindow
        VenteWindow(self.root, self.service, self.societe_courante,
                   self.exercice_courant, callback=self.load_ecritures)
    
    def saisie_achat(self):
        """Ouvre la fenêtre de saisie d'achat"""
        if not self.exercice_courant:
            messagebox.showwarning("Attention", "Aucun exercice sélectionné")
            return
        
        from src.presentation.gui_achat import AchatWindow
        AchatWindow(self.root, self.service, self.societe_courante,
                   self.exercice_courant, callback=self.load_ecritures)
    
    def voir_details_ecriture(self, event):
        """Affiche les détails d'une écriture"""
        selection = self.tree_ecritures.selection()
        if not selection:
            return
        
        # À implémenter : fenêtre de détails
        messagebox.showinfo("Info", "Fonctionnalité à venir")
    
    def calculer_balance(self):
        """Calcule la balance"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        try:
            self.service.calculer_balance(self.societe_courante.id, self.exercice_courant.id)
            messagebox.showinfo("Succès", "✅ Balance calculée avec succès")
            self.update_dashboard()
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Erreur: {e}")
    
    def afficher_dashboard(self):
        """Affiche le tableau de bord"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return

        from src.presentation.gui_dashboard import DashboardWindow
        DashboardWindow(self.root, self.service, self.societe_courante, self.exercice_courant)

    def import_csv(self):
        """Ouvre la fenêtre d'import CSV"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return

        from src.presentation.gui_import import ImportCSVWindow
        ImportCSVWindow(self.root, self.service, self.societe_courante, self.exercice_courant)

    def afficher_balance(self):
        """Affiche la balance"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return

        from src.presentation.gui_rapports import BalanceWindow
        BalanceWindow(self.root, self.service, self.societe_courante, self.exercice_courant)
    
    def afficher_resultat(self):
        """Affiche le compte de résultat"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        from src.presentation.gui_rapports import ResultatWindow
        ResultatWindow(self.root, self.service, self.societe_courante, self.exercice_courant)
    
    def afficher_bilan(self):
        """Affiche le bilan"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        from src.presentation.gui_rapports import BilanWindow
        BilanWindow(self.root, self.service, self.societe_courante, self.exercice_courant)
    
    def afficher_tva(self):
        """Affiche le récapitulatif TVA"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        from src.presentation.gui_rapports import TVAWindow
        TVAWindow(self.root, self.service, self.societe_courante, self.exercice_courant)
    
    def tester_comptabilite(self):
        """Teste la cohérence comptable"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        try:
            resultats = self.service.tester_comptabilite(
                self.societe_courante.id,
                self.exercice_courant.id
            )
            
            # Afficher les résultats
            msg = "🧪 TESTS DE COHÉRENCE COMPTABLE\n\n"
            for key, value in resultats.items():
                msg += f"{key}: {value}\n"
            
            messagebox.showinfo("Tests comptables", msg)
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Erreur: {e}")
    
    def cloturer_exercice(self):
        """Clôture l'exercice"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        if self.exercice_courant.cloture:
            messagebox.showwarning("Attention", "Cet exercice est déjà clôturé")
            return
        
        reponse = messagebox.askyesno(
            "Confirmation",
            f"⚠️ Clôturer l'exercice {self.exercice_courant.annee} ?\n\n"
            "Cette opération :\n"
            "- Calcule le résultat\n"
            "- Crée l'exercice suivant\n"
            "- Génère le report à nouveau\n\n"
            "Continuer ?"
        )
        
        if reponse:
            try:
                success, message = self.service.cloturer_exercice(
                    self.societe_courante.id,
                    self.exercice_courant.id
                )
                
                if success:
                    messagebox.showinfo("Succès", message)
                    self.load_initial_data()
                else:
                    messagebox.showerror("Erreur", message)
            except Exception as e:
                messagebox.showerror("Erreur", f"❌ {e}")
    
    def exporter_fec(self):
        """Exporte le FEC"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return
        
        try:
            success, message = self.service.exporter_fec(
                self.societe_courante.id,
                self.exercice_courant.id
            )
            
            if success:
                messagebox.showinfo("Succès", message)
            else:
                messagebox.showerror("Erreur", message)
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ {e}")
    
    def ouvrir_lettrage(self):
        """Ouvre la fenêtre de lettrage"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return

        from src.presentation.gui_lettrage import LettrageWindow
        LettrageWindow(self.root, self.service, self.societe_courante, self.exercice_courant)

    def afficher_grand_livre(self):
        """Affiche le Grand Livre"""
        if not self.exercice_courant or not self.societe_courante:
            messagebox.showwarning("Attention", "Société ou exercice non sélectionné")
            return

        from src.presentation.gui_grand_livre import GrandLivreWindow
        GrandLivreWindow(self.root, self.service, self.societe_courante, self.exercice_courant)

    def gestion_tiers(self):
        """Ouvre la fenêtre de gestion des tiers"""
        if not self.societe_courante:
            messagebox.showwarning("Attention", "Aucune société sélectionnée")
            return

        from src.presentation.gui_tiers import TiersWindow
        TiersWindow(self.root, self.service, self.societe_courante, callback=self.load_tiers)

    def about(self):
        """Affiche les informations sur l'application"""
        messagebox.showinfo(
            "À propos",
            "Système de Comptabilité Générale\n"
            "Version 2.5 - ÉDITION COMPLÈTE\n\n"
            "✅ Saisie d'écritures (manuelle, ventes, achats)\n"
            "✅ Lettrage comptable automatique\n"
            "✅ Grand Livre détaillé\n"
            "✅ Rapports: Balance, Bilan, Compte de résultat, TVA\n"
            "✅ Exports Excel et CSV\n"
            "✅ Gestion des tiers\n"
            "✅ Export FEC\n\n"
            "Conforme au Plan Comptable Général (PCG)\n"
            "© 2025 - Application professionnelle"
        )
    
    def quit_app(self):
        """Quitte l'application"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
            self.db_manager.disconnect()
            self.root.destroy()


def main():
    """Point d'entrée de l'application"""
    root = tk.Tk()
    app = ComptaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.mainloop()


if __name__ == "__main__":
    main()
