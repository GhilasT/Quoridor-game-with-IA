import sys
import pygame
from collections import deque
from heapq import heappush, heappop
import random

# Nouvelle exception pour le retour au menu
class ReturnToMenu(Exception):
    pass

# Variables globales pour le suivi d'état
current_game_mode = None  # NEW
current_difficulty = 2    # NEW

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
GRID_SIZE = 9
LARGEUR, HAUTEUR = 900, 900
MARGE = 50
ESPACEMENT = 8
TAILLE_CASE = (LARGEUR - 2*MARGE - 8*ESPACEMENT) // GRID_SIZE

# Créer la fenêtre
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Quoridor")

# Constantes de couleurs
FOND = (10, 20, 40)  # Bleu nuit dégradé
CASE = (250, 233, 192)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
JOUEUR1 = (130, 9, 5)
JOUEUR2 = (11, 30, 74)
MUR = (35, 82, 250)
MUR_PREVIEW = (78, 126, 255)
HIGHLIGHT = (173, 216, 230, 100)
CASE_SOMBRE = (200, 183, 142)
BUTTON_COLOR = (255, 215, 0)  # Jaune
BUTTON_HOVER_COLOR = (255, 235, 100)  # Jaune plus clair pour le survol
TEXT_COLOR = (10, 20, 40)  # Bleu nuit

# Charger la police personnalisée
font_title = pygame.font.Font('NovaSquare-Regular.ttf', 150)  # Police ajustée à 75% de 200
font_button = pygame.font.Font('NovaSquare-Regular.ttf', 35)  # Police plus petite pour le texte des boutons

murs = []
mur_preview = None
last_click_time = 0  

def a_star_search(start_pos, target_row, walls):
    """
    Algorithme A* pour trouver le chemin le plus court vers une ligne cible
    """
    if start_pos is None:
        return float('inf'), []

    def heuristic(pos, target):
        """Distance Manhattan vers la ligne cible"""
        return abs(pos[0] - target)

    # Initialisation
    open_set = []
    heappush(open_set, (heuristic(start_pos, target_row), 0, start_pos, []))  # (f, g, position, path)
    closed_set = set()

    while open_set:
        _, g_score, current_pos, path = heappop(open_set)

        # Arrivé à la ligne cible
        if current_pos[0] == target_row:
            return g_score, path + [current_pos]

        # Déjà visité
        if current_pos in closed_set:
            continue

        closed_set.add(current_pos)
        i, j = current_pos

        # Explorer les voisins
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            neighbor = (ni, nj)

            if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                if not mur_bloque_mouvement(i, j, ni, nj, walls):
                    if neighbor not in closed_set:
                        new_g = g_score + 1
                        new_f = new_g + heuristic(neighbor, target_row)
                        heappush(open_set, (new_f, new_g, neighbor, path + [current_pos]))

    return float('inf'), []  # Pas de chemin trouvé

def evaluer_position(grille, murs, murs_restants_j1, murs_restants_j2, joueur_principal=2):
    """
    Fonction d'évaluation unifiée pour les deux modes de jeu.
    Par défaut, évalue du point de vue du joueur 2 (IA) pour compatibilité avec l'ancien code.
    
    Args:
        grille: Grille de jeu actuelle
        murs: Liste des murs placés
        murs_restants_j1: Nombre de murs restants pour le joueur 1
        murs_restants_j2: Nombre de murs restants pour le joueur 2
        joueur_principal: Le joueur dont on évalue la position (1 ou 2)
        
    Returns:
        float: Score d'évaluation (positif si favorable au joueur_principal)
    """
    # Déterminer qui est le joueur et qui est l'adversaire
    joueur_num = joueur_principal
    adversaire_num = 3 - joueur_principal  # 1->2, 2->1

    # Trouver les positions des joueurs
    pos_joueur = find_player_position(grille, joueur_num)
    pos_adversaire = find_player_position(grille, adversaire_num)
    
    if pos_joueur is None or pos_adversaire is None:
        return 0
        
    # Déterminer les lignes objectifs
    ligne_obj_joueur = 8 if joueur_num == 1 else 0
    ligne_obj_adversaire = 0 if joueur_num == 1 else 8

    # Détection de fin de partie
    if pos_joueur[0] == ligne_obj_joueur:  # Joueur principal gagne
        return 10000
    if pos_adversaire[0] == ligne_obj_adversaire:  # Adversaire gagne
        return -10000
        
    # Calcul des chemins optimaux
    dist_joueur, chemin_joueur = a_star_search(pos_joueur, ligne_obj_joueur, murs)
    dist_adversaire, chemin_adversaire = a_star_search(pos_adversaire, ligne_obj_adversaire, murs)
    
    # Coefficients de pondération
    poids_distance = 5.0
    poids_avance = 3.0 
    poids_position_centrale = 0.5
    
    # Distance et progression - positif quand favorable au joueur_principal
    position_score = (dist_adversaire - dist_joueur) * poids_distance
    
    # Calcul de la progression vers l'objectif
    if joueur_num == 1:  # Joueur 1 va vers le bas (ligne 8)
        progres_joueur = pos_joueur[0] * poids_avance
    else:  # Joueur 2 va vers le haut (ligne 0)
        progres_joueur = (8 - pos_joueur[0]) * poids_avance
    
    # Bonus pour le contrôle du centre
    centre_score = 0
    if 3 <= pos_joueur[1] <= 5:
        centre_score = poids_position_centrale
    
    # Impact des murs restants en fin de partie
    murs_score = 0
    if dist_joueur <= 3 or dist_adversaire <= 3:  # En fin de partie
        murs_restants_joueur = murs_restants_j1 if joueur_num == 1 else murs_restants_j2
        murs_restants_adversaire = murs_restants_j2 if joueur_num == 1 else murs_restants_j1
        murs_score = (murs_restants_joueur - murs_restants_adversaire) * 0.5
    
    return position_score + progres_joueur + centre_score + murs_score

def evaluer_position_intermediaire(grille, murs, murs_restants_j1, murs_restants_j2, joueur_principal=2):
    """
    Fonction d'évaluation pour le niveau intermédiaire, plus orientée sur le blocage.
    
    Args:
        Identiques à evaluer_position
    """
    joueur_num = joueur_principal
    adversaire_num = 3 - joueur_principal
    
    pos_joueur = find_player_position(grille, joueur_num)
    pos_adversaire = find_player_position(grille, adversaire_num)
    
    if pos_joueur is None or pos_adversaire is None:
        return 0
        
    ligne_obj_joueur = 8 if joueur_num == 1 else 0
    ligne_obj_adversaire = 0 if joueur_num == 1 else 8

    # Détection de fin de partie
    if pos_joueur[0] == ligne_obj_joueur:
        return 10000
    if pos_adversaire[0] == ligne_obj_adversaire:
        return -10000
        
    # Calcul des chemins
    dist_joueur, chemin_joueur = a_star_search(pos_joueur, ligne_obj_joueur, murs)
    dist_adversaire, chemin_adversaire = a_star_search(pos_adversaire, ligne_obj_adversaire, murs)
    
    # Plus orienté sur le blocage de l'adversaire que l'avancée personnelle
    poids_distance_adversaire = 7.0  # Plus élevé que dans la version standard
    poids_distance_joueur = 3.0      # Moins élevé que dans la version standard
    poids_avance = 2.0
    poids_murs_restants = 1.2        # Plus d'importance aux murs
    
    # Score basé sur la différence de distance, mais favorisant le blocage
    position_score = poids_distance_adversaire * dist_adversaire - poids_distance_joueur * dist_joueur
    
    # Progression du joueur
    if joueur_num == 1:
        progres_joueur = pos_joueur[0] * poids_avance
    else:
        progres_joueur = (8 - pos_joueur[0]) * poids_avance
        
    # Favoriser la conservation des murs pour la fin de partie
    murs_restants_joueur = murs_restants_j1 if joueur_num == 1 else murs_restants_j2
    murs_restants_adversaire = murs_restants_j2 if joueur_num == 1 else murs_restants_j1
    
    murs_score = (murs_restants_joueur - murs_restants_adversaire * 0.8) * poids_murs_restants
    
    # Bonus pour être en position de bloquer l'adversaire
    dist_a_adversaire = abs(pos_joueur[0] - pos_adversaire[0]) + abs(pos_joueur[1] - pos_adversaire[1])
    bonus_blocage = 0
    if dist_a_adversaire <= 2:
        if 1 <= pos_adversaire[0] <= 7:  # Si l'adversaire n'est pas aux extrémités
            bonus_blocage = 3.0
    
    # Bonus pour les positions qui contrôlent le centre du plateau
    centre_score = 0
    if 3 <= pos_joueur[1] <= 5:
        if (joueur_num == 1 and pos_joueur[0] >= 4) or (joueur_num == 2 and pos_joueur[0] <= 4):
            centre_score = 2.5  # Forte valeur pour contrôler le centre dans la moitié adverse
        else:
            centre_score = 1.0
    
    # Pénalité pour trop s'éloigner du centre horizontalement
    ecart_centre = abs(pos_joueur[1] - 4)
    penalite_ecart = -ecart_centre * 0.5
    
    return position_score + progres_joueur + murs_score + bonus_blocage + centre_score + penalite_ecart

