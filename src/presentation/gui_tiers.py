"""
Fenêtre de gestion des tiers (CRUD)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.domain.models import Tiers
from typing import Callable, Optional


class TiersWindow:
    """Fenêtre de gestion des tiers (clients et fournisseurs)"""

    def __init__(self, parent, service, societe, callback: Callable = None):
        self.service = service
        self.societe = societe
        self.callback = callback
        self.tiers_selectionne = None

        self.window = tk.Toplevel(parent)
        self.window.title("Gestion des Tiers")
        self.window.geometry("1200x700")
        self.window.transient(parent)

        self.create_widgets()
        self.load_tiers()

    def create_widgets(self):
        """Crée les widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titre
        ttk.Label(main_frame, text="👥 GESTION DES TIERS",
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Frame gauche : Liste des tiers
        left_frame = ttk.LabelFrame(main_frame, text="Liste des tiers", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Filtres
        filter_frame = ttk.Frame(left_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Type:").grid(row=0, column=0, sticky=tk.W)
        self.cmb_type_filtre = ttk.Combobox(filter_frame,
                                           values=['Tous', 'CLIENT', 'FOURNISSEUR'],
                                           state='readonly', width=15)
        self.cmb_type_filtre.set('Tous')
        self.cmb_type_filtre.grid(row=0, column=1, padx=5)
        ttk.Button(filter_frame, text="Filtrer", command=self.load_tiers).grid(row=0, column=2, padx=5)

        # TreeView
        columns = ('code', 'nom', 'type', 'ville', 'pays')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=25)

        self.tree.heading('code', text='Code')
        self.tree.heading('nom', text='Nom')
        self.tree.heading('type', text='Type')
        self.tree.heading('ville', text='Ville')
        self.tree.heading('pays', text='Pays')

        self.tree.column('code', width=100)
        self.tree.column('nom', width=250)
        self.tree.column('type', width=120)
        self.tree.column('ville', width=150)
        self.tree.column('pays', width=60)

        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('<<TreeviewSelect>>', self.on_tiers_selected)

        # Boutons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, pady=10)

        ttk.Button(btn_frame, text="➕ Nouveau", command=self.nouveau_tiers).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="✏️ Modifier", command=self.modifier_tiers).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="❌ Supprimer", command=self.supprimer_tiers).grid(row=0, column=2, padx=5)

        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # Frame droite : Formulaire
        right_frame = ttk.LabelFrame(main_frame, text="Informations", padding="15")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        row = 0

        # Code
        ttk.Label(right_frame, text="Code auxiliaire:").grid(row=row, column=0, sticky=tk.W, pady=8)
        self.entry_code = ttk.Entry(right_frame, width=30)
        self.entry_code.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8)
        row += 1

        # Nom
        ttk.Label(right_frame, text="Nom:").grid(row=row, column=0, sticky=tk.W, pady=8)
        self.entry_nom = ttk.Entry(right_frame, width=30)
        self.entry_nom.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8)
        row += 1

        # Type
        ttk.Label(right_frame, text="Type:").grid(row=row, column=0, sticky=tk.W, pady=8)
        self.cmb_type = ttk.Combobox(right_frame, values=['CLIENT', 'FOURNISSEUR'],
                                    state='readonly', width=28)
        self.cmb_type.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8)
        row += 1

        # Adresse
        ttk.Label(right_frame, text="Adresse:").grid(row=row, column=0, sticky=tk.W, pady=8)
        self.entry_adresse = ttk.Entry(right_frame, width=30)
        self.entry_adresse.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8)
        row += 1

        # Ville
        ttk.Label(right_frame, text="Ville:").grid(row=row, column=0, sticky=tk.W, pady=8)
        self.entry_ville = ttk.Entry(right_frame, width=30)
        self.entry_ville.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8)
        row += 1

        # Pays
        ttk.Label(right_frame, text="Pays (code):").grid(row=row, column=0, sticky=tk.W, pady=8)
        self.entry_pays = ttk.Entry(right_frame, width=30)
        self.entry_pays.insert(0, "FR")
        self.entry_pays.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8)
        row += 1

        # Boutons d'action
        btn_action_frame = ttk.Frame(right_frame)
        btn_action_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_action_frame, text="💾 Enregistrer",
                  command=self.enregistrer, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(btn_action_frame, text="🔄 Annuler",
                  command=self.annuler, width=15).grid(row=0, column=1, padx=5)

        right_frame.columnconfigure(1, weight=1)

        # Configuration redimensionnement
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def load_tiers(self):
        """Charge la liste des tiers"""
        # Effacer l'ancienne liste
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupérer le filtre
        type_filtre = self.cmb_type_filtre.get()
        if type_filtre == 'Tous':
            type_filtre = None

        # Charger les tiers
        try:
            tiers = self.service.get_tiers(self.societe.id, type_filtre)

            for t in tiers:
                self.tree.insert('', tk.END, iid=t.id, values=(
                    t.code_aux,
                    t.nom,
                    t.type,
                    t.ville or '',
                    t.pays or ''
                ))

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")

    def on_tiers_selected(self, event=None):
        """Appelé quand un tiers est sélectionné"""
        selection = self.tree.selection()
        if not selection:
            return

        # Récupérer le tiers
        tiers_id = int(selection[0])

        # Récupérer les détails depuis les values
        values = self.tree.item(selection[0])['values']

        # Remplir le formulaire
        self.entry_code.delete(0, tk.END)
        self.entry_code.insert(0, values[0])

        self.entry_nom.delete(0, tk.END)
        self.entry_nom.insert(0, values[1])

        self.cmb_type.set(values[2])

        self.entry_adresse.delete(0, tk.END)

        self.entry_ville.delete(0, tk.END)
        self.entry_ville.insert(0, values[3])

        self.entry_pays.delete(0, tk.END)
        self.entry_pays.insert(0, values[4] if values[4] else 'FR')

        self.tiers_selectionne = tiers_id

    def nouveau_tiers(self):
        """Prépare la saisie d'un nouveau tiers"""
        self.tiers_selectionne = None
        self.annuler()
        self.entry_code.focus()

    def modifier_tiers(self):
        """Prépare la modification d'un tiers"""
        if not self.tree.selection():
            messagebox.showwarning("Attention", "Sélectionnez un tiers à modifier")
            return

        self.entry_code.focus()

    def enregistrer(self):
        """Enregistre le tiers"""
        # Validation
        if not self.entry_code.get():
            messagebox.showwarning("Attention", "Le code est obligatoire")
            self.entry_code.focus()
            return

        if not self.entry_nom.get():
            messagebox.showwarning("Attention", "Le nom est obligatoire")
            self.entry_nom.focus()
            return

        if not self.cmb_type.get():
            messagebox.showwarning("Attention", "Le type est obligatoire")
            self.cmb_type.focus()
            return

        # Créer l'objet Tiers
        tiers = Tiers(
            id=self.tiers_selectionne,
            societe_id=self.societe.id,
            code_aux=self.entry_code.get().strip().upper(),
            nom=self.entry_nom.get().strip(),
            type=self.cmb_type.get(),
            adresse=self.entry_adresse.get().strip() or None,
            ville=self.entry_ville.get().strip() or None,
            pays=self.entry_pays.get().strip().upper() or 'FR'
        )

        try:
            if self.tiers_selectionne:
                # Modification
                success, message = self.service.update_tiers(tiers)
                if success:
                    messagebox.showinfo("Succès", message)
                else:
                    messagebox.showerror("Erreur", message)
                    return
            else:
                # Création
                tiers_id = self.service.create_tiers(tiers)
                messagebox.showinfo("Succès", f"✅ Tiers créé avec l'ID {tiers_id}")

            # Recharger et notifier
            self.load_tiers()
            self.annuler()

            if self.callback:
                self.callback()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {e}")

    def annuler(self):
        """Annule la saisie"""
        self.tiers_selectionne = None

        self.entry_code.delete(0, tk.END)
        self.entry_nom.delete(0, tk.END)
        self.cmb_type.set('')
        self.entry_adresse.delete(0, tk.END)
        self.entry_ville.delete(0, tk.END)
        self.entry_pays.delete(0, tk.END)
        self.entry_pays.insert(0, 'FR')

        # Déselectionner dans le tree
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def supprimer_tiers(self):
        """Supprime le tiers sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un tiers à supprimer")
            return

        tiers_id = int(selection[0])
        values = self.tree.item(selection[0])['values']
        nom = values[1]

        if not messagebox.askyesno("Confirmation",
                                  f"Supprimer le tiers '{nom}' ?\n\n"
                                  f"⚠️ Cette action est irréversible."):
            return

        try:
            success, message = self.service.delete_tiers(tiers_id)

            if success:
                messagebox.showinfo("Succès", message)
                self.load_tiers()
                self.annuler()

                if self.callback:
                    self.callback()
            else:
                messagebox.showwarning("Attention", message)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
