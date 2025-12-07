"""
Interface graphique pour l'import de données CSV
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImportCSVWindow:
    """Fenêtre d'import CSV pour les écritures"""

    def __init__(self, parent, service, societe, exercice):
        self.service = service
        self.societe = societe
        self.exercice = exercice
        self.file_path = None

        self.window = tk.Toplevel(parent)
        self.window.title("📥 Import CSV - Écritures")
        self.window.geometry("800x600")
        self.window.transient(parent)

        self.create_widgets()

    def create_widgets(self):
        """Crée l'interface"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titre
        ttk.Label(main_frame, text="📥 IMPORT D'ÉCRITURES (CSV)",
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="📋 Instructions", padding="10")
        instructions_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        instructions_text = """
Format CSV attendu (séparateur: virgule, encodage: UTF-8):

Colonnes obligatoires:
  • date          : Date de l'écriture (format: YYYY-MM-DD, ex: 2025-01-15)
  • journal       : Code du journal (VE, AC, BQ, OD)
  • numero_piece  : Numéro de la pièce justificative
  • libelle       : Libellé de l'écriture
  • compte        : Numéro du compte (ex: 411000)
  • debit         : Montant au débit (0 si aucun)
  • credit        : Montant au crédit (0 si aucun)

Colonnes optionnelles:
  • tiers         : Code du tiers (ex: CLT0001)

Note: Les lignes avec la même date + même numéro de pièce seront groupées en une seule écriture.
        """

        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT, foreground="#555").pack()

        # Sélection fichier
        file_frame = ttk.LabelFrame(main_frame, text="1. Sélectionner le fichier CSV", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.lbl_file = ttk.Label(file_frame, text="Aucun fichier sélectionné", foreground="red")
        self.lbl_file.pack(side=tk.LEFT, padx=5)

        ttk.Button(file_frame, text="📁 Parcourir...", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="✨ Créer un exemple", command=self.create_example).pack(side=tk.LEFT, padx=5)

        # Aperçu
        preview_frame = ttk.LabelFrame(main_frame, text="2. Aperçu et validation", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        self.text_preview = tk.Text(preview_frame, height=15, width=80, font=('Courier', 9))
        self.text_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.text_preview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_preview.configure(yscrollcommand=scrollbar.set)

        # Boutons d'action
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="✅ Valider le fichier", command=self.validate_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📥 Importer", command=self.import_file, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Fermer", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        # Configuration redimensionnement
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def select_file(self):
        """Sélectionne un fichier CSV"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )

        if file_path:
            self.file_path = file_path
            self.lbl_file.config(text=Path(file_path).name, foreground="green")
            self.load_preview()

    def load_preview(self):
        """Charge un aperçu du fichier"""
        if not self.file_path:
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # Premiers 2000 caractères

            self.text_preview.delete('1.0', tk.END)
            self.text_preview.insert('1.0', content)

            if len(content) == 2000:
                self.text_preview.insert(tk.END, "\n\n... (fichier tronqué pour l'aperçu)")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le fichier:\n{e}")

    def validate_file(self):
        """Valide le fichier CSV"""
        if not self.file_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier")
            return

        try:
            from src.utils.import_utils import EcritureCSVImporter

            importer = EcritureCSVImporter(self.file_path)
            is_valid, message = importer.validate()

            if is_valid:
                messagebox.showinfo("Validation", message)
            else:
                messagebox.showerror("Erreur de validation", message)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la validation:\n{e}")

    def import_file(self):
        """Importe le fichier CSV"""
        if not self.file_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier")
            return

        # Confirmation
        if not messagebox.askyesno("Confirmation",
                                  "Importer les écritures dans la base de données ?\n\n"
                                  "Cette action est irréversible."):
            return

        try:
            from src.utils.import_utils import EcritureCSVImporter

            importer = EcritureCSVImporter(self.file_path)

            # Import
            self.window.config(cursor="wait")
            self.window.update()

            nb_success, nb_errors, errors = importer.import_ecritures(
                self.service,
                self.societe.id,
                self.exercice.id
            )

            self.window.config(cursor="")

            # Résultat
            message = f"Import terminé:\n\n"
            message += f"✅ Écritures créées: {nb_success}\n"
            message += f"❌ Erreurs: {nb_errors}\n"

            if errors:
                message += f"\nDétails des erreurs:\n"
                message += "\n".join(errors[:10])  # Max 10 erreurs affichées

                if len(errors) > 10:
                    message += f"\n... et {len(errors) - 10} autres erreurs"

            if nb_errors > 0:
                messagebox.showwarning("Import terminé avec erreurs", message)
            else:
                messagebox.showinfo("Succès", message)

                # Recalculer la balance
                self.service.calculer_balance(self.societe.id, self.exercice.id)

        except Exception as e:
            self.window.config(cursor="")
            messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{e}")
            logger.error(f"❌ Erreur import CSV: {e}", exc_info=True)

    def create_example(self):
        """Crée un fichier CSV exemple"""
        file_path = filedialog.asksaveasfilename(
            title="Enregistrer le fichier exemple",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile="exemple_import_ecritures.csv"
        )

        if file_path:
            try:
                from src.utils.import_utils import create_sample_csv
                create_sample_csv(file_path)
                messagebox.showinfo("Succès", f"Fichier exemple créé:\n{file_path}\n\n"
                                             f"Vous pouvez l'ouvrir avec Excel ou LibreOffice.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer le fichier:\n{e}")
