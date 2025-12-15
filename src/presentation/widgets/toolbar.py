"""
ToolBar - Barre d'outils réutilisable avec boutons rapides
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable


class ToolBar:
    """Barre d'outils avec raccourcis"""

    def __init__(self, parent, callbacks: Dict[str, Callable]):
        """
        Initialise la barre d'outils

        Args:
            parent: Widget parent
            callbacks: Dictionnaire des callbacks pour chaque bouton
        """
        self.parent = parent
        self.callbacks = callbacks

        # Frame principale
        self.frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        # Note: Le parent doit appeler grid() ou pack() sur ce frame
        # Ne pas appeler pack() ici pour permettre au parent de choisir le layout manager

        self._create_buttons()

    def _create_buttons(self):
        """Crée les boutons de la toolbar"""

        # Bouton Nouvelle écriture
        btn_new = ttk.Button(
            self.frame,
            text="✏️ Nouvelle Écriture",
            command=self.callbacks.get('nouvelle_ecriture', lambda: None)
        )
        btn_new.pack(side=tk.LEFT, padx=2, pady=2)

        # Bouton Vente
        btn_vente = ttk.Button(
            self.frame,
            text="💰 Vente",
            command=self.callbacks.get('saisie_vente', lambda: None)
        )
        btn_vente.pack(side=tk.LEFT, padx=2, pady=2)

        # Bouton Achat
        btn_achat = ttk.Button(
            self.frame,
            text="🛒 Achat",
            command=self.callbacks.get('saisie_achat', lambda: None)
        )
        btn_achat.pack(side=tk.LEFT, padx=2, pady=2)

        # Séparateur
        ttk.Separator(self.frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5, pady=2
        )

        # Bouton Balance
        btn_balance = ttk.Button(
            self.frame,
            text="📊 Balance",
            command=self.callbacks.get('afficher_balance', lambda: None)
        )
        btn_balance.pack(side=tk.LEFT, padx=2, pady=2)

        # Bouton Grand Livre
        btn_grand_livre = ttk.Button(
            self.frame,
            text="📚 Grand Livre",
            command=self.callbacks.get('afficher_grand_livre', lambda: None)
        )
        btn_grand_livre.pack(side=tk.LEFT, padx=2, pady=2)

        # Séparateur
        ttk.Separator(self.frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5, pady=2
        )

        # Bouton Lettrage
        btn_lettrage = ttk.Button(
            self.frame,
            text="🔗 Lettrage",
            command=self.callbacks.get('ouvrir_lettrage', lambda: None)
        )
        btn_lettrage.pack(side=tk.LEFT, padx=2, pady=2)

        # Bouton Tiers
        btn_tiers = ttk.Button(
            self.frame,
            text="👥 Tiers",
            command=self.callbacks.get('gestion_tiers', lambda: None)
        )
        btn_tiers.pack(side=tk.LEFT, padx=2, pady=2)

    def enable(self):
        """Active tous les boutons"""
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=tk.NORMAL)

    def disable(self):
        """Désactive tous les boutons"""
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=tk.DISABLED)
