"""
Fenêtre de saisie manuelle d'écriture comptable
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal
from typing import Callable
from src.domain.models import Ecriture, Mouvement


class EcritureWindow:
    """Fenêtre de saisie manuelle d'écriture"""
    
    def __init__(self, parent, service, societe, exercice, callback: Callable = None):
        self.service = service
        self.societe = societe
        self.exercice = exercice
        self.callback = callback
        self.mouvements = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nouvelle Écriture")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Crée les widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # En-tête
        header_frame = ttk.LabelFrame(main_frame, text="En-tête de l'écriture", padding="10")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Journal
        ttk.Label(header_frame, text="Journal:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cmb_journal = ttk.Combobox(header_frame, state='readonly', width=35)
        self.cmb_journal.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Date
        ttk.Label(header_frame, text="Date:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.entry_date = ttk.Entry(header_frame, width=15)
        self.entry_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
        
        # Référence
        ttk.Label(header_frame, text="Référence:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_reference = ttk.Entry(header_frame, width=37)
        self.entry_reference.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Libellé
        ttk.Label(header_frame, text="Libellé:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.entry_libelle = ttk.Entry(header_frame, width=37)
        self.entry_libelle.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Lignes d'écriture
        lignes_frame = ttk.LabelFrame(main_frame, text="Lignes de l'écriture", padding="10")
        lignes_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Formulaire d'ajout de ligne
        add_frame = ttk.Frame(lignes_frame)
        add_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(add_frame, text="Compte:").grid(row=0, column=0, sticky=tk.W)
        self.cmb_compte = ttk.Combobox(add_frame, width=35)
        self.cmb_compte.grid(row=0, column=1, padx=5)
        self.cmb_compte.bind('<KeyRelease>', self.search_compte)
        
        ttk.Label(add_frame, text="Libellé ligne:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.entry_ligne_libelle = ttk.Entry(add_frame, width=25)
        self.entry_ligne_libelle.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Débit:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.entry_debit = ttk.Entry(add_frame, width=15)
        self.entry_debit.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(5, 0))
        
        ttk.Label(add_frame, text="Crédit:").grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        self.entry_credit = ttk.Entry(add_frame, width=15)
        self.entry_credit.grid(row=1, column=3, sticky=tk.W, padx=5, pady=(5, 0))
        
        ttk.Button(add_frame, text="➕ Ajouter ligne", 
                  command=self.ajouter_ligne).grid(row=1, column=4, padx=10, pady=(5, 0))
        
        # TreeView des lignes
        columns = ('compte', 'libelle', 'debit', 'credit')
        self.tree_lignes = ttk.Treeview(lignes_frame, columns=columns, show='headings', height=12)
        
        self.tree_lignes.heading('compte', text='Compte')
        self.tree_lignes.heading('libelle', text='Libellé')
        self.tree_lignes.heading('debit', text='Débit')
        self.tree_lignes.heading('credit', text='Crédit')
        
        self.tree_lignes.column('compte', width=150)
        self.tree_lignes.column('libelle', width=350)
        self.tree_lignes.column('debit', width=120, anchor=tk.E)
        self.tree_lignes.column('credit', width=120, anchor=tk.E)
        
        self.tree_lignes.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(lignes_frame, orient=tk.VERTICAL, command=self.tree_lignes.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree_lignes.configure(yscrollcommand=scrollbar.set)
        
        # Bouton supprimer ligne
        ttk.Button(lignes_frame, text="🗑️ Supprimer ligne sélectionnée", 
                  command=self.supprimer_ligne).grid(row=2, column=0, pady=5)
        
        # Totaux
        totaux_frame = ttk.Frame(lignes_frame)
        totaux_frame.grid(row=3, column=0, pady=10)
        
        self.lbl_total_debit = ttk.Label(totaux_frame, text="Total Débit: 0.00", 
                                         font=('Arial', 10, 'bold'))
        self.lbl_total_debit.grid(row=0, column=0, padx=20)
        
        self.lbl_total_credit = ttk.Label(totaux_frame, text="Total Crédit: 0.00", 
                                          font=('Arial', 10, 'bold'))
        self.lbl_total_credit.grid(row=0, column=1, padx=20)
        
        self.lbl_equilibre = ttk.Label(totaux_frame, text="❌ Déséquilibrée", 
                                       font=('Arial', 11, 'bold'), foreground='red')
        self.lbl_equilibre.grid(row=0, column=2, padx=20)
        
        lignes_frame.columnconfigure(0, weight=1)
        lignes_frame.rowconfigure(1, weight=1)
        
        # Boutons de validation
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, pady=20)
        
        ttk.Button(btn_frame, text="✅ Valider l'écriture", 
                  command=self.valider, width=20).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", 
                  command=self.window.destroy, width=20).grid(row=0, column=1, padx=5)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
    
    def load_data(self):
        """Charge les données (journaux, comptes)"""
        # Journaux
        journaux = self.service.get_journaux(self.societe.id)
        self.journaux = {f"{j.code} - {j.libelle}": j for j in journaux}
        self.cmb_journal['values'] = list(self.journaux.keys())
        if self.journaux:
            self.cmb_journal.set(list(self.journaux.keys())[0])
        
        # Comptes
        self.comptes_dict = {}
        comptes = self.service.get_comptes(self.societe.id)
        for c in comptes:
            key = f"{c.compte} - {c.intitule}"
            self.comptes_dict[key] = c
    
    def search_compte(self, event=None):
        """Recherche de comptes pendant la saisie"""
        search_term = self.cmb_compte.get()
        if len(search_term) < 2:
            return
        
        # Filtrer les comptes
        matching = [key for key in self.comptes_dict.keys() 
                   if search_term.upper() in key.upper()]
        self.cmb_compte['values'] = matching[:50]  # Limiter à 50 résultats
    
    def ajouter_ligne(self):
        """Ajoute une ligne à l'écriture"""
        # Validation
        if not self.cmb_compte.get() or self.cmb_compte.get() not in self.comptes_dict:
            messagebox.showwarning("Attention", "Veuillez sélectionner un compte valide")
            return
        
        try:
            debit = Decimal(self.entry_debit.get() or '0')
            credit = Decimal(self.entry_credit.get() or '0')
            
            if debit == 0 and credit == 0:
                messagebox.showwarning("Attention", "Le débit ou le crédit doit être renseigné")
                return
            
            if debit > 0 and credit > 0:
                messagebox.showwarning("Attention", "Une ligne ne peut avoir qu'un débit OU un crédit")
                return
        except:
            messagebox.showwarning("Attention", "Montants invalides")
            return
        
        # Récupérer le compte
        compte = self.comptes_dict[self.cmb_compte.get()]
        
        # Créer le mouvement
        mouvement = Mouvement(
            compte_id=compte.id,
            compte_numero=compte.compte,
            libelle=self.entry_ligne_libelle.get() or compte.intitule,
            debit=debit,
            credit=credit
        )
        
        self.mouvements.append(mouvement)
        
        # Ajouter à la TreeView
        self.tree_lignes.insert('', tk.END, values=(
            f"{compte.compte} - {compte.intitule}",
            mouvement.libelle,
            f"{debit:.2f}" if debit > 0 else "",
            f"{credit:.2f}" if credit > 0 else ""
        ))
        
        # Réinitialiser les champs
        self.entry_ligne_libelle.delete(0, tk.END)
        self.entry_debit.delete(0, tk.END)
        self.entry_credit.delete(0, tk.END)
        self.cmb_compte.set('')
        
        # Mettre à jour les totaux
        self.update_totaux()
    
    def supprimer_ligne(self):
        """Supprime la ligne sélectionnée"""
        selection = self.tree_lignes.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une ligne")
            return
        
        # Récupérer l'index
        index = self.tree_lignes.index(selection[0])
        
        # Supprimer de la liste et du tree
        del self.mouvements[index]
        self.tree_lignes.delete(selection[0])
        
        # Mettre à jour les totaux
        self.update_totaux()
    
    def update_totaux(self):
        """Met à jour les totaux"""
        total_debit = sum(m.debit for m in self.mouvements)
        total_credit = sum(m.credit for m in self.mouvements)
        
        self.lbl_total_debit.config(text=f"Total Débit: {total_debit:.2f}")
        self.lbl_total_credit.config(text=f"Total Crédit: {total_credit:.2f}")
        
        # Vérifier l'équilibre
        if abs(total_debit - total_credit) < Decimal('0.01'):
            self.lbl_equilibre.config(text="✅ Équilibrée", foreground='green')
        else:
            ecart = total_debit - total_credit
            self.lbl_equilibre.config(
                text=f"❌ Déséquilibrée (écart: {ecart:.2f})", 
                foreground='red'
            )
    
    def valider(self):
        """Valide et enregistre l'écriture"""
        # Validations
        if not self.cmb_journal.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un journal")
            return
        
        if len(self.mouvements) < 2:
            messagebox.showwarning("Attention", "Une écriture doit avoir au moins 2 lignes")
            return
        
        total_debit = sum(m.debit for m in self.mouvements)
        total_credit = sum(m.credit for m in self.mouvements)
        
        if abs(total_debit - total_credit) >= Decimal('0.01'):
            messagebox.showerror("Erreur", "L'écriture n'est pas équilibrée")
            return
        
        # Créer l'écriture
        journal = self.journaux[self.cmb_journal.get()]
        
        try:
            date_ecriture = date.fromisoformat(self.entry_date.get())
        except:
            messagebox.showwarning("Attention", "Date invalide (format: YYYY-MM-DD)")
            return
        
        ecriture = Ecriture(
            societe_id=self.societe.id,
            exercice_id=self.exercice.id,
            journal_id=journal.id,
            numero="",  # Sera généré automatiquement
            date_ecriture=date_ecriture,
            reference_piece=self.entry_reference.get(),
            libelle=self.entry_libelle.get(),
            validee=True,
            date_validation=date_ecriture,
            mouvements=self.mouvements
        )
        
        # Enregistrer
        success, message, ecriture_id = self.service.create_ecriture(ecriture)
        
        if success:
            messagebox.showinfo("Succès", message)
            if self.callback:
                self.callback()
            self.window.destroy()
        else:
            messagebox.showerror("Erreur", message)
