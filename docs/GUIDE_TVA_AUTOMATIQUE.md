# 📊 GUIDE : CALCUL AUTOMATIQUE DE LA TVA

## ✅ Confirmation : Votre système calcule automatiquement la TVA !

Votre application de comptabilité dispose d'un **calcul automatique de la TVA** dans les écritures de vente et d'achat.

---

## 🎯 Fonctionnalités de Calcul Automatique

### 1. **Saisie de Vente** 📝

Lorsque vous ouvrez `Comptabilité → Saisie Vente` :

#### Ce que vous saisissez :
- ✏️ **Montant HT** (Hors Taxes)
- ✏️ **Taux de TVA** (20%, 10%, 5.5%, 2.1%, 0%)

#### Ce que le système calcule automatiquement :
- ✅ **Montant TVA** = HT × Taux TVA
- ✅ **Montant TTC** = HT + TVA

#### Exemple concret :
```
Vous saisissez :
  - Montant HT : 1000.00 €
  - Taux TVA : 20%

Le système calcule automatiquement :
  - Montant TVA : 200.00 € (affiché en temps réel)
  - Montant TTC : 1200.00 € (affiché en temps réel)
```

#### Écritures générées automatiquement :
```
Débit  411 (Client)         1200.00 €
Crédit 707 (Ventes)         1000.00 €
Crédit 4457 (TVA collectée)  200.00 €
```

---

### 2. **Saisie d'Achat** 🛒

Lorsque vous ouvrez `Comptabilité → Saisie Achat` :

#### Ce que vous saisissez :
- ✏️ **Montant HT** (Hors Taxes)
- ✏️ **Taux de TVA** (20%, 10%, 5.5%, 2.1%, 0%)

#### Ce que le système calcule automatiquement :
- ✅ **Montant TVA** = HT × Taux TVA
- ✅ **Montant TTC** = HT + TVA

#### Exemple concret :
```
Vous saisissez :
  - Montant HT : 800.00 €
  - Taux TVA : 20%

Le système calcule automatiquement :
  - Montant TVA : 160.00 € (affiché en temps réel)
  - Montant TTC : 960.00 € (affiché en temps réel)
```

#### Écritures générées automatiquement :
```
Débit  606 (Achats)           800.00 €
Débit  4456 (TVA déductible)  160.00 €
Crédit 401 (Fournisseur)      960.00 €
```

---

## 🔄 Calcul en Temps Réel

Le calcul de la TVA se fait **instantanément** :

### 1. **Pendant la saisie**
- Dès que vous tapez un montant HT, la TVA est calculée
- Dès que vous changez le taux, la TVA est recalculée

### 2. **Mise à jour automatique**
```python
# Le système écoute les événements :
self.entry_montant_ht.bind('<KeyRelease>', self.calculer_montants)
self.cmb_tva.bind('<<ComboboxSelected>>', self.calculer_montants)
```

---

## 📋 Taux de TVA Disponibles

| Taux | Usage Typique |
|------|---------------|
| **20%** | Taux normal (défaut) |
| **10%** | Taux réduit (restauration, transport) |
| **5.5%** | Taux réduit (livres, alimentation) |
| **2.1%** | Taux super réduit (médicaments) |
| **0%** | Hors TVA (exports, certains services) |

---

## ⚙️ Code Technique (Pour Information)

### Fonction de calcul dans gui_vente.py et gui_achat.py :

```python
def calculer_montants(self, event=None):
    """Calcule les montants TVA et TTC"""
    try:
        # Récupérer le montant HT
        montant_ht = Decimal(self.entry_montant_ht.get() or '0')
        
        # Récupérer le taux TVA (en décimal)
        taux_tva = Decimal(self.cmb_tva.get() or '0') / Decimal('100')
        
        # Calculer la TVA
        montant_tva = montant_ht * taux_tva
        
        # Calculer le TTC
        montant_ttc = montant_ht + montant_tva
        
        # Afficher les résultats
        self.lbl_tva.config(text=f"{montant_tva:.2f}")
        self.lbl_ttc.config(text=f"{montant_ttc:.2f}")
    except:
        self.lbl_tva.config(text="0.00")
        self.lbl_ttc.config(text="0.00")
```

---

## ✅ Avantages du Calcul Automatique

### 1. **Gain de temps**
- ⏱️ Pas besoin de calculer manuellement
- ⏱️ Pas besoin de calculatrice