def evaluer_position_difficile(grille, murs, murs_restants_j1, murs_restants_j2, joueur_principal=2):
    """
    Fonction d'évaluation pour le niveau difficile, plus sophistiquée et équilibrée.
    
    Args:
        Identiques à evaluer_position
    """
    joueur_num = joueur_principal
    adversaire_num = 3 - joueur_principal
    
    pos_joueur = find_player_position(grille, joueur_num)
    pos_adversaire = find_player_position(grille, adversaire_num)
    
    if pos_joueur is None or pos_adversaire is None:
        return 0
        
    ligne_obj_joueur = 8 if joueur_num == 1 else 0
    ligne_obj_adversaire = 0 if joueur_num == 1 else 8

    # Détection de fin de partie
    if pos_joueur[0] == ligne_obj_joueur:
        return 10000
    if pos_adversaire[0] == ligne_obj_adversaire:
        return -10000
        
    # Calcul des chemins plus détaillé
    dist_joueur, chemin_joueur = a_star_search(pos_joueur, ligne_obj_joueur, murs)
    dist_adversaire, chemin_adversaire = a_star_search(pos_adversaire, ligne_obj_adversaire, murs)
    
    # Équilibre bien dosé entre progression et blocage
    poids_distance = 5.5
    poids_avance = 3.5
    poids_position_centrale = 1.0
    poids_murs_strategie = 2.0
    
    # Score basé sur la différence de distance 
    position_score = (dist_adversaire - dist_joueur) * poids_distance
    
    # Progression et avancement sur le plateau
    if joueur_num == 1:
        progres_joueur = pos_joueur[0] * poids_avance
    else:
        progres_joueur = (8 - pos_joueur[0]) * poids_avance
    
    # Contrôle du centre avec plus de nuances
    centre_score = 0
    if 2 <= pos_joueur[1] <= 6:  # Zone plus large que la version de base
        centre_bonus = 6 - abs(pos_joueur[1] - 4) * 2  # Bonus dégressif depuis la colonne centrale
        centre_score = centre_bonus * poids_position_centrale
    
    # Bonus pour les positions de jeu stratégiques
    position_strategique = 0
    if (joueur_num == 1 and pos_joueur[0] >= 5) or (joueur_num == 2 and pos_joueur[0] <= 3):
        # Position avancée dans le territoire adverse
        position_strategique += 2.0
    
    # La différence de chemins alternatifs (mesure la flexibilité de mouvement)
    chemins_joueur = count_chemins_alternatifs(pos_joueur, ligne_obj_joueur, murs, max_depth=6)
    chemins_adversaire = count_chemins_alternatifs(pos_adversaire, ligne_obj_adversaire, murs, max_depth=6)
    score_flexibilite = (chemins_joueur - chemins_adversaire) * 0.5
    
    # Utilisation stratégique des murs (variable selon la phase de jeu)
    murs_restants_joueur = murs_restants_j1 if joueur_num == 1 else murs_restants_j2
    murs_restants_adversaire = murs_restants_j2 if joueur_num == 1 else murs_restants_j1
    
    # En début de partie, conserver ses murs
    if len(murs) < 8:
        murs_score = murs_restants_joueur * 0.4
    # En milieu de partie, les utiliser stratégiquement
    elif len(murs) < 16:
        ratio_joueur_adverse = murs_restants_joueur / (murs_restants_adversaire + 0.1)
        murs_score = ratio_joueur_adverse * poids_murs_strategie
    # En fin de partie, pousser pour la victoire ou bloquer l'adversaire
    else:
        if dist_joueur < dist_adversaire:
            # Si on est en avance, garder des murs pour bloquer le rattrapage
            murs_score = murs_restants_joueur * 0.8
        else:
            # Si on est en retard, valeur moindre des murs
            murs_score = murs_restants_joueur * 0.3
    
    return position_score + progres_joueur + centre_score + position_strategique + score_flexibilite + murs_score

def minimax(grille, murs, murs_restants_j1, murs_restants_j2, profondeur, alpha, beta, 
           est_maximisant, tour_joueur, joueur_principal=2, difficulte=5):
    """
    Implémentation unifiée de minimax avec élagage alpha-beta.
    Utilise différentes fonctions d'évaluation selon la difficulté.
    
    Args:
        grille: Grille de jeu actuelle
        murs: Liste des murs placés
        murs_restants_j1, murs_restants_j2: Nombre de murs restants
        profondeur: Profondeur restante de recherche
        alpha, beta: Valeurs pour l'élagage
        est_maximisant: Si c'est le tour du joueur maximisant
        tour_joueur: Le joueur qui joue actuellement (1 ou 2)
        joueur_principal: Le joueur pour lequel on optimise (1 ou 2)
        difficulte: Le niveau de difficulté qui détermine la fonction d'évaluation
        
    Returns:
        float: Score de la meilleure position trouvée
    """
    # Vérifier fin de partie ou profondeur max atteinte
    if profondeur == 0:
        if difficulte == 1:
            return evaluer_position(grille, murs, murs_restants_j1, murs_restants_j2, joueur_principal)
        elif difficulte == 3:
            return evaluer_position_intermediaire(grille, murs, murs_restants_j1, murs_restants_j2, joueur_principal)
        else:  # difficulté 5
            return evaluer_position_difficile(grille, murs, murs_restants_j1, murs_restants_j2, joueur_principal)

    pos_joueur = find_player_position(grille, tour_joueur)
    if pos_joueur is None:
        return 0

    # Ligne objectif dépend du joueur
    ligne_obj = 8 if tour_joueur == 1 else 0

    # Vérifier victoire
    if pos_joueur[0] == ligne_obj:
        return float('inf') if tour_joueur == joueur_principal else float('-inf')

    # Obtenir coups possibles
    i, j = pos_joueur
    coups_possibles = get_possible_moves(i, j, tour_joueur, grille)

    # Tour du joueur maximisant (joueur_principal)
    if est_maximisant:
        meilleur_score = float('-inf')
        for coup in coups_possibles:
            ni, nj = coup
            # Simuler le coup
            grille_temp = [ligne[:] for ligne in grille]
            grille_temp[i][j] = 0
            grille_temp[ni][nj] = tour_joueur

            # Appel récursif - prochain joueur
            prochain_tour = 3 - tour_joueur  # 1->2, 2->1
            score = minimax(grille_temp, murs,
                          murs_restants_j1 if tour_joueur == 2 else murs_restants_j1,
                          murs_restants_j2 if tour_joueur == 1 else murs_restants_j2,
                          profondeur - 1, alpha, beta, False, prochain_tour, joueur_principal, difficulte)

            meilleur_score = max(score, meilleur_score)
            alpha = max(alpha, meilleur_score)

            # Élagage
            if beta <= alpha:
                break

        return meilleur_score

    # Tour du joueur minimisant
    else:
        meilleur_score = float('inf')
        for coup in coups_possibles:
            ni, nj = coup
            # Simuler le coup
            grille_temp = [ligne[:] for ligne in grille]
            grille_temp[i][j] = 0
            grille_temp[ni][nj] = tour_joueur

            # Appel récursif - prochain joueur
            prochain_tour = 3 - tour_joueur  # 1->2, 2->1
            score = minimax(grille_temp, murs,
                          murs_restants_j1 if tour_joueur == 2 else murs_restants_j1,
                          murs_restants_j2 if tour_joueur == 1 else murs_restants_j2,
                          profondeur - 1, alpha, beta, True, prochain_tour, joueur_principal, difficulte)

            meilleur_score = min(score, meilleur_score)
            beta = min(beta, meilleur_score)

            # Élagage
            if beta <= alpha:
                break

        return meilleur_score

