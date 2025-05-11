# Quoridor IA

![Quoridor](Images/img_welcome.png)

## Description

Quoridor IA est un projet pédagogique de l’Unité d’Enseignement « Intelligence Artificielle » (Université Paris Cité, 2024/2025), conçu en Python 3. Il met en œuvre :

- Une interface graphique **Tkinter** pour choisir un mode de jeu (Joueur vs Joueur, Joueur vs IA, IA vs IA, Batch IA vs IA).  
- Un moteur de plateau **Pygame** avec :  
  - Recherche de chemin A*  
  - Minimax avec élagage alpha-bêta  
  - Trois heuristiques (Facile, Intermédiaire, Difficile)  
  - Simulation de tournois automatisés  

L’objectif est de comparer les performances de différentes stratégies IA sur le jeu abstrait **Quoridor** (9×9), à informations parfaites et sans hasard.

---

## Table des matières

1. [Prérequis](#prérequis)  
2. [Installation](#installation)  
3. [Lancement](#lancement)  
4. [Structure du projet](#structure-du-projet)  
5. [Modes de jeu](#modes-de-jeu)  
6. [Simulations batch](#simulations-batch)  
7. [Auteurs & Licence](#auteurs--licence)  

---

## Prérequis

- **Python 3.8+**  
- Modules Python :
  - `pygame`
  - `tkinter` (inclus dans la plupart des distributions Python)
  - `numpy` (optionnel, selon extensions)

Vous pouvez installer les dépendances (sous Windows / macOS / Linux) :

```bash
pip install pygame
Installation
Cloner ce dépôt :

bash
Copier
Modifier
git clone https://votre-repo/quoridor-ia.git
cd quoridor-ia
Vérifier que Projet IA.py, quoridor_menus.py et launcher.py sont dans le même dossier.

Optionnel : installer une police personnalisée

Copier NovaSquare-Regular.ttf dans le dossier du projet.

Lancement
Sous PowerShell (Windows)
Ouvrez PowerShell dans le répertoire du projet.

Exécutez :

powershell
Copier
Modifier
.\start_quoridor.ps1
Vous devriez voir :

csharp
Copier
Modifier
Lancement de Quoridor...
pygame 2.x.x (SDL x.x.x, Python 3.x.x)
Hello from the pygame community. https://www.pygame.org/contribute.html
L’interface graphique Tkinter s’ouvre, suivez les menus.

Sous macOS / Linux
bash
Copier
Modifier
python launcher.py
Puis sélectionnez votre mode de jeu dans la fenêtre Tkinter.

Structure du projet
bash
Copier
Modifier
quoridor-ia/
├── __pycache__/
├── NovaSquare-Regular.ttf   # Police personnalisée
├── Projet IA.py             # Mécanique du jeu (Pygame + IA + batch)
├── quoridor_menus.py        # Menus Tkinter
├── launcher.py              # Orchestration (Tkinter → Pygame)
├── start_quoridor.ps1       # Script PowerShell de lancement
Modes de jeu
Joueur vs Joueur
Deux humains s’affrontent en local.

Joueur vs IA
Choisissez un niveau (Facile, Intermédiaire, Difficile).

IA vs IA
Sélectionnez deux difficultés IA, observez la partie.

Batch IA vs IA
Lancez N simulations ; les statistiques (victoires, nuls, nombre moyen de coups) s’affichent.

Simulations batch
Dans le mode Batch IA vs IA, chaque configuration est jouée 100 fois par défaut.

Limite de 200 tours : au-delà, la partie est considérée comme nulle (pour éviter les blocages perpétuels).

Résultats : victoires J1/J2, nuls, durée moyenne (en nombre de coups).

Auteurs
Ghilas Tidjet

Badredine Bouamama
Université Paris Cité, 2024/2025


