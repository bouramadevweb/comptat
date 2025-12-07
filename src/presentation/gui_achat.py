"""
Fenêtre de saisie d'achat
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal
from typing import Callable


class AchatWindow:
    """Fenêtre de saisie simplifiée d'achat"""
    
    def __init__(self, parent, service, societe, exercice, callback: Callable = None):
        self.service = service
        self.societe = societe
        self.exercice = exercice
        self.callback = callback
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("Saisie d'Achat")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Crée les widgets"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # En-tête
        ttk.Label(main_frame, text="🛒 SAISIE D'ACHAT", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Formulaire
        row = 1
        
        # Journal
        ttk.Label(main_frame, text="Journal:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cmb_journal = ttk.Combobox(main_frame, state='readonly', width=40)
        self.cmb_journal.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Date
        ttk.Label(main_frame, text="Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_date = ttk.Entry(main_frame, width=42)
        self.entry_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Fournisseur
        ttk.Label(main_frame, text="Fournisseur:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cmb_fournisseur = ttk.Combobox(main_frame, state='readonly', width=40)
        self.cmb_fournisseur.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Référence
        ttk.Label(main_frame, text="Référence (facture):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_reference = ttk.Entry(main_frame, width=42)
        self.entry_reference.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Libellé
        ttk.Label(main_frame, text="Libellé:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_libelle = ttk.Entry(main_frame, width=42)
        self.entry_libelle.insert(0, "Achat de marchandises")
        self.entry_libelle.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Montant HT
        ttk.Label(main_frame, text="Montant HT (€):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_montant_ht = ttk.Entry(main_frame, width=42)
        self.entry_montant_ht.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.entry_montant_ht.bind('<KeyRelease>', self.calculer_montants)
        row += 1
        
        # Taux TVA
        ttk.Label(main_frame, text="Taux TVA (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cmb_tva = ttk.Combobox(main_frame, values=['20', '10', '5.5', '2.1', '0'], 
                                     state='readonly', width=40)
        self.cmb_tva.set('20')
        self.cmb_tva.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.cmb_tva.bind('<<ComboboxSelected>>', self.calculer_montants)
        row += 1
        
        # Montant TVA (calculé)
        ttk.Label(main_frame, text="Montant TVA (€):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.lbl_tva = ttk.Label(main_frame, text="0.00", font=('Arial', 10, 'bold'))
        self.lbl_tva.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Montant TTC (calculé)
        ttk.Label(main_frame, text="Montant TTC (€):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.lbl_ttc = ttk.Label(main_frame, text="0.00", 
                                font=('Arial', 12, 'bold'), foreground='blue')
        self.lbl_ttc.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Séparateur
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        row += 1
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="✅ Valider", 
                  command=self.valider, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", 
                  command=self.window.destroy, width=15).grid(row=0, column=1, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def load_data(self):
        """Charge les données (journaux, fournisseurs)"""
        try:
            journaux = self.service.get_journaux(self.societe.id)
            journaux_achat = [j for j in journaux if getattr(j, 'type', '').upper() == 'ACHAT']
            journaux_source = journaux_achat if journaux_achat else journaux

            if journaux_source:
                self.journaux = {f"{j.code} - {j.libelle}": j for j in journaux_source}
                self.cmb_journal['values'] = list(self.journaux.keys())
                self.cmb_journal.set(list(self.journaux.keys())[0])
            else:
                messagebox.showwarning("Attention", "Aucun journal disponible pour les achats.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les journaux: {e}")
            self.journaux = {}

        # Charger les fournisseurs
        try:
            fournisseurs = self.service.get_tiers(self.societe.id, 'FOURNISSEUR')
            if fournisseurs:
                self.fournisseurs = {f"{f.code_aux} - {f.nom}": f for f in fournisseurs}
                self.cmb_fournisseur['values'] = list(self.fournisseurs.keys())
                self.cmb_fournisseur.set(list(self.fournisseurs.keys())[0])
            else:
                messagebox.showwarning("Attention", "Aucun fournisseur disponible.")
                self.fournisseurs = {}
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les fournisseurs: {e}")
            self.fournisseurs = {}
    
    def calculer_montants(self, event=None):
        """Calcule les montants TVA et TTC"""
        try:
            montant_ht = Decimal(self.entry_montant_ht.get() or '0')
            taux_tva = Decimal(self.cmb_tva.get() or '0') / Decimal('100')
            
            montant_tva = montant_ht * taux_tva
            montant_ttc = montant_ht + montant_tva
            
            self.lbl_tva.config(text=f"{montant_tva:.2f}")
            self.lbl_ttc.config(text=f"{montant_ttc:.2f}")
        except:
            self.lbl_tva.config(text="0.00")
            self.lbl_ttc.config(text="0.00")
    
    def valider(self):
        """Valide et enregistre l'achat"""
        # Validation des champs
        if not self.cmb_journal.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un journal")
            return
        
        if not self.cmb_fournisseur.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner un fournisseur")
            return
        
        if not self.entry_reference.get():
            messagebox.showwarning("Attention", "Veuillez saisir une référence")
            return
        
        try:
            montant_ht = Decimal(self.entry_montant_ht.get())
            if montant_ht <= 0:
                raise ValueError("Montant invalide")
        except:
            messagebox.showwarning("Attention", "Montant HT invalide")
            return
        
        # Récupérer les données
        journal = self.journaux.get(self.cmb_journal.get())
        fournisseur = self.fournisseurs.get(self.cmb_fournisseur.get())
        if not journal or not fournisseur:
            messagebox.showwarning("Attention", "Sélection invalide (journal ou fournisseur).")
            return
        taux_tva = Decimal(self.cmb_tva.get()) / Decimal('100')
        try:
            date_achat = date.fromisoformat(self.entry_date.get())
        except ValueError:
            messagebox.showwarning("Attention", "Format de date invalide (YYYY-MM-DD).")
            return
        
        # Créer l'écriture d'achat
        success, message, ecriture_id = self.service.creer_ecriture_achat(
            societe_id=self.societe.id,
            exercice_id=self.exercice.id,
            journal_id=journal.id,
            date_ecriture=date_achat,
            fournisseur_id=fournisseur.id,
            montant_ht=montant_ht,
            taux_tva=taux_tva,
            reference=self.entry_reference.get(),
            libelle=self.entry_libelle.get()
        )
        
        if success:
            messagebox.showinfo("Succès", message)
            if self.callback:
                self.callback()
            self.window.destroy()
        else:
            hint = ""
            if "Comptes manquants" in message:
                hint = (
                    "\n\nVérifiez que les comptes suivants existent dans le plan comptable :\n"
                    " - 401000 (Fournisseurs)\n"
                    " - 606000 (Achats de fournitures ou compte d'achat utilisé)\n"
                    " - 44566x (TVA déductible, selon le taux)"
                )
            messagebox.showerror("Erreur", f"{message}{hint}")