### 2. **Zéro erreur de calcul**
- 🎯 Calculs précis (2 décimales)
- 🎯 Pas d'erreur d'arrondi
- 🎯 Cohérence garantie

### 3. **Validation en temps réel**
- 👁️ Vous voyez immédiatement le montant TTC
- 👁️ Vous pouvez vérifier avant de valider

### 4. **Conformité comptable**
- ✅ TVA collectée correctement enregistrée (compte 4457)
- ✅ TVA déductible correctement enregistrée (compte 4456)
- ✅ Prêt pour la déclaration de TVA

---

## 📊 Consultation de la TVA

Après avoir saisi vos écritures, consultez la TVA :

### Menu `Rapports → Déclaration TVA`

Affiche automatiquement :
- 💰 **TVA Collectée** (sur vos ventes)
- 💰 **TVA Déductible** (sur vos achats)
- 💰 **TVA à Payer** = Collectée - Déductible

---

## 🔍 Exemple Complet

### Scénario : Vente de 1000 € HT + Achat de 600 € HT

#### 1. Saisie Vente (1000 € HT, TVA 20%)
```
Vous tapez : 1000
Le système affiche automatiquement :
  - TVA : 200.00 €
  - TTC : 1200.00 €

Écriture générée :
  Débit  411 (Client)        1200.00 €
  Crédit 707 (Ventes)        1000.00 €
  Crédit 4457 (TVA coll.)     200.00 €
```

#### 2. Saisie Achat (600 € HT, TVA 20%)
```
Vous tapez : 600
Le système affiche automatiquement :
  - TVA : 120.00 €
  - TTC : 720.00 €

Écriture générée :
  Débit  606 (Achats)         600.00 €
  Débit  4456 (TVA déd.)      120.00 €
  Crédit 401 (Fournisseur)    720.00 €
```

#### 3. Déclaration TVA (Rapports → Déclaration TVA)
```
TVA Collectée :  200.00 €
TVA Déductible : 120.00 €
TVA à Payer :     80.00 €
```

---

## ⚠️ Important : Saisie Manuelle

### Pour les écritures manuelles (`Nouvelle écriture`) :
- ❌ La TVA n'est **PAS** calculée automatiquement
- ✏️ Vous devez saisir les lignes vous-même :
  - Compte de charge/produit (HT)
  - Compte de TVA (4456 ou 4457)
  - Compte de tiers (TTC)

### Recommandation :
👉 **Utilisez toujours "Saisie Vente" ou "Saisie Achat"** pour bénéficier du calcul automatique !

---

## 🎓 Formation Rapide

### Pour saisir une vente avec TVA automatique :

1. **Ouvrir** : `Comptabilité → Saisie Vente`
2. **Sélectionner** : Client
3. **Saisir** : Montant HT (exemple : 1000)
4. **Choisir** : Taux TVA (défaut : 20%)
5. **Vérifier** : TVA et TTC affichés automatiquement
6. **Valider** ✅

### Pour saisir un achat avec TVA automatique :

1. **Ouvrir** : `Comptabilité → Saisie Achat`
2. **Sélectionner** : Fournisseur
3. **Saisir** : Montant HT (exemple : 600)
4. **Choisir** : Taux TVA (défaut : 20%)
5. **Vérifier** : TVA et TTC affichés automatiquement
6. **Valider** ✅

---

## ✨ Résumé

| Fonctionnalité | Status | Description |
|----------------|--------|-------------|
| Calcul TVA Ventes | ✅ | Automatique en temps réel |
| Calcul TVA Achats | ✅ | Automatique en temps réel |
| Affichage TTC | ✅ | Instantané |
| Écritures comptables | ✅ | Générées automatiquement |
| Déclaration TVA | ✅ | Rapport automatique |
| Conformité PCG | ✅ | Comptes 4456/4457 |

---

## 💡 Astuce

**Pour les opérations courantes (ventes et achats), vous n'avez JAMAIS besoin de calculer la TVA vous-même !**

Le système :
1. Calcule la TVA
2. Affiche le TTC
3. Génère les écritures
4. Met à jour la balance
5. Prépare la déclaration TVA

**Tout est automatique !** 🎉

---

**📅 Version** : 2.0  
**🔄 Dernière mise à jour** : 2025  
**✅ Statut** : Calcul automatique opérationnel