def meilleur_deplacement_pour_joueur(grille, murs, joueur_num, pos_joueur, profondeur, 
                                    murs_restants_joueur, murs_restants_adversaire, difficulte):
    """Détermine le meilleur déplacement pour un joueur"""
    i, j = pos_joueur
    coups_possibles = get_possible_moves(i, j, joueur_num, grille)
    
    if not coups_possibles:
        return None, None
        
    meilleur_score = float('-inf')
    meilleur_coup = None
    
    for coup in coups_possibles:
        ni, nj = coup
        # Score de base selon la difficulté
        score_base = 0
        
        # Bonus pour direction favorable
        if (joueur_num == 1 and ni > i) or (joueur_num == 2 and ni < i):
            score_base += 2 if difficulte == 5 else 3  # Plus agressif pour l'IA intermédiaire
            
        # Bonus pour position centrale
        if 3 <= nj <= 5:
            score_base += 1
            
        # Simuler le déplacement
        grille_temp = [ligne[:] for ligne in grille]
        grille_temp[i][j] = 0
        grille_temp[ni][nj] = joueur_num
        
        # Évaluation minimax avec la difficulté appropriée
        score_minimax = minimax(grille_temp, murs, 
                              murs_restants_j1=murs_restants_adversaire if joueur_num == 2 else murs_restants_joueur,
                              murs_restants_j2=murs_restants_adversaire if joueur_num == 1 else murs_restants_joueur,
                              profondeur=profondeur - 1, 
                              alpha=float('-inf'), beta=float('inf'), 
                              est_maximisant=False, 
                              tour_joueur=3 - joueur_num,
                              joueur_principal=joueur_num,
                              difficulte=difficulte)
        
        # Score final
        score_final = score_base + score_minimax
        
        if score_final > meilleur_score:
            meilleur_score = score_final
            meilleur_coup = coup
            
    return meilleur_coup, "deplacement"

def murs_proches_des_chemins_critique(grille, walls, pos_joueur, target_row, difficulte=5):
    """Identifie les murs potentiels qui ralentissent efficacement l'adversaire"""
    # Trouver le chemin optimal actuel
    dist_actuelle, chemin = a_star_search(pos_joueur, target_row, walls)

    murs_candidats = []
    murs_evalues = []
    
    # Stratégies différentes selon la difficulté
    chemins_a_analyser = 1  # Base 
    if difficulte == 3:
        # L'IA intermédiaire analysera plus de segments pour trouver des opportunités de blocage
        chemins_a_analyser = min(len(chemin) - 1, 4)  # Analyser jusqu'à 4 segments du chemin
    elif difficulte == 5:
        # L'IA difficile est plus sélective et efficace
        chemins_a_analyser = min(len(chemin) - 1, 3)  # Analyser jusqu'à 3 segments du chemin

    # Analyser chaque segment du chemin pour les murs potentiels
    for i in range(min(chemins_a_analyser, len(chemin) - 1)):
        curr_i, curr_j = chemin[i]
        next_i, next_j = chemin[i + 1]

        # Différence de position
        di = next_i - curr_i
        dj = next_j - curr_j

        # Générer des murs possibles
        murs_possibles = []

        # Si mouvement horizontal
        if di == 0:
            x = min(curr_j, next_j)
            # Mur vertical pour bloquer ce mouvement
            murs_possibles.append({'x': x, 'y': curr_i - 1, 'orientation': 'V'})
            murs_possibles.append({'x': x, 'y': curr_i, 'orientation': 'V'})
            
            # Pour le niveau intermédiaire, ajouter des murs adjacents pour créer des labyrinthes
            if difficulte == 3 and curr_i > 0 and curr_i < GRID_SIZE-1:
                murs_possibles.append({'x': x - 1 if x > 0 else x, 'y': curr_i, 'orientation': 'H'})
                murs_possibles.append({'x': x, 'y': curr_i, 'orientation': 'H'})

        # Si mouvement vertical
        elif dj == 0:
            y = min(curr_i, next_i)
            # Mur horizontal pour bloquer ce mouvement
            murs_possibles.append({'x': curr_j - 1, 'y': y, 'orientation': 'H'})
            murs_possibles.append({'x': curr_j, 'y': y, 'orientation': 'H'})
            
            # Pour le niveau intermédiaire, ajouter des murs adjacents pour créer des labyrinthes
            if difficulte == 3 and curr_j > 0 and curr_j < GRID_SIZE-1:
                murs_possibles.append({'x': curr_j, 'y': y - 1 if y > 0 else y, 'orientation': 'V'})
                murs_possibles.append({'x': curr_j, 'y': y, 'orientation': 'V'})

        # Évaluer chaque mur possible
        for mur in murs_possibles:
            if (0 <= mur['x'] <= GRID_SIZE-2 and
                0 <= mur['y'] <= GRID_SIZE-2 and
                mur not in murs_evalues):

                murs_evalues.append(mur)

                if mur_est_valide(mur) and mur not in walls:
                    temp_walls = walls.copy()
                    temp_walls.append(mur)

                    # Vérifier que les deux joueurs ont toujours un chemin
                    pos_j1 = find_player_position(grille, 1)
                    pos_j2 = find_player_position(grille, 2)

                    if (has_path(pos_j1, 8, temp_walls) and
                        has_path(pos_j2, 0, temp_walls)):

                        # Calculer la nouvelle distance
                        nouvelle_dist, _ = a_star_search(pos_joueur, target_row, temp_walls)

                        # Gain = augmentation de distance
                        gain = nouvelle_dist - dist_actuelle
                        
                        # Pour l'IA intermédiaire, considérer aussi les murs qui créent des détours plus longs
                        if difficulte == 3 and gain > 0:
                            # Bonus pour les murs qui forcent l'adversaire à faire un grand détour
                            chemins_avant = count_chemins_alternatifs(pos_joueur, target_row, walls, max_depth=4)
                            chemins_apres = count_chemins_alternatifs(pos_joueur, target_row, temp_walls, max_depth=4)
                            
                            # Si le mur réduit significativement les options de l'adversaire
                            if chemins_avant > chemins_apres:
                                gain += (chemins_avant - chemins_apres) * 0.5

                        if gain > 0:
                            murs_candidats.append((mur, gain))

    # Trier les murs par gain décroissant
    murs_candidats.sort(key=lambda x: x[1], reverse=True)

    # Retourner les meilleurs murs (plus nombreux pour l'IA intermédiaire)
    if difficulte == 3:
        return [mur for mur, _ in murs_candidats[:7]]  # Plus d'options pour l'IA intermédiaire
    else:
        return [mur for mur, _ in murs_candidats[:5]]

def meilleur_mur_pour_joueur(grille, murs, pos_adversaire, pos_joueur, joueur_num, 
                           murs_restants, murs_restants_adversaire, ligne_obj_adv, 
                           profondeur, difficulte):
    """Détermine le meilleur mur à placer pour un joueur"""
    # Trouver des murs candidats avec la difficulté appropriée
    murs_candidats = murs_proches_des_chemins_critique(grille, murs, pos_adversaire, ligne_obj_adv, difficulte)
    
    if not murs_candidats:
        return None, None
    
    meilleur_score = float('-inf')
    meilleur_mur = None
    
    max_candidats = 7 if difficulte == 3 else 5
    
    for mur in murs_candidats[:max_candidats]:
        if mur_est_valide(mur) and mur not in murs:
            temp_murs = murs.copy()
            temp_murs.append(mur)
            
            # Vérifier que les deux joueurs ont toujours un chemin
            ligne_obj_joueur = 8 if joueur_num == 1 else 0
            if has_path(pos_adversaire, ligne_obj_adv, temp_murs) and has_path(pos_joueur, ligne_obj_joueur, temp_murs):
                # Évaluation avec la fonction appropriée à la difficulté
                score = minimax(grille, temp_murs,
                              murs_restants_j1=murs_restants_adversaire if joueur_num == 2 else murs_restants - 1,
                              murs_restants_j2=murs_restants_adversaire if joueur_num == 1 else murs_restants - 1,
                              profondeur=profondeur - 1,
                              alpha=float('-inf'), beta=float('inf'),
                              est_maximisant=False, 
                              tour_joueur=3 - joueur_num,
                              joueur_principal=joueur_num,
                              difficulte=difficulte)
                
                # Pour l'IA intermédiaire, favoriser les murs qui créent des déviations complexes
                if difficulte == 3:
                    # Vérifier l'impact sur les chemins alternatifs de l'adversaire
                    chemins_avant = count_chemins_alternatifs(pos_adversaire, ligne_obj_adv, murs, max_depth=4)
                    chemins_apres = count_chemins_alternatifs(pos_adversaire, ligne_obj_adv, temp_murs, max_depth=4)
                    
                    # Bonus pour réduire les options
                    score += (chemins_avant - chemins_apres) * 2.0
                    
                    # Également vérifier l'impact sur la distance
                    dist_avant, _ = a_star_search(pos_adversaire, ligne_obj_adv, murs)
                    dist_apres, _ = a_star_search(pos_adversaire, ligne_obj_adv, temp_murs)
                    
                    # Bonus pour l'augmentation de la distance
                    if dist_apres > dist_avant:
                        score += (dist_apres - dist_avant) * 3.0
                
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_mur = mur
                
    return meilleur_mur, "mur" if meilleur_mur else None

