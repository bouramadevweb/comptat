#!/usr/bin/env python3
"""
Script simple pour créer une société et un exercice
Mode non-interactif
"""

import sys
from datetime import date
from src.infrastructure.factories import create_db_manager
from scripts.init_societe import InitialisationSociete

def main():
    """Crée une société avec valeurs par défaut"""

    # Paramètres par défaut
    nom_societe = sys.argv[1] if len(sys.argv) > 1 else "Ma Société"
    siren = sys.argv[2] if len(sys.argv) > 2 else "999999999"
    annee = int(sys.argv[3]) if len(sys.argv) > 3 else date.today().year

    print("\n" + "="*70)
    print(f"   CRÉATION SOCIÉTÉ : {nom_societe}")
    print("="*70)

    try:
        # Créer le gestionnaire de base
        db = create_db_manager()

        # Créer l'initialisateur
        init = InitialisationSociete(db)

        # Créer la société (mode permissif pour éviter les erreurs de validation)
        societe_id, exercice_id, message = init.creer_societe_complete(
            nom_societe=nom_societe,
            siren=siren,
            adresse="1 Rue Exemple",
            code_postal="75001",
            ville="Paris",
            annee_exercice=annee,
            mode_strict=False  # Mode permissif
        )

        print(f"\n{message}")

        db.disconnect()

        return 0

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
