"""
Tableau de bord avec statistiques et KPIs
"""
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DashboardWindow:
    """Fenêtre de tableau de bord avec statistiques"""

    def __init__(self, parent, service, societe, exercice):
        self.service = service
        self.societe = societe
        self.exercice = exercice

        self.window = tk.Toplevel(parent)
        self.window.title(f"📊 Tableau de Bord - {societe.nom} - Exercice {exercice.annee}")
        self.window.geometry("1200x800")
        self.window.transient(parent)

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Crée l'interface du dashboard"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titre
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(title_frame, text=f"📊 TABLEAU DE BORD",
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

        ttk.Button(title_frame, text="🔄 Actualiser",
                  command=self.load_data).pack(side=tk.RIGHT, padx=5)

        # ROW 1: KPIs Principaux
        kpis_frame = ttk.LabelFrame(main_frame, text="📈 Indicateurs Clés (KPIs)", padding="15")
        kpis_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        self.kpi_widgets = {}
        kpis = [
            ("ca", "💰 Chiffre d'Affaires", "#2E7D32"),
            ("charges", "📉 Charges", "#C62828"),
            ("resultat", "📊 Résultat", "#1565C0"),
            ("tresorerie", "💵 Trésorerie", "#F57C00"),
        ]

        for idx, (key, label, color) in enumerate(kpis):
            frame = ttk.Frame(kpis_frame)
            frame.grid(row=0, column=idx, padx=10, sticky=(tk.W, tk.E))

            ttk.Label(frame, text=label, font=('Arial', 10)).pack()
            value_label = ttk.Label(frame, text="0.00 €", font=('Arial', 14, 'bold'),
                                   foreground=color)
            value_label.pack()
            self.kpi_widgets[key] = value_label

        kpis_frame.columnconfigure(0, weight=1)
        kpis_frame.columnconfigure(1, weight=1)
        kpis_frame.columnconfigure(2, weight=1)
        kpis_frame.columnconfigure(3, weight=1)

        # ROW 2: Colonnes gauche et droite
        left_column = ttk.Frame(main_frame)
        left_column.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        right_column = ttk.Frame(main_frame)
        right_column.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # TVA
        tva_frame = ttk.LabelFrame(left_column, text="💸 TVA", padding="10")
        tva_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.tva_widgets = {}
        for key, label in [("collectee", "Collectée"), ("deductible", "Déductible"), ("a_payer", "À Payer")]:
            frame = ttk.Frame(tva_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=f"{label}:", width=12).pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0.00 €", font=('Arial', 10, 'bold'))
            value_label.pack(side=tk.LEFT)
            self.tva_widgets[key] = value_label

        # Compteurs
        compteurs_frame = ttk.LabelFrame(left_column, text="📋 Statistiques", padding="10")
        compteurs_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.stat_widgets = {}
        for key, label in [
            ("nb_ecritures", "Nombre d'écritures"),
            ("nb_clients", "Clients"),
            ("nb_fournisseurs", "Fournisseurs"),
            ("nb_comptes_utilises", "Comptes utilisés")
        ]:
            frame = ttk.Frame(compteurs_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=f"{label}:", width=18).pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0", font=('Arial', 10, 'bold'))
            value_label.pack(side=tk.LEFT)
            self.stat_widgets[key] = value_label

        # Top Clients/Fournisseurs
        top_frame = ttk.LabelFrame(right_column, text="🏆 Top 5 Tiers", padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Clients
        ttk.Label(top_frame, text="Top 5 Clients", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.tree_clients = ttk.Treeview(top_frame, columns=('nom', 'ca'), show='headings', height=5)
        self.tree_clients.heading('nom', text='Client')
        self.tree_clients.heading('ca', text='CA (€)')
        self.tree_clients.column('nom', width=200)
        self.tree_clients.column('ca', width=100)
        self.tree_clients.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Fournisseurs
        ttk.Label(top_frame, text="Top 5 Fournisseurs", font=('Arial', 11, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))

        self.tree_fournisseurs = ttk.Treeview(top_frame, columns=('nom', 'montant'), show='headings', height=5)
        self.tree_fournisseurs.heading('nom', text='Fournisseur')
        self.tree_fournisseurs.heading('montant', text='Montant (€)')
        self.tree_fournisseurs.column('nom', width=200)
        self.tree_fournisseurs.column('montant', width=100)
        self.tree_fournisseurs.grid(row=3, column=0, sticky=(tk.W, tk.E))

        # Configuration du redimensionnement
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(2, weight=1)

        left_column.rowconfigure(1, weight=1)
        right_column.rowconfigure(0, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def load_data(self):
        """Charge toutes les données du dashboard"""
        try:
            self.load_kpis()
            self.load_tva()
            self.load_statistics()
            self.load_top_tiers()
        except Exception as e:
            logger.error(f"❌ Erreur chargement dashboard: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")

    def load_kpis(self):
        """Charge les KPIs principaux"""
        try:
            # Compte de résultat
            resultat = self.service.get_compte_resultat(self.societe.id, self.exercice.id)

            charges = resultat.get('total_charges', Decimal('0'))
            produits = resultat.get('total_produits', Decimal('0'))
            res = resultat.get('resultat', Decimal('0'))

            # Trésorerie (somme des comptes 51x et 53x)
            tresorerie = self.get_tresorerie()

            # Mise à jour
            self.kpi_widgets['ca'].config(text=f"{produits:,.2f} €")
            self.kpi_widgets['charges'].config(text=f"{charges:,.2f} €")

            # Résultat avec couleur
            resultat_text = f"{res:,.2f} €"
            resultat_color = "#2E7D32" if res >= 0 else "#C62828"
            self.kpi_widgets['resultat'].config(text=resultat_text, foreground=resultat_color)

            self.kpi_widgets['tresorerie'].config(text=f"{tresorerie:,.2f} €")

        except Exception as e:
            logger.error(f"❌ Erreur load_kpis: {e}")

    def get_tresorerie(self):
        """Calcule la trésorerie (banques + caisse)"""
        try:
            query = """
                SELECT COALESCE(SUM(total_debit - total_credit), 0) as tresorerie
                FROM BALANCE
                WHERE societe_id = %s
                  AND exercice_id = %s
                  AND (compte LIKE '51%' OR compte LIKE '53%')
            """
            result = self.service.db.execute_query(query, (self.societe.id, self.exercice.id))
            if result and result[0]:
                return Decimal(str(result[0]['tresorerie']))
            return Decimal('0')
        except:
            return Decimal('0')

    def load_tva(self):
        """Charge les données TVA"""
        try:
            tva_data = self.service.get_tva_recap(self.societe.id, self.exercice.id)

            self.tva_widgets['collectee'].config(text=f"{tva_data['tva_collectee']:,.2f} €")
            self.tva_widgets['deductible'].config(text=f"{tva_data['tva_deductible']:,.2f} €")

            tva_a_payer = tva_data['tva_a_payer']
            color = "#C62828" if tva_a_payer > 0 else "#2E7D32"
            self.tva_widgets['a_payer'].config(text=f"{tva_a_payer:,.2f} €", foreground=color)

        except Exception as e:
            logger.error(f"❌ Erreur load_tva: {e}")

    def load_statistics(self):
        """Charge les statistiques"""
        try:
            # Nombre d'écritures
            query = "SELECT COUNT(*) as nb FROM ECRITURES WHERE exercice_id = %s"
            result = self.service.db.execute_query(query, (self.exercice.id,))
            nb_ecritures = result[0]['nb'] if result else 0

            # Nombre de clients
            clients = self.service.get_tiers(self.societe.id, 'CLIENT')
            nb_clients = len(clients)

            # Nombre de fournisseurs
            fournisseurs = self.service.get_tiers(self.societe.id, 'FOURNISSEUR')
            nb_fournisseurs = len(fournisseurs)

            # Nombre de comptes utilisés
            query = """
                SELECT COUNT(DISTINCT compte_id) as nb
                FROM MOUVEMENTS m
                JOIN ECRITURES e ON m.ecriture_id = e.id
                WHERE e.exercice_id = %s
            """
            result = self.service.db.execute_query(query, (self.exercice.id,))
            nb_comptes = result[0]['nb'] if result else 0

            # Mise à jour
            self.stat_widgets['nb_ecritures'].config(text=str(nb_ecritures))
            self.stat_widgets['nb_clients'].config(text=str(nb_clients))
            self.stat_widgets['nb_fournisseurs'].config(text=str(nb_fournisseurs))
            self.stat_widgets['nb_comptes_utilises'].config(text=str(nb_comptes))

        except Exception as e:
            logger.error(f"❌ Erreur load_statistics: {e}")

    def load_top_tiers(self):
        """Charge les top clients et fournisseurs"""
        try:
            # Top 5 clients (CA = somme des crédits sur compte 411xxx)
            query = """
                SELECT t.nom, SUM(m.debit) as ca
                FROM MOUVEMENTS m
                JOIN ECRITURES e ON m.ecriture_id = e.id
                JOIN COMPTES c ON m.compte_id = c.id
                JOIN TIERS t ON m.tiers_id = t.id
                WHERE e.exercice_id = %s
                  AND c.compte LIKE '411%%'
                  AND t.type = 'CLIENT'
                GROUP BY t.id, t.nom
                ORDER BY ca DESC
                LIMIT 5
            """
            clients = self.service.db.execute_query(query, (self.exercice.id,))

            # Effacer et remplir
            for item in self.tree_clients.get_children():
                self.tree_clients.delete(item)

            for client in clients:
                self.tree_clients.insert('', tk.END, values=(
                    client['nom'],
                    f"{float(client['ca']):,.2f}"
                ))

            # Top 5 fournisseurs (somme des crédits sur compte 401xxx)
            query = """
                SELECT t.nom, SUM(m.credit) as montant
                FROM MOUVEMENTS m
                JOIN ECRITURES e ON m.ecriture_id = e.id
                JOIN COMPTES c ON m.compte_id = c.id
                JOIN TIERS t ON m.tiers_id = t.id
                WHERE e.exercice_id = %s
                  AND c.compte LIKE '401%%'
                  AND t.type = 'FOURNISSEUR'
                GROUP BY t.id, t.nom
                ORDER BY montant DESC
                LIMIT 5
            """
            fournisseurs = self.service.db.execute_query(query, (self.exercice.id,))

            # Effacer et remplir
            for item in self.tree_fournisseurs.get_children():
                self.tree_fournisseurs.delete(item)

            for fournisseur in fournisseurs:
                self.tree_fournisseurs.insert('', tk.END, values=(
                    fournisseur['nom'],
                    f"{float(fournisseur['montant']):,.2f}"
                ))

        except Exception as e:
            logger.error(f"❌ Erreur load_top_tiers: {e}")