def meilleur_coup_ia(grille, murs, murs_restants_j1, murs_restants_j2, difficulte, joueur_num=2):
    """
    Fonction unifiée pour déterminer le meilleur coup de l'IA.
    Par défaut, joue pour le joueur 2 (IA) pour compatibilité.
    
    Args:
        grille: Grille de jeu actuelle
        murs: Liste des murs placés
        murs_restants_j1, murs_restants_j2: Nombre de murs restants
        difficulte: Niveau de difficulté (1=facile, 3=moyen, 5=difficile)
        joueur_num: Le joueur pour lequel on cherche le meilleur coup (1 ou 2)
        
    Returns:
        tuple: (coup, type_coup) où coup est la position ou le mur,
               et type_coup est "deplacement" ou "mur"
    """
    pos_joueur = find_player_position(grille, joueur_num)
    adversaire_num = 3 - joueur_num
    pos_adversaire = find_player_position(grille, adversaire_num)
    
    if pos_joueur is None or pos_adversaire is None:
        return None, None

    # Configuration selon la difficulté
    profondeur_recherche = {
        1: 1,   # Facile
        3: 3,   # Moyen
        5: 4    # Difficile (légère augmentation)
    }.get(difficulte, 3)
    
    murs_restants_joueur = murs_restants_j1 if joueur_num == 1 else murs_restants_j2
    murs_restants_adversaire = murs_restants_j2 if joueur_num == 1 else murs_restants_j1

    # Stratégie simplifiée pour le niveau facile
    if difficulte == 1:
        # Déplacement purement directionnel avec Manhattan
        i, j = pos_joueur
        coups_possibles = get_possible_moves(i, j, joueur_num, grille)
        if not coups_possibles:
            return None, None
            
        # Choisir le coup qui rapproche le plus de l'objectif
        direction = -1 if joueur_num == 2 else 1
        coups_tries = sorted(coups_possibles, key=lambda x: (direction * x[0], abs(x[1] - 4)))
        return coups_tries[0], "deplacement"

    # Stratégie pour niveau moyen et difficile
    else:
        # Calcul des chemins vers l'objectif
        ligne_obj_joueur = 8 if joueur_num == 1 else 0
        ligne_obj_adversaire = 0 if joueur_num == 1 else 8
        
        dist_joueur, _ = a_star_search(pos_joueur, ligne_obj_joueur, murs)
        dist_adv, _ = a_star_search(pos_adversaire, ligne_obj_adversaire, murs)
        
        # Ajuster la stratégie selon la situation
        if difficulte == 3:  # Moyen - plus agressif avec les murs
            # Plus de murs quand en désavantage ou quand l'adversaire est proche de gagner
            if dist_joueur > dist_adv or dist_adv <= 3:
                priorite_deplacement = 0.4  # 60% de chances de placer un mur
            else:
                priorite_deplacement = 0.65  # 35% de chances de placer un mur
        else:  # Difficile - stratégie plus équilibrée
            priorite_deplacement = 0.75 if dist_joueur <= dist_adv else 0.6
            if dist_adv <= 2:  # Si l'adversaire est près de gagner, priorité aux murs
                priorite_deplacement = 0.3
        
        # Décision: déplacement ou pose de mur
        if random.random() < priorite_deplacement or murs_restants_joueur == 0:
            # DÉPLACEMENT
            return meilleur_deplacement_pour_joueur(grille, murs, joueur_num, pos_joueur, profondeur_recherche,
                                                  murs_restants_joueur, murs_restants_adversaire, difficulte)
        else:
            # MUR
            ligne_obj_adv = 8 if adversaire_num == 1 else 0
            mur_candidat, type_coup = meilleur_mur_pour_joueur(grille, murs, pos_adversaire, pos_joueur, 
                                                            joueur_num, murs_restants_joueur, 
                                                            murs_restants_adversaire, ligne_obj_adv, 
                                                            profondeur_recherche, difficulte)
            
            if mur_candidat:
                return mur_candidat, type_coup
            else:
                # Fallback sur déplacement si pas de bon mur
                return meilleur_deplacement_pour_joueur(grille, murs, joueur_num, pos_joueur, profondeur_recherche,
                                                      murs_restants_joueur, murs_restants_adversaire, difficulte)

def dessiner_murs(surface):
    global mur_preview
    for mur in murs:
        if mur['orientation'] == 'H':
            x = MARGE + mur['x'] * (TAILLE_CASE + ESPACEMENT)
            y = MARGE + (mur['y'] + 1) * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
            largeur = 2 * TAILLE_CASE + ESPACEMENT
            hauteur = ESPACEMENT
        else:
            x = MARGE + (mur['x'] + 1) * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
            y = MARGE + mur['y'] * (TAILLE_CASE + ESPACEMENT)
            largeur = ESPACEMENT
            hauteur = 2 * TAILLE_CASE + ESPACEMENT

        pygame.draw.rect(surface, MUR, (x, y, largeur, hauteur))

    if mur_preview and mur_est_valide(mur_preview) and mur_preview not in murs:
        if mur_preview['orientation'] == 'H':
            x = MARGE + mur_preview['x'] * (TAILLE_CASE + ESPACEMENT)
            y = MARGE + (mur_preview['y'] + 1) * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
            largeur = 2 * TAILLE_CASE + ESPACEMENT
            hauteur = ESPACEMENT
        else:
            x = MARGE + (mur_preview['x'] + 1) * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
            y = MARGE + mur_preview['y'] * (TAILLE_CASE + ESPACEMENT)
            largeur = ESPACEMENT
            hauteur = 2 * TAILLE_CASE + ESPACEMENT

        pygame.draw.rect(surface, MUR_PREVIEW, (x, y, largeur, hauteur))


def conflit(mur1, mur2):
    if mur1['orientation'] != mur2['orientation']:
        return False

    if mur1['orientation'] == 'H':
        return (mur1['y'] == mur2['y'] and
                mur1['x'] <= mur2['x'] + 1 and
                mur1['x'] + 1 >= mur2['x'])
    else:
        return (mur1['x'] == mur2['x'] and
                mur1['y'] <= mur2['y'] + 1 and
                mur1['y'] + 1 >= mur2['y'])

def mur_est_valide(mur, murs_locaux=None):
    """Version modifiée pour accepter une liste de murs optionnelle"""
    if murs_locaux is None:
        murs_locaux = murs
        
    if not (0 <= mur['x'] <= GRID_SIZE-2 and
            0 <= mur['y'] <= GRID_SIZE-2):
        return False

    for mur_existant in murs_locaux:
        if conflit(mur, mur_existant):
            return False

    return True

def convertir_pos_souris_en_cell(pos):
    x, y = pos
    x_rel = x - MARGE
    y_rel = y - MARGE

    if x_rel < 0 or y_rel < 0:
        return None, None

    cell_x = x_rel // (TAILLE_CASE + ESPACEMENT)
    cell_y = y_rel // (TAILLE_CASE + ESPACEMENT)

    if cell_x >= GRID_SIZE or cell_y >= GRID_SIZE:
        return None, None

    offset_x = x_rel % (TAILLE_CASE + ESPACEMENT)
    offset_y = y_rel % (TAILLE_CASE + ESPACEMENT)

    if offset_x > TAILLE_CASE or offset_y > TAILLE_CASE:
        return None, None

    return cell_y, cell_x

def mur_bloque_mouvement(current_i, current_j, target_i, target_j, walls=None):
    if walls is None:
        walls = murs
    di = target_i - current_i
    dj = target_j - current_j

    if di == 0 and abs(dj) == 1:
        x = min(current_j, target_j)
        orientation = 'V'
        for mur in walls:
            if mur['orientation'] == orientation and mur['x'] == x:
                if mur['y'] <= current_i <= mur['y'] + 1:
                    return True
    elif abs(di) == 1 and dj == 0:
        y = min(current_i, target_i)
        orientation = 'H'
        for mur in walls:
            if mur['orientation'] == orientation and mur['y'] == y:
                if mur['x'] <= current_j <= mur['x'] + 1:
                    return True
    return False

