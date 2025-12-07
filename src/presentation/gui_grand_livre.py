"""
Fenêtre du Grand Livre (consultation détaillée par compte)
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from decimal import Decimal
from datetime import datetime


class GrandLivreWindow:
    """Fenêtre d'affichage du Grand Livre"""

    def __init__(self, parent, service, societe, exercice):
        self.service = service
        self.societe = societe
        self.exercice = exercice
        self.compte_selectionne = None

        self.window = tk.Toplevel(parent)
        self.window.title(f"Grand Livre - {exercice.annee}")
        self.window.geometry("1400x800")
        self.window.transient(parent)

        self.create_widgets()
        self.load_comptes()

    def create_widgets(self):
        """Crée les widgets"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titre
        ttk.Label(main_frame, text=f"📚 GRAND LIVRE - {self.exercice.annee}",
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 15))

        # Frame sélection compte
        select_frame = ttk.LabelFrame(main_frame, text="Sélection du compte", padding="10")
        select_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(select_frame, text="Compte:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.cmb_compte = ttk.Combobox(select_frame, width=60, state='readonly')
        self.cmb_compte.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        ttk.Button(select_frame, text="📋 Afficher",
                  command=self.afficher_compte).grid(row=0, column=2, padx=5)
        ttk.Button(select_frame, text="💾 Exporter",
                  command=self.exporter).grid(row=0, column=3, padx=5)

        select_frame.columnconfigure(1, weight=1)

        # Informations compte
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.lbl_compte_info = ttk.Label(info_frame, text="", font=('Arial', 10, 'bold'))
        self.lbl_compte_info.pack(side=tk.LEFT)

        self.lbl_solde = ttk.Label(info_frame, text="", font=('Arial', 10, 'bold'))
        self.lbl_solde.pack(side=tk.RIGHT)

        # TreeView mouvements
        columns = ('date', 'journal', 'compte', 'ecriture', 'reference', 'libelle',
                  'debit', 'credit', 'solde', 'lettrage')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=30)

        self.tree.heading('date', text='Date')
        self.tree.heading('journal', text='Journal')
        self.tree.heading('compte', text='Compte')
        self.tree.heading('ecriture', text='N° Écriture')
        self.tree.heading('reference', text='Référence')
        self.tree.heading('libelle', text='Libellé')
        self.tree.heading('debit', text='Débit')
        self.tree.heading('credit', text='Crédit')
        self.tree.heading('solde', text='Solde')
        self.tree.heading('lettrage', text='Let.')

        self.tree.column('date', width=100)
        self.tree.column('journal', width=80)
        self.tree.column('compte', width=100)
        self.tree.column('ecriture', width=100)
        self.tree.column('reference', width=120)
        self.tree.column('libelle', width=350)
        self.tree.column('debit', width=120, anchor=tk.E)
        self.tree.column('credit', width=120, anchor=tk.E)
        self.tree.column('solde', width=120, anchor=tk.E)
        self.tree.column('lettrage', width=60, anchor=tk.CENTER)

        self.tree.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.grid(row=3, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_x.grid(row=4, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        # Totaux
        totaux_frame = ttk.Frame(main_frame)
        totaux_frame.grid(row=5, column=0, pady=10)

        self.lbl_totaux = ttk.Label(totaux_frame, text="", font=('Arial', 10, 'bold'))
        self.lbl_totaux.pack()

        # Configuration redimensionnement
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def load_comptes(self):
        """Charge la liste des comptes"""
        try:
            comptes = self.service.get_comptes(self.societe.id)
            values = ["Tous les comptes"] + [f"{c.compte} - {c.intitule}" for c in comptes]
            self.cmb_compte['values'] = values

            if values:
                self.cmb_compte.set(values[0])

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des comptes: {e}")

    def afficher_compte(self):
        """Affiche les mouvements du compte sélectionné"""
        selection = self.cmb_compte.get()
        if not selection:
            return

        # Extraire le numéro de compte (ou None pour tous)
        if selection == "Tous les comptes":
            compte_numero = None
            compte_intitule = "Tous les comptes"
            self.compte_selectionne = "ALL"
        else:
            compte_numero = selection.split(' - ')[0]
            compte_intitule = ' - '.join(selection.split(' - ')[1:])
            self.compte_selectionne = compte_numero

        # Effacer les anciennes données
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Requête grand livre (filtrée si compte_numero fourni)
            query = """
                SELECT
                    e.date_ecriture,
                    j.code as journal_code,
                    e.numero as ecriture_numero,
                    e.reference_piece,
                    m.libelle,
                    m.debit,
                    m.credit,
                    m.lettrage_code,
                    c.compte
                FROM MOUVEMENTS m
                JOIN ECRITURES e ON e.id = m.ecriture_id
                JOIN JOURNAUX j ON j.id = e.journal_id
                JOIN COMPTES c ON c.id = m.compte_id
                WHERE e.societe_id = %s
                AND e.exercice_id = %s
                AND e.validee = 1
            """
            params = [self.societe.id, self.exercice.id]
            if compte_numero:
                query += " AND c.compte = %s"
                params.append(compte_numero)
            query += " ORDER BY c.compte, e.date_ecriture, e.numero, m.id"

            mouvements = self.service.db.execute_query(query, tuple(params))

            # Calculer le solde progressif
            solde_par_compte = {}
            total_debit = Decimal('0')
            total_credit = Decimal('0')

            for mvt in mouvements:
                debit = Decimal(str(mvt['debit']))
                credit = Decimal(str(mvt['credit']))

                total_debit += debit
                total_credit += credit
                compte_courant = mvt['compte']
                solde_par_compte.setdefault(compte_courant, Decimal('0'))
                solde_par_compte[compte_courant] += debit - credit
                solde_courant = solde_par_compte[compte_courant]

                lettrage = mvt['lettrage_code'] if mvt['lettrage_code'] else ''

                self.tree.insert('', tk.END, values=(
                    mvt['date_ecriture'],
                    mvt['journal_code'],
                    compte_courant,
                    mvt['ecriture_numero'],
                    mvt['reference_piece'] or '',
                    mvt['libelle'],
                    f"{debit:.2f}",
                    f"{credit:.2f}",
                    f"{solde_courant:.2f}",
                    lettrage
                ))

            # Afficher les informations
            self.lbl_compte_info.config(
                text=f"{compte_intitule} | {len(mouvements)} mouvements"
            )

            # Couleur du solde
            if compte_numero:
                solde_global = solde_par_compte.get(compte_numero, Decimal('0'))
            else:
                solde_global = sum(solde_par_compte.values())

            if solde_global > 0:
                solde_text = f"Solde: {solde_global:.2f} € (Débiteur)"
                color = 'blue'
            elif solde_global < 0:
                solde_text = f"Solde: {abs(solde_global):.2f} € (Créditeur)"
                color = 'red'
            else:
                solde_text = f"Solde: {solde_global:.2f} € (Soldé)"
                color = 'green'

            self.lbl_solde.config(text=solde_text, foreground=color)

            self.lbl_totaux.config(
                text=f"TOTAUX : Débit = {total_debit:.2f} € | Crédit = {total_credit:.2f} € | Solde = {solde_global:.2f} €"
            )

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")
            import traceback
            traceback.print_exc()

    def exporter(self):
        """Exporte le grand livre en CSV"""
        if not self.compte_selectionne:
            messagebox.showwarning("Attention", "Affichez d'abord un compte")
            return

        # Demander le nom de fichier
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            initialfile=f"grand_livre_{self.compte_selectionne}_{self.exercice.annee}.csv"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # En-tête
                f.write(f"Grand Livre - Compte {self.compte_selectionne}\n")
                f.write(f"Exercice {self.exercice.annee}\n")
                f.write(f"Édité le {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("\n")

                # Colonnes
                f.write("Date;Journal;Écriture;Référence;Libellé;Débit;Crédit;Solde;Lettrage\n")

                # Données
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    f.write(";".join(str(v) for v in values) + "\n")

            messagebox.showinfo("Succès", f"✅ Export réussi\n{filename}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
