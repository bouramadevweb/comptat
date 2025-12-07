"""
Fenêtre de lettrage comptable
"""
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from typing import Optional


class LettrageWindow:
    """Fenêtre de lettrage des comptes"""

    def __init__(self, parent, service, societe, exercice):
        self.service = service
        self.societe = societe
        self.exercice = exercice
        self.compte_selectionne = None
        self.mouvements_selection = []

        self.window = tk.Toplevel(parent)
        self.window.title("Lettrage Comptable")
        self.window.geometry("1400x800")
        self.window.transient(parent)

        self.create_widgets()
        self.load_comptes()

    def create_widgets(self):
        """Crée les widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titre
        ttk.Label(main_frame, text="🔗 LETTRAGE COMPTABLE",
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Frame gauche : Sélection du compte
        left_frame = ttk.LabelFrame(main_frame, text="Sélection du compte", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        ttk.Label(left_frame, text="Compte lettrable:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cmb_compte = ttk.Combobox(left_frame, width=50, state='readonly')
        self.cmb_compte.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.cmb_compte.bind('<<ComboboxSelected>>', self.on_compte_selected)

        ttk.Button(left_frame, text="Charger", command=self.load_mouvements).grid(row=2, column=0, pady=10)

        # Informations sur le compte
        self.lbl_info_compte = ttk.Label(left_frame, text="", foreground='blue', wraplength=300)
        self.lbl_info_compte.grid(row=3, column=0, sticky=tk.W, pady=10)

        left_frame.columnconfigure(0, weight=1)

        # Frame droite : Mouvements non lettrés
        right_frame = ttk.LabelFrame(main_frame, text="Mouvements non lettrés", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # TreeView mouvements
        columns = ('id', 'date', 'ecriture', 'libelle', 'debit', 'credit', 'solde')
        self.tree_mouvements = ttk.Treeview(right_frame, columns=columns, show='headings',
                                           height=20, selectmode='extended')

        self.tree_mouvements.heading('id', text='ID')
        self.tree_mouvements.heading('date', text='Date')
        self.tree_mouvements.heading('ecriture', text='N° Écriture')
        self.tree_mouvements.heading('libelle', text='Libellé')
        self.tree_mouvements.heading('debit', text='Débit')
        self.tree_mouvements.heading('credit', text='Crédit')
        self.tree_mouvements.heading('solde', text='Solde')

        self.tree_mouvements.column('id', width=50)
        self.tree_mouvements.column('date', width=100)
        self.tree_mouvements.column('ecriture', width=100)
        self.tree_mouvements.column('libelle', width=250)
        self.tree_mouvements.column('debit', width=100, anchor=tk.E)
        self.tree_mouvements.column('credit', width=100, anchor=tk.E)
        self.tree_mouvements.column('solde', width=100, anchor=tk.E)

        self.tree_mouvements.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree_mouvements.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_mouvements.configure(yscrollcommand=scrollbar.set)

        # Boutons d'action
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=1, column=0, pady=10)

        ttk.Button(btn_frame, text="🔗 Lettrer la sélection",
                  command=self.lettrer_selection).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="🔗 Lettrage automatique",
                  command=self.lettrage_automatique).grid(row=0, column=1, padx=5)

        # Solde de la sélection
        self.lbl_solde_selection = ttk.Label(right_frame, text="Solde sélection: 0.00 €",
                                            font=('Arial', 10, 'bold'))
        self.lbl_solde_selection.grid(row=2, column=0, pady=5)

        self.tree_mouvements.bind('<<TreeviewSelect>>', self.on_selection_changed)

        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # Frame mouvements lettrés
        lettre_frame = ttk.LabelFrame(main_frame, text="Mouvements lettrés", padding="10")
        lettre_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # TreeView lettrés
        columns_lettre = ('code', 'date', 'ecriture', 'libelle', 'debit', 'credit')
        self.tree_lettres = ttk.Treeview(lettre_frame, columns=columns_lettre,
                                        show='headings', height=20)

        self.tree_lettres.heading('code', text='Code')
        self.tree_lettres.heading('date', text='Date')
        self.tree_lettres.heading('ecriture', text='Écriture')
        self.tree_lettres.heading('libelle', text='Libellé')
        self.tree_lettres.heading('debit', text='Débit')
        self.tree_lettres.heading('credit', text='Crédit')

        self.tree_lettres.column('code', width=60)
        self.tree_lettres.column('date', width=100)
        self.tree_lettres.column('ecriture', width=100)
        self.tree_lettres.column('libelle', width=200)
        self.tree_lettres.column('debit', width=100, anchor=tk.E)
        self.tree_lettres.column('credit', width=100, anchor=tk.E)

        self.tree_lettres.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar2 = ttk.Scrollbar(lettre_frame, orient=tk.VERTICAL, command=self.tree_lettres.yview)
        scrollbar2.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_lettres.configure(yscrollcommand=scrollbar2.set)

        ttk.Button(lettre_frame, text="❌ Délettrer",
                  command=self.delettrer).grid(row=1, column=0, pady=10)

        lettre_frame.columnconfigure(0, weight=1)
        lettre_frame.rowconfigure(0, weight=1)

        # Configuration du redimensionnement
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def load_comptes(self):
        """Charge les comptes lettrables"""
        comptes = self.service.get_comptes(self.societe.id)
        comptes_lettrables = [c for c in comptes if c.lettrable]

        values = [f"{c.compte} - {c.intitule}" for c in comptes_lettrables]
        self.cmb_compte['values'] = values

        if values:
            self.cmb_compte.set(values[0])

    def on_compte_selected(self, event=None):
        """Appelé quand un compte est sélectionné"""
        self.load_mouvements()

    def load_mouvements(self):
        """Charge les mouvements du compte sélectionné"""
        selection = self.cmb_compte.get()
        if not selection:
            return

        # Extraire le numéro de compte
        compte_numero = selection.split(' - ')[0]
        self.compte_selectionne = compte_numero

        # Effacer les anciennes données
        for item in self.tree_mouvements.get_children():
            self.tree_mouvements.delete(item)

        for item in self.tree_lettres.get_children():
            self.tree_lettres.delete(item)

        # Charger les mouvements non lettrés
        try:
            mouvements = self.service.get_mouvements_a_lettrer(
                self.societe.id,
                self.exercice.id,
                compte_numero
            )

            total_solde = Decimal('0')
            for mvt in mouvements:
                solde = Decimal(str(mvt.get('solde', 0)))
                total_solde += solde

                self.tree_mouvements.insert('', tk.END, values=(
                    mvt['mouvement_id'],
                    mvt['date'],
                    mvt['ecriture_numero'],
                    mvt['libelle'],
                    f"{mvt['debit']:.2f}",
                    f"{mvt['credit']:.2f}",
                    f"{solde:.2f}"
                ))

            # Charger les mouvements lettrés
            lettres = self.service.get_mouvements_lettres(
                self.societe.id,
                self.exercice.id,
                compte_numero
            )

            for code, mouvements in lettres.items():
                for mvt in mouvements:
                    self.tree_lettres.insert('', tk.END, values=(
                        code,
                        mvt['date'],
                        mvt['ecriture_numero'],
                        mvt['libelle'],
                        f"{mvt['debit']:.2f}",
                        f"{mvt['credit']:.2f}"
                    ))

            # Afficher les infos
            self.lbl_info_compte.config(
                text=f"Compte: {compte_numero}\n"
                     f"{len(mouvements)} mouvements non lettrés\n"
                     f"Solde total: {total_solde:.2f} €\n"
                     f"{len(lettres)} lettrages existants"
            )

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")

    def on_selection_changed(self, event=None):
        """Appelé quand la sélection change"""
        selection = self.tree_mouvements.selection()

        total_debit = Decimal('0')
        total_credit = Decimal('0')

        for item in selection:
            values = self.tree_mouvements.item(item)['values']
            total_debit += Decimal(str(values[4]))
            total_credit += Decimal(str(values[5]))

        solde = total_debit - total_credit

        if abs(solde) < 0.01:
            color = 'green'
            text = f"✅ Solde sélection: {solde:.2f} € (Équilibré)"
        else:
            color = 'red'
            text = f"❌ Solde sélection: {solde:.2f} € (Déséquilibré)"

        self.lbl_solde_selection.config(text=text, foreground=color)

    def lettrer_selection(self):
        """Lettre les mouvements sélectionnés"""
        selection = self.tree_mouvements.selection()

        if len(selection) < 2:
            messagebox.showwarning("Attention",
                                 "Sélectionnez au moins 2 mouvements à lettrer")
            return

        # Récupérer les IDs
        mouvement_ids = []
        for item in selection:
            values = self.tree_mouvements.item(item)['values']
            mouvement_ids.append(int(values[0]))

        # Lettrer
        try:
            success, message = self.service.lettrer_mouvements(mouvement_ids)

            if success:
                messagebox.showinfo("Succès", message)
                self.load_mouvements()
            else:
                messagebox.showerror("Erreur", message)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du lettrage: {e}")

    def lettrage_automatique(self):
        """Tente un lettrage automatique des mouvements qui s'équilibrent"""
        if not self.compte_selectionne:
            return

        try:
            # Récupérer tous les mouvements non lettrés
            mouvements = self.service.get_mouvements_a_lettrer(
                self.societe.id,
                self.exercice.id,
                self.compte_selectionne
            )

            if len(mouvements) < 2:
                messagebox.showinfo("Info", "Pas assez de mouvements pour un lettrage automatique")
                return

            # Grouper par montant opposé
            lettrages_trouves = 0

            # Chercher des paires qui s'équilibrent
            for i, mvt1 in enumerate(mouvements):
                solde1 = Decimal(str(mvt1['solde']))

                for mvt2 in mouvements[i+1:]:
                    solde2 = Decimal(str(mvt2['solde']))

                    # Si les soldes sont opposés (s'annulent)
                    if abs(solde1 + solde2) < 0.01:
                        ids = [mvt1['mouvement_id'], mvt2['mouvement_id']]
                        success, _ = self.service.lettrer_mouvements(ids)

                        if success:
                            lettrages_trouves += 1

            if lettrages_trouves > 0:
                messagebox.showinfo("Succès",
                                  f"✅ {lettrages_trouves} lettrage(s) automatique(s) effectué(s)")
                self.load_mouvements()
            else:
                messagebox.showinfo("Info",
                                  "Aucun lettrage automatique trouvé")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")

    def delettrer(self):
        """Délètre le code sélectionné"""
        selection = self.tree_lettres.selection()

        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un lettrage à supprimer")
            return

        # Récupérer le code de lettrage
        values = self.tree_lettres.item(selection[0])['values']
        code_lettrage = values[0]

        # Confirmer
        if not messagebox.askyesno("Confirmation",
                                  f"Délettrer le code {code_lettrage} ?"):
            return

        try:
            success, message = self.service.delettrer_mouvements(code_lettrage)

            if success:
                messagebox.showinfo("Succès", message)
                self.load_mouvements()
            else:
                messagebox.showerror("Erreur", message)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du délettrage: {e}")