def mouvement_est_valide(current_i, current_j, target_i, target_j, tour_joueur, grille):
    di = target_i - current_i
    dj = target_j - current_j

    if (abs(di) == 1 and dj == 0) or (di == 0 and abs(dj) == 1):
        return not mur_bloque_mouvement(current_i, current_j, target_i, target_j)

    if (abs(di) == 2 and dj == 0) or (di == 0 and abs(dj) == 2):
        mi = current_i + di//2
        mj = current_j + dj//2

        if 0 <= mi < GRID_SIZE and 0 <= mj < GRID_SIZE:
            if grille[mi][mj] not in (0, tour_joueur):
                return (not mur_bloque_mouvement(current_i, current_j, mi, mj) and
                        not mur_bloque_mouvement(mi, mj, target_i, target_j))

    return False

def get_possible_moves(i, j, tour_joueur, grille):
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
            if not mur_bloque_mouvement(i, j, ni, nj) and grille[ni][nj] == 0:
                moves.append((ni, nj))
            elif grille[ni][nj] not in (0, tour_joueur):
                ni2, nj2 = ni + di, nj + dj
                if 0 <= ni2 < GRID_SIZE and 0 <= nj2 < GRID_SIZE:
                    if (not mur_bloque_mouvement(i, j, ni, nj) and
                        not mur_bloque_mouvement(ni, nj, ni2, nj2) and
                        grille[ni2][nj2] == 0):
                        moves.append((ni2, nj2))
    return moves

def find_player_position(grille, player_num):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grille[i][j] == player_num:
                return (i, j)
    return None

