"""Script pour corriger rapidement les tests"""
import re

# Lire le fichier test_services.py
with open('tests/test_services.py', 'r') as f:
    content = f.read()

# Correction 1: get_tiers avec type_tiers optionnel
content = re.sub(
    r'mock_tiers_dao\.get_all\.assert_called_once_with\(1\)',
    'mock_tiers_dao.get_all.assert_called_once_with(1, None)',
    content
)

# Correction 2: get_mouvements_a_lettrer avec 4 paramètres
content = re.sub(
    r'comptabilite_service\.get_mouvements_a_lettrer\((\d+),\s*(\d+),\s*(["\'][\d]+["\'])\)',
    r'comptabilite_service.get_mouvements_a_lettrer(\1, \2, \3, None)',
    content
)

content = re.sub(
    r'mock_ecriture_dao\.get_mouvements_a_lettrer\.assert_called_once_with\((\d+),\s*(\d+),\s*(["\'][\d]+["\'])\)',
    r'mock_ecriture_dao.get_mouvements_a_lettrer.assert_called_once_with(\1, \2, \3, None)',
    content
)

# Sauvegarder
with open('tests/test_services.py', 'w') as f:
    f.write(content)

print("✅ Corrections appliquées à test_services.py")
