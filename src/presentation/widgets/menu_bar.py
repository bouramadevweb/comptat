"""
MenuBar - Barre de menu réutilisable
Extrait de gui_main.py pour améliorer la maintenabilité
"""
import tkinter as tk
from typing import Dict, Callable


class MenuBar:
    """Barre de menu de l'application"""

    def __init__(self, parent, callbacks: Dict[str, Callable]):
        """
        Initialise la barre de menu

        Args:
            parent: Widget parent (root)
            callbacks: Dictionnaire des callbacks pour chaque action menu
        """
        self.parent = parent
        self.callbacks = callbacks
        self.menubar = tk.Menu(parent)
        self._create_menus()

    def _create_menus(self):
        """Crée tous les menus"""
        self._create_file_menu()
        self._create_compta_menu()
        self._create_rapports_menu()
        self._create_cloture_menu()
        self._create_gestion_menu()
        self._create_aide_menu()

    def _create_file_menu(self):
        """Menu Fichier"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Fichier", menu=file_menu)

        file_menu.add_command(
            label="📊 Tableau de Bord",
            command=self.callbacks.get('afficher_dashboard', self._not_implemented)
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="📥 Importer CSV",
            command=self.callbacks.get('import_csv', self._not_implemented)
        )
        file_menu.add_command(
            label="Exporter FEC",
            command=self.callbacks.get('exporter_fec', self._not_implemented)
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quitter",
            command=self.callbacks.get('quit_app', self._not_implemented)
        )

    def _create_compta_menu(self):
        """Menu Comptabilité"""
        compta_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Comptabilité", menu=compta_menu)

        compta_menu.add_command(
            label="Nouvelle écriture",
            command=self.callbacks.get('nouvelle_ecriture', self._not_implemented)
        )
        compta_menu.add_command(
            label="Saisie Vente",
            command=self.callbacks.get('saisie_vente', self._not_implemented)
        )
        compta_menu.add_command(
            label="Saisie Achat",
            command=self.callbacks.get('saisie_achat', self._not_implemented)
        )
        compta_menu.add_separator()
        compta_menu.add_command(
            label="🔗 Lettrage",
            command=self.callbacks.get('ouvrir_lettrage', self._not_implemented)
        )
        compta_menu.add_separator()
        compta_menu.add_command(
            label="Calculer Balance",
            command=self.callbacks.get('calculer_balance', self._not_implemented)
        )

    def _create_rapports_menu(self):
        """Menu Rapports"""
        rapports_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Rapports", menu=rapports_menu)

        rapports_menu.add_command(
            label="Balance",
            command=self.callbacks.get('afficher_balance', self._not_implemented)
        )
        rapports_menu.add_command(
            label="📚 Grand Livre",
            command=self.callbacks.get('afficher_grand_livre', self._not_implemented)
        )
        rapports_menu.add_separator()
        rapports_menu.add_command(
            label="Compte de résultat",
            command=self.callbacks.get('afficher_resultat', self._not_implemented)
        )
        rapports_menu.add_command(
            label="Bilan",
            command=self.callbacks.get('afficher_bilan', self._not_implemented)
        )
        rapports_menu.add_command(
            label="TVA",
            command=self.callbacks.get('afficher_tva', self._not_implemented)
        )

    def _create_cloture_menu(self):
        """Menu Clôture"""
        cloture_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Clôture", menu=cloture_menu)

        cloture_menu.add_command(
            label="Tester comptabilité",
            command=self.callbacks.get('tester_comptabilite', self._not_implemented)
        )
        cloture_menu.add_command(
            label="Clôturer exercice",
            command=self.callbacks.get('cloturer_exercice', self._not_implemented)
        )

    def _create_gestion_menu(self):
        """Menu Gestion"""
        gestion_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Gestion", menu=gestion_menu)

        gestion_menu.add_command(
            label="👥 Gestion des Tiers",
            command=self.callbacks.get('gestion_tiers', self._not_implemented)
        )

    def _create_aide_menu(self):
        """Menu Aide"""
        aide_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Aide", menu=aide_menu)

        aide_menu.add_command(
            label="À propos",
            command=self.callbacks.get('about', self._not_implemented)
        )

    def _not_implemented(self):
        """Placeholder pour les callbacks non implémentés"""
        from tkinter import messagebox
        messagebox.showinfo("Info", "Fonctionnalité non implémentée")

    def get_menubar(self):
        """Retourne la barre de menu"""
        return self.menubar

    def attach_to(self, window):
        """Attache la barre de menu à une fenêtre"""
        window.config(menu=self.menubar)