def has_path(start_pos, target_row, walls):
    if start_pos is None:
        return False
    visited = set()
    queue = deque([start_pos])
    visited.add(start_pos)

    while queue:
        i, j = queue.popleft()
        if i == target_row:
            return True
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                if not mur_bloque_mouvement(i, j, ni, nj, walls):
                    if (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
    return False

def gestion_clic_souris(pos_souris, grille):
    global murs

    x_relatif = pos_souris[0] - MARGE
    y_relatif = pos_souris[1] - MARGE

    if x_relatif < 0 or y_relatif < 0:
        return False

    max_grid = GRID_SIZE * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
    if x_relatif > max_grid or y_relatif > max_grid:
        return False

    case_x = x_relatif // (TAILLE_CASE + ESPACEMENT)
    case_y = y_relatif // (TAILLE_CASE + ESPACEMENT)
    case_x = min(case_x, GRID_SIZE-2)
    case_y = min(case_y, GRID_SIZE-2)

    offset_x = x_relatif % (TAILLE_CASE + ESPACEMENT)
    offset_y = y_relatif % (TAILLE_CASE + ESPACEMENT)

    seuil = 10
    nouveau_mur = None

    if abs(offset_y - (TAILLE_CASE + ESPACEMENT)) < seuil:
        nouveau_mur = {'x': case_x, 'y': case_y, 'orientation': 'H'}
    elif abs(offset_x - (TAILLE_CASE + ESPACEMENT)) < seuil:
        nouveau_mur = {'x': case_x, 'y': case_y, 'orientation': 'V'}

    if nouveau_mur and mur_est_valide(nouveau_mur) and nouveau_mur not in murs:
        temp_murs = murs.copy()
        temp_murs.append(nouveau_mur)
        player1_pos = find_player_position(grille, 1)
        player2_pos = find_player_position(grille, 2)

        if (player1_pos is not None and player2_pos is not None and
            has_path(player1_pos, 8, temp_murs) and
            has_path(player2_pos, 0, temp_murs)):
            murs.append(nouveau_mur)
            return True
        else:
            return False
    return False

def gestion_hover_souris(pos_souris):
    global mur_preview
    x_relatif = pos_souris[0] - MARGE
    y_relatif = pos_souris[1] - MARGE

    if x_relatif < 0 or y_relatif < 0:
        mur_preview = None
        return

    max_grid = GRID_SIZE * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
    if x_relatif > max_grid or y_relatif > max_grid:
        mur_preview = None
        return

    case_x = x_relatif // (TAILLE_CASE + ESPACEMENT)
    case_y = y_relatif // (TAILLE_CASE + ESPACEMENT)
    case_x = min(case_x, GRID_SIZE-2)
    case_y = min(case_y, GRID_SIZE-2)

    offset_x = x_relatif % (TAILLE_CASE + ESPACEMENT)
    offset_y = y_relatif % (TAILLE_CASE + ESPACEMENT)

    seuil = 10
    nouveau_mur = None

    if abs(offset_y - (TAILLE_CASE + ESPACEMENT)) < seuil:
        nouveau_mur = {'x': case_x, 'y': case_y, 'orientation': 'H'}
    elif abs(offset_x - (TAILLE_CASE + ESPACEMENT)) < seuil:
        nouveau_mur = {'x': case_x, 'y': case_y, 'orientation': 'V'}

    mur_preview = nouveau_mur if (nouveau_mur and mur_est_valide(nouveau_mur)) else None

def creer_grille():
    grille = [[0 for _ in range(9)] for _ in range(9)]
    grille[0][4] = 1
    grille[8][4] = 2
    return grille

def dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves):
    fenetre.fill(FOND)
    for i in range(9):
        for j in range(9):
            couleur = CASE_SOMBRE if i in (0, 8) else CASE
            rect = pygame.Rect(j * (TAILLE_CASE + ESPACEMENT) + MARGE,
                             i * (TAILLE_CASE + ESPACEMENT) + MARGE,
                             TAILLE_CASE, TAILLE_CASE)
            pygame.draw.rect(fenetre, couleur, rect)

    for i in range(9):
        for j in range(9):
            if grille[i][j] == 1:
                pos = (j * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE//2,
                       i * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE//2)
                pygame.draw.circle(fenetre, JOUEUR1, pos, TAILLE_CASE//3)
                if joueur_selectionne == (i, j):
                    pygame.draw.circle(fenetre, BLANC, pos, TAILLE_CASE//3 + 2, 2)
            elif grille[i][j] == 2:
                pos = (j * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE//2,
                       i * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE//2)
                pygame.draw.circle(fenetre, JOUEUR2, pos, TAILLE_CASE//3)
                if joueur_selectionne == (i, j):
                    pygame.draw.circle(fenetre, BLANC, pos, TAILLE_CASE//3 + 2, 2)

    if joueur_selectionne is not None:
        surface_highlight = pygame.Surface((TAILLE_CASE, TAILLE_CASE), pygame.SRCALPHA)
        surface_highlight.fill(HIGHLIGHT)

        for mi, mj in possible_moves:
            rect = pygame.Rect(
                mj * (TAILLE_CASE + ESPACEMENT) + MARGE,
                mi * (TAILLE_CASE + ESPACEMENT) + MARGE,
                TAILLE_CASE,
                TAILLE_CASE
            )
            fenetre.blit(surface_highlight, rect.topleft)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_button(surface, text, x, y, width, height, color, hover_color, action=None):
    global last_click_time  # Accès à la variable globale
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    COOLDOWN = 300  # Délai de 300 millisecondes

    if x <= mouse[0] <= x + width and y <= mouse[1] <= y + height:
        pygame.draw.rect(surface, hover_color, (x, y, width, height))
        if click and action is not None:
            current_time = pygame.time.get_ticks()
            if current_time - last_click_time > COOLDOWN:
                action()
                last_click_time = current_time  # Mise à jour du dernier clic
    else:
        pygame.draw.rect(surface, color, (x, y, width, height))

    draw_text(text, font_button, TEXT_COLOR, surface, x + width // 2, y + height // 2)
    
def show_winner(winner):
    global murs, current_game_mode  # MODIFIED
    murs = []

    button_width = 300
    button_height = 60
    was_pve_mode = current_game_mode == 'PVE'  # MODIFIED

    try:  # NEW
        while True:
            fenetre.fill(FOND)
            draw_text(f"Joueur {winner} gagne !", font_title, BUTTON_COLOR, fenetre, LARGEUR//2, HAUTEUR//2 - 100)

            # Bouton Menu Principal
            draw_button(fenetre, "Menu Principal", (LARGEUR - button_width)//2, HAUTEUR//2,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: exec("raise ReturnToMenu()"))  # MODIFIED

            # Bouton Rejouer
            mode_text = "Rejouer contre IA" if was_pve_mode else "Rejouer"
            draw_button(fenetre, mode_text, (LARGEUR - button_width)//2, HAUTEUR//2 + button_height + 20,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: restart_game(was_pve_mode))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
    except ReturnToMenu:  # NEW
        return

def mainPVE(difficulte=None):  # MODIFIED
    global current_game_mode, current_difficulty  # NEW
    if difficulte is None:
        difficulte = current_difficulty
    current_game_mode = 'PVE'
    current_difficulty = difficulte

    grille = creer_grille()
    tour_joueur = 1
    joueur_selectionne = None
    possible_moves = []
    murs_restants_j1 = 10
    murs_restants_j2 = 10

    try:  # NEW
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if tour_joueur == 1:
                        i, j = convertir_pos_souris_en_cell(event.pos)

                        if joueur_selectionne is not None:
                            if i is None or j is None:
                                joueur_selectionne = None
                                possible_moves = []
                            elif i == joueur_selectionne[0] and j == joueur_selectionne[1]:
                                joueur_selectionne = None
                                possible_moves = []
                            else:
                                current_i, current_j = joueur_selectionne
                                if mouvement_est_valide(current_i, current_j, i, j, tour_joueur, grille):
                                    if grille[i][j] == 0:
                                        grille[current_i][current_j] = 0
                                        grille[i][j] = tour_joueur

                                        # Vérification victoire joueur
                                        if i == 8:
                                            show_winner(1)
                                            return

                                        joueur_selectionne = None
                                        possible_moves = []
                                        tour_joueur = 2

                        else:
                            if i is not None and j is not None and grille[i][j] == tour_joueur:
                                joueur_selectionne = (i, j)
                                possible_moves = get_possible_moves(i, j, tour_joueur, grille)
                            elif gestion_clic_souris(event.pos, grille):
                                # Le joueur a posé un mur
                                murs_restants_j1 -= 1
                                possible_moves = []
                                tour_joueur = 2
                elif event.type == pygame.MOUSEMOTION:
                    gestion_hover_souris(event.pos)

            if tour_joueur == 2:
                # Afficher la sélection et les coups possibles de l'IA
                pos_ia = find_player_position(grille, 2)
                if pos_ia:
                    joueur_selectionne = pos_ia
                    possible_moves = get_possible_moves(pos_ia[0], pos_ia[1], 2, grille)
                    # Mise à jour de l'affichage pour les surbrillances
                    dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
                    dessiner_murs(fenetre)
                    pygame.display.flip()
                    pygame.time.wait(500)  # Délai pour visualiser

                # Calcul du meilleur coup avec l'IA améliorée
                coup, type_coup = meilleur_coup_ia(grille, murs, murs_restants_j1, murs_restants_j2, difficulte)

                # Vérification pour s'assurer qu'un coup est joué
                if coup and type_coup == "deplacement":
                    ni, nj = coup
                    pos_ia = find_player_position(grille, 2)
                    if pos_ia:
                        i, j = pos_ia
                        grille[i][j] = 0
                        grille[ni][nj] = 2

                        # Prévisualisation et mise à jour
                        joueur_selectionne = None
                        possible_moves = []
                        dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
                        dessiner_murs(fenetre)
                        pygame.display.flip()
                        pygame.time.wait(500)

                        # Vérification victoire IA
                        if ni == 0:
                            show_winner(2)
                            return
                elif coup and type_coup == "mur":
                    # Prévisualisation du mur
                    global mur_preview
                    mur_preview = coup
                    dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
                    dessiner_murs(fenetre)
                    pygame.display.flip()
                    pygame.time.wait(500)

                    # Pose du mur
                    murs.append(coup)
                    mur_preview = None
                    murs_restants_j2 -= 1
                else:
                    # Si aucun coup n'a été retourné, on force un mouvement simple vers l'avant si possible
                    pos_ia = find_player_position(grille, 2)
                    if pos_ia:
                        i, j = pos_ia
                        # Essayer d'avancer vers le haut (ligne 0) si possible
                        if i > 0 and grille[i-1][j] == 0 and not mur_bloque_mouvement(i, j, i-1, j):
                            grille[i][j] = 0
                            grille[i-1][j] = 2
                            # Vérification victoire IA
                            if i-1 == 0:
                                show_winner(2)
                                return
                        # Sinon essayer de se déplacer dans une direction valide aléatoire
                        else:
                            moves = get_possible_moves(i, j, 2, grille)
                            if moves:
                                ni, nj = random.choice(moves)
                                grille[i][j] = 0
                                grille[ni][nj] = 2
                                # Vérification victoire IA
                                if ni == 0:
                                    show_winner(2)
                                    return

                tour_joueur = 1
                joueur_selectionne = None
                possible_moves = []

            dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
            dessiner_murs(fenetre)

            # Afficher le nombre de murs restants
            mur_font = pygame.font.Font('NovaSquare-Regular.ttf', 20)
            draw_text(f"Murs J1: {murs_restants_j1}", mur_font, BLANC, fenetre, LARGEUR - 100, 20)
            draw_text(f"Murs IA: {murs_restants_j2}", mur_font, BLANC, fenetre, LARGEUR - 100, 50)

            pygame.display.flip()
    except ReturnToMenu:  # NEW
        return

def mainPVP():
    global current_game_mode  # NEW
    current_game_mode = 'PVP'
    grille = creer_grille()
    tour_joueur = 1
    joueur_selectionne = None
    possible_moves = []

    try:  # NEW
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    i, j = convertir_pos_souris_en_cell(event.pos)

                    if joueur_selectionne is not None:
                        if i is None or j is None:
                            joueur_selectionne = None
                            possible_moves = []
                        elif i == joueur_selectionne[0] and j == joueur_selectionne[1]:
                            joueur_selectionne = None
                            possible_moves = []
                        else:
                            current_i, current_j = joueur_selectionne
                            if mouvement_est_valide(current_i, current_j, i, j, tour_joueur, grille):
                                if grille[i][j] == 0:
                                    grille[current_i][current_j] = 0
                                    grille[i][j] = tour_joueur

                                    # Vérification victoire
                                    if (tour_joueur == 1 and i == 8) or (tour_joueur == 2 and i == 0):
                                        show_winner(tour_joueur)
                                        return

                                    joueur_selectionne = None
                                    possible_moves = []
                                    tour_joueur = 2 if tour_joueur == 1 else 1

                    else:
                        if gestion_clic_souris(event.pos, grille):
                            possible_moves = []
                            tour_joueur = 2 if tour_joueur == 1 else 1
                        elif i is not None and j is not None and grille[i][j] == tour_joueur:
                            joueur_selectionne = (i, j)
                            possible_moves = get_possible_moves(i, j, tour_joueur, grille)
                elif event.type == pygame.MOUSEMOTION:
                    gestion_hover_souris(event.pos)

            dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
            dessiner_murs(fenetre)
            pygame.display.flip()
    except ReturnToMenu:  # NEW
        return

def mainAIvsAI(difficulte_ia1=None, difficulte_ia2=None):
    global current_game_mode, current_difficulty, murs, mur_preview
    if difficulte_ia1 is None:
        difficulte_ia1 = current_difficulty
    if difficulte_ia2 is None:
        difficulte_ia2 = current_difficulty
    current_game_mode = 'AIvsAI'

    # Initialisation identique à simulate_ai_vs_ai
    grille = creer_grille()
    murs.clear()  # S'assurer que la liste de murs est vide au début
    tour_joueur = 1
    murs_restants_j1 = 10
    murs_restants_j2 = 10
    max_tours = 200
    tour = 0
    joueur_selectionne = None
    possible_moves = []

    try:
        while True:
            # Gestion des évènements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        raise ReturnToMenu()

            # Affichage de l'état actuel
            dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
            dessiner_murs(fenetre)

            # Affichage des informations
            mur_font = pygame.font.Font('NovaSquare-Regular.ttf', 20)
            draw_text(f"Tour: {tour}", mur_font, BLANC, fenetre, LARGEUR // 2, 20)
            draw_text(f"Murs IA1: {murs_restants_j1}", mur_font, BLANC, fenetre, LARGEUR - 100, 20)
            draw_text(f"Murs IA2: {murs_restants_j2}", mur_font, BLANC, fenetre, LARGEUR - 100, 50)
            draw_text("Appuyez sur ESC pour revenir au menu", mur_font, BLANC, fenetre, LARGEUR // 2, HAUTEUR - 20)

            pygame.display.flip()
            pygame.time.wait(500)  # Délai pour visualiser l'état actuel

            # Vérification de fin de partie
            tour += 1
            if tour > max_tours:
                draw_text("Match nul - Nombre maximum de tours atteint", mur_font, BLANC, fenetre, LARGEUR // 2, HAUTEUR // 2)
                pygame.display.flip()
                pygame.time.wait(2000)
                return

            # Vérification victoire immédiate
            pos_j1 = find_player_position(grille, 1)
            pos_j2 = find_player_position(grille, 2)
            
            if pos_j1 and pos_j1[0] == 8:  # Joueur 1 a gagné
                show_winner(1)
                return
            if pos_j2 and pos_j2[0] == 0:  # Joueur 2 a gagné
                show_winner(2)
                return

            # Mise en évidence du joueur actuel et de ses mouvements possibles
            if tour_joueur == 1:
                joueur_selectionne = pos_j1
                possible_moves = get_possible_moves(pos_j1[0], pos_j1[1], 1, grille) if pos_j1 else []
            else:
                joueur_selectionne = pos_j2
                possible_moves = get_possible_moves(pos_j2[0], pos_j2[1], 2, grille) if pos_j2 else []

            # Affichage des possibilités
            dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
            dessiner_murs(fenetre)
            pygame.display.flip()
            pygame.time.wait(700)  # Délai pour visualiser les possibilités

            # Tour du joueur actuel avec la fonction unifiée
            if tour_joueur == 1:
                coup, type_coup = meilleur_coup_ia(
                    grille, murs, murs_restants_j1, murs_restants_j2, difficulte_ia1, 1
                )
                
                # Fallback si pas de coup valide
                if not coup or not type_coup:
                    coup = random.choice(get_possible_moves(pos_j1[0], pos_j1[1], 1, grille))
                    type_coup = "deplacement"

                # Application du coup avec visualisation
                if type_coup == "deplacement":
                    ni, nj = coup
                    if pos_j1:
                        grille[pos_j1[0]][pos_j1[1]] = 0
                        grille[ni][nj] = 1
                elif type_coup == "mur" and murs_restants_j1 > 0:
                    # Prévisualisation du mur
                    mur_preview = coup
                    dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
                    dessiner_murs(fenetre)
                    pygame.display.flip()
                    pygame.time.wait(500)
                    
                    if mur_est_valide(coup) and coup not in murs:
                        murs.append(coup)
                        murs_restants_j1 -= 1
                    mur_preview = None

                tour_joueur = 2

            else:
                coup, type_coup = meilleur_coup_ia(
                    grille, murs, murs_restants_j1, murs_restants_j2, difficulte_ia2, 2
                )
                
                # Fallback si pas de coup valide
                if not coup or not type_coup:
                    coup = random.choice(get_possible_moves(pos_j2[0], pos_j2[1], 2, grille))
                    type_coup = "deplacement"

                # Application du coup avec visualisation
                if type_coup == "deplacement":
                    ni, nj = coup
                    if pos_j2:
                        grille[pos_j2[0]][pos_j2[1]] = 0
                        grille[ni][nj] = 2
                elif type_coup == "mur" and murs_restants_j2 > 0:
                    # Prévisualisation du mur
                    mur_preview = coup
                    dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
                    dessiner_murs(fenetre)
                    pygame.display.flip()
                    pygame.time.wait(500)
                    
                    if mur_est_valide(coup) and coup not in murs:
                        murs.append(coup)
                        murs_restants_j2 -= 1
                    mur_preview = None

                tour_joueur = 1

    except ReturnToMenu:
        return

def difficulty_menu():
    button_width = 450
    button_height = 80
    button_spacing = 40
    total_height = button_height * 3 + button_spacing * 2 + 100

    try:  # NEW
        while True:
            fenetre.fill(FOND)
            draw_text("Difficulté :", font_title, BUTTON_COLOR, fenetre, LARGEUR // 2, 100)

            start_y = (HAUTEUR - total_height) // 2 + 100
            draw_button(fenetre, "Facile", (LARGEUR - button_width) // 2, start_y,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: set_difficulty(1))  # MODIFIED

            draw_button(fenetre, "Intermédiaire", (LARGEUR - button_width) // 2, start_y + button_height + button_spacing,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: set_difficulty(3))  # MODIFIED

            draw_button(fenetre, "Difficile", (LARGEUR - button_width) // 2, start_y + (button_height + button_spacing)*2,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: set_difficulty(5))  # MODIFIED

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
    except ReturnToMenu:  # NEW
        return

def set_difficulty(diff):  # NEW
    global current_difficulty
    current_difficulty = diff
    mainPVE(diff)

def restart_game(was_pve_mode=False):
    global murs
    murs = []
    if was_pve_mode:
        mainPVE(current_difficulty)  # MODIFIED
    else:
        mainPVP()

def ai_vs_ai_difficulty_menu():
    button_width = 450
    button_height = 80
    button_spacing = 40

    # Utiliser un dictionnaire pour stocker les valeurs modifiables
    state = {
        "difficulte_ia1": 2,
        "difficulte_ia2": 2,
        "selection_en_cours": "IA1"
    }

    try:
        while True:
            fenetre.fill(FOND)

            if state["selection_en_cours"] == "IA1":
                draw_text("Difficulté IA1 (rouge) :", font_title, BUTTON_COLOR, fenetre, LARGEUR // 2, 100)
                start_y = 250

                # Boutons pour IA1 avec modification directe du dictionnaire
                draw_button(fenetre, "Facile", (LARGEUR - button_width)//2, start_y,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda: state.update({"difficulte_ia1": 1, "selection_en_cours": "IA2"}))

                draw_button(fenetre, "Intermédiaire", (LARGEUR - button_width)//2, start_y + button_height + button_spacing,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda: state.update({"difficulte_ia1": 3, "selection_en_cours": "IA2"}))

                draw_button(fenetre, "Difficile", (LARGEUR - button_width)//2, start_y + (button_height + button_spacing)*2,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda: state.update({"difficulte_ia1": 5, "selection_en_cours": "IA2"}))

            elif state["selection_en_cours"] == "IA2":
                draw_text("Difficulté IA2 (bleu) :", font_title, BUTTON_COLOR, fenetre, LARGEUR // 2, 100)
                start_y = 250

                # Boutons pour IA2 avec fermeture explicite
                draw_button(fenetre, "Facile", (LARGEUR - button_width)//2, start_y,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda d=1: mainAIvsAI(state["difficulte_ia1"], d))

                draw_button(fenetre, "Intermédiaire", (LARGEUR - button_width)//2, start_y + button_height + button_spacing,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda d=3: mainAIvsAI(state["difficulte_ia1"], d))

                draw_button(fenetre, "Difficile", (LARGEUR - button_width)//2, start_y + (button_height + button_spacing)*2,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda d=5: mainAIvsAI(state["difficulte_ia1"], d))

                # Bouton retour
                draw_button(fenetre, "Retour", (LARGEUR - button_width)//2, start_y + (button_height + button_spacing)*3,
                          button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                          lambda: state.update({"selection_en_cours": "IA1"}))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        raise ReturnToMenu()

            pygame.display.flip()
    except ReturnToMenu:
        return

def batch_ai_menu():
    """Menu de configuration des matchs en batch"""
    button_width = 400
    button_height = 60
    state = {
        "ia1_diff": 1,
        "ia2_diff": 1,
        "num_matches": 100,
        "current_selection": "IA1"
    }

    # Définition des difficultés avec leur valeur réelle et leur nom
    difficulty_options = [
        {"value": 1, "name": "Facile"},
        {"value": 3, "name": "Intermédiaire"},
        {"value": 5, "name": "Difficile"}
    ]

    try:
        while True:
            fenetre.fill(FOND)
            draw_text("BATCH IA vs IA", font_title, BUTTON_COLOR, fenetre, LARGEUR//2, 100)

            # Sélection difficulté IA1
            y = 200
            draw_text("IA 1 (Rouge):", font_button, BLANC, fenetre, LARGEUR//2 - 200, y)
            for i, diff in enumerate(difficulty_options):
                x = LARGEUR//2 - 150 + i*130
                selected = state["ia1_diff"] == diff["value"]
                draw_button(fenetre, diff["name"], x, y, 
                          120, 40, BUTTON_COLOR if not selected else (0,200,0), BUTTON_HOVER_COLOR,
                          lambda d=diff["value"]: state.update({"ia1_diff": d}))

            # Sélection difficulté IA2
            y += 80
            draw_text("IA 2 (Bleu):", font_button, BLANC, fenetre, LARGEUR//2 - 200, y)
            for i, diff in enumerate(difficulty_options):
                x = LARGEUR//2 - 150 + i*130
                selected = state["ia2_diff"] == diff["value"]
                draw_button(fenetre, diff["name"], x, y, 
                          120, 40, BUTTON_COLOR if not selected else (0,200,0), BUTTON_HOVER_COLOR,
                          lambda d=diff["value"]: state.update({"ia2_diff": d}))

            # Nombre de matchs
            y += 100
            draw_text(f"Nombre de matchs: {state['num_matches']}", font_button, BLANC, fenetre, LARGEUR//2, y)
            draw_button(fenetre, "-", LARGEUR//2 - 100, y + 40, 50, 40, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: state.update({"num_matches": max(1, state["num_matches"]-1)}))
            draw_button(fenetre, "+", LARGEUR//2 + 50, y + 40, 50, 40, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                       lambda: state.update({"num_matches": state["num_matches"]+1}))

            # Bouton de lancement
            draw_button(fenetre, "LANCER", LARGEUR//2 - 100, HAUTEUR - 100, 200, 60, 
                      (0, 150, 0), (0, 200, 0), 
                      lambda: run_batch_simulations(state["ia1_diff"], state["ia2_diff"], state["num_matches"]))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    raise ReturnToMenu()

            pygame.display.flip()
    except ReturnToMenu:
        return

def main_menu():
    button_width = 450
    button_height = 80
    button_spacing = 40
    total_height = button_height * 4 + button_spacing * 3 + 150  # Ajusté pour 4 boutons

    try:
        while True:
            fenetre.fill(FOND)
            draw_text("QUORRIDOR", font_title, BUTTON_COLOR, fenetre, LARGEUR // 2, 250)

            start_y = (HAUTEUR - total_height) // 2 + 150
            draw_button(fenetre, "Joueur Vs Joueur", (LARGEUR - button_width) // 2, start_y,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, mainPVP)

            draw_button(fenetre, "Joueur Vs IA", (LARGEUR - button_width) // 2, start_y + button_height + button_spacing,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, difficulty_menu)

            # Nouveau bouton pour IA vs IA
            draw_button(fenetre, "IA Vs IA", (LARGEUR - button_width) // 2, start_y + (button_height + button_spacing)*2,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, ai_vs_ai_difficulty_menu)

            # Nouveau bouton pour Batch IA vs IA
            draw_button(fenetre, "Batch IA vs IA", (LARGEUR - button_width)//2, start_y + (button_height + button_spacing)*3,
                       button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, batch_ai_menu)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
    except ReturnToMenu:
        main_menu()

def count_chemins_alternatifs(pos, target_row, walls, max_depth=10):
    """
    Compte le nombre de chemins alternatifs proches du chemin optimal
    Utilise une profondeur limitée pour l'efficacité
    """
    if pos is None:
        return 0

    # Trouve d'abord le chemin le plus court avec A*
    dist, chemin_optimal = a_star_search(pos, target_row, walls)
    if dist == float('inf'):
        return 0

    # Compte les chemins alternatifs
    chemins_distincts = set()
    chemins_distincts.add(tuple(chemin_optimal))

    # Points d'embranchement possibles du chemin optimal
    for i in range(len(chemin_optimal) - 1):
        point = chemin_optimal[i]

        # Recherche de chemins alternatifs depuis ce point
        visited = set([point])
        queue = deque([(point, [point], 0)])  # (position, chemin, profondeur)

        while queue:
            current, path, depth = queue.popleft()

            if depth > max_depth:
                continue

            # Si nous avons rejoint le chemin optimal plus loin
            if current in chemin_optimal[i+1:]:
                nouveau_chemin = tuple(chemin_optimal[:i] + path + chemin_optimal[chemin_optimal.index(current)+1:])
                if len(nouveau_chemin) <= dist + 2:  # Seulement les chemins courts
                    chemins_distincts.add(nouveau_chemin)
                continue

            # Explorer les voisins
            c_i, c_j = current
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for di, dj in directions:
                ni, nj = c_i + di, c_j + dj
                neighbor = (ni, nj)

                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE:
                    if not mur_bloque_mouvement(c_i, c_j, ni, nj, walls):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor], depth + 1))

    # Retourne le nombre de chemins distincts trouvés
    return len(chemins_distincts)

def simulate_ai_vs_ai(difficulte_ia1, difficulte_ia2):
    """Simulation complète sans interface graphique"""
    grille = creer_grille()
    murs_locaux = []  # Utiliser une liste de murs locale
    tour_joueur = 1
    murs_restants_j1 = 10
    murs_restants_j2 = 10
    max_tours = 200  # Sécurité contre les boucles infinies
    tour = 0

    while True:
        tour += 1
        if tour > max_tours:
            return 0  # Match nul après 200 tours

        # Vérification victoire immédiate
        pos_j1 = find_player_position(grille, 1)
        pos_j2 = find_player_position(grille, 2)
        
        if pos_j1 is None or pos_j2 is None:
            return 0  # En cas d'erreur, considérer comme match nul
            
        if pos_j1[0] == 8:  # Joueur 1 a gagné
            return 1
        if pos_j2[0] == 0:  # Joueur 2 a gagné
            return 2

        try:
            # Tour du joueur actuel
            if tour_joueur == 1:
                # S'assurer que get_possible_moves ne retourne pas une liste vide
                moves = get_possible_moves(pos_j1[0], pos_j1[1], 1, grille)
                if not moves:
                    return 0  # Match nul si aucun mouvement possible
                    
                coup, type_coup = meilleur_coup_ia(
                    grille, murs_locaux, murs_restants_j1, murs_restants_j2, difficulte_ia1, 1
                )
                
                # Fallback si pas de coup valide
                if not coup or not type_coup:
                    if not moves:
                        return 0  # Match nul si aucun mouvement possible
                    coup = random.choice(moves)
                    type_coup = "deplacement"

                # Application du coup
                if type_coup == "deplacement":
                    ni, nj = coup
                    grille[pos_j1[0]][pos_j1[1]] = 0
                    grille[ni][nj] = 1
                elif type_coup == "mur" and murs_restants_j1 > 0:
                    if mur_est_valide(coup) and coup not in murs_locaux:
                        murs_locaux.append(coup)
                        murs_restants_j1 -= 1

                tour_joueur = 2

            else:
                # S'assurer que get_possible_moves ne retourne pas une liste vide
                moves = get_possible_moves(pos_j2[0], pos_j2[1], 2, grille)
                if not moves:
                    return 0  # Match nul si aucun mouvement possible
                
                # Même logique pour le joueur 2
                coup, type_coup = meilleur_coup_ia(
                    grille, murs_locaux, murs_restants_j1, murs_restants_j2, difficulte_ia2, 2
                )
                
                # Fallback si pas de coup valide
                if not coup or not type_coup:
                    if not moves:
                        return 0  # Match nul si aucun mouvement possible
                    coup = random.choice(moves)
                    type_coup = "deplacement"

                if type_coup == "deplacement":
                    ni, nj = coup
                    grille[pos_j2[0]][pos_j2[1]] = 0
                    grille[ni][nj] = 2
                elif type_coup == "mur" and murs_restants_j2 > 0:
                    if mur_est_valide(coup) and coup not in murs_locaux:
                        murs_locaux.append(coup)
                        murs_restants_j2 -= 1

                tour_joueur = 1

        except Exception as e:
            print(f"Erreur durant la simulation: {str(e)}")
            return 0  # Match nul en cas d'erreur

def run_batch_simulations(difficulte_ia1, difficulte_ia2, num_matches):
    """Exécute une série de matchs et affiche les résultats dans la console"""
    difficulty_names = {
        1: "Facile",
        3: "Intermédiaire",
        5: "Difficile"
    }
    ia1_name = difficulty_names.get(difficulte_ia1, "Inconnu")
    ia2_name = difficulty_names.get(difficulte_ia2, "Inconnu")
    
    print(f"\nDébut de {num_matches} matchs {ia1_name} vs {ia2_name}...")
    scores = {0: 0, 1: 0, 2: 0}  # Clé 0 pour les matchs nuls
    
    try:
        for match in range(1, num_matches + 1):
            gagnant = simulate_ai_vs_ai(difficulte_ia1, difficulte_ia2)
            # Vérifier que le résultat est valide (0, 1 ou 2)
            if gagnant not in scores:
                print(f"Erreur: résultat invalide {gagnant}, considéré comme match nul")
                gagnant = 0
                
            scores[gagnant] += 1
            if gagnant == 0:
                resultat = "Match nul"
            else:
                resultat = f"{ia1_name if gagnant == 1 else ia2_name} gagne"
            print(f"- Match {match} : {resultat}")

        print("\nRésultats finaux:")
        total = sum(scores.values())
        if total > 0:  # Éviter division par zéro
            print(f"- {ia1_name}: {scores[1]} victoires ({scores[1]/total*100:.1f}%)")
            print(f"- {ia2_name}: {scores[2]} victoires ({scores[2]/total*100:.1f}%)")
            print(f"- Matchs nuls: {scores[0]} ({scores[0]/total*100:.1f}%)")
        else:
            print("Aucun match n'a été complété avec succès.")
        print("----------------------------------")
    except Exception as e:
        print(f"Erreur pendant les simulations: {str(e)}")

if __name__ == "__main__":
    main_menu()
