"""
StatusBar - Barre de statut réutilisable
"""
import tkinter as tk
from tkinter import ttk


class StatusBar:
    """Barre de statut pour afficher les informations de session"""

    def __init__(self, parent):
        """
        Initialise la barre de statut

        Args:
            parent: Widget parent
        """
        self.frame = ttk.Frame(parent, relief=tk.SUNKEN)
        # Note: Le parent doit appeler grid() ou pack() sur ce frame
        # Ne pas appeler pack() ici pour permettre au parent de choisir le layout manager

        # Labels de statut
        self.label_societe = ttk.Label(
            self.frame,
            text="Société: Non chargée",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label_societe.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)

        self.label_exercice = ttk.Label(
            self.frame,
            text="Exercice: Non sélectionné",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label_exercice.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)

        self.label_status = ttk.Label(
            self.frame,
            text="Prêt",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)

    def update_societe(self, societe_nom: str):
        """Met à jour le nom de la société affichée"""
        self.label_societe.config(text=f"Société: {societe_nom}")

    def update_exercice(self, exercice_annee: int, cloture: bool = False):
        """Met à jour l'exercice affiché"""
        statut = "🔒 Clôturé" if cloture else "✅ Ouvert"
        self.label_exercice.config(text=f"Exercice: {exercice_annee} {statut}")

    def update_status(self, message: str):
        """Met à jour le message de statut"""
        self.label_status.config(text=message)

    def clear(self):
        """Réinitialise la barre de statut"""
        self.label_societe.config(text="Société: Non chargée")
        self.label_exercice.config(text="Exercice: Non sélectionné")
        self.label_status.config(text="Prêt")
