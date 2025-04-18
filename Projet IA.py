import sys
import pygame
from collections import deque

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

murs = [
    # {'x': 2, 'y': 3, 'orientation': 'H'},  #Exemple Mur horizontal entre les cases
    # {'x': 5, 'y': 4, 'orientation': 'V'},  #Exemple Mur vertical entre les cases
]
mur_preview = None

def dessiner_murs(surface):
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

def mur_est_valide(mur):
    if not (0 <= mur['x'] <= GRID_SIZE-2 and
            0 <= mur['y'] <= GRID_SIZE-2):
        return False

    for mur_existant in murs:
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
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x <= mouse[0] <= x + width and y <= mouse[1] <= y + height:
        pygame.draw.rect(surface, hover_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(surface, color, (x, y, width, height))

    draw_text(text, font_button, TEXT_COLOR, surface, x + width // 2, y + height // 2)

def show_winner(winner):
    button_width = 300
    button_height = 60
    while True:
        fenetre.fill(FOND)
        draw_text(f"Joueur {winner} gagne !", font_title, BUTTON_COLOR, fenetre, LARGEUR//2, HAUTEUR//2 - 50)
        draw_button(fenetre, "Menu Principal", (LARGEUR - button_width)//2, HAUTEUR//2 + 50, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, main_menu)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

def main_menu():
    button_width = 450  # Réduction de la largeur des boutons
    button_height = 80  # Réduction de la hauteur des boutons
    button_spacing = 40  # Réduction de l'espacement entre les boutons
    total_height = button_height * 2 + button_spacing + 150  # Ajout de 150 pour le texte "QUORRIDOR"

    while True:
        fenetre.fill(FOND)
        draw_text("QUORRIDOR", font_title, BUTTON_COLOR, fenetre, LARGEUR // 2, 250)  # Position ajustée

        start_y = (HAUTEUR - total_height) // 2 + 150  # Ajustement pour centrer les boutons
        draw_button(fenetre, "Jouer Vs Joueur", (LARGEUR - button_width) // 2, start_y, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, mainPVP)
        draw_button(fenetre, "Joueur Vs IA", (LARGEUR - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, difficulty_menu)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

def evaluer_position(grille, murs):
    """Évalue la position actuelle du jeu pour le joueur IA (joueur 2)"""
    pos_j1 = find_player_position(grille, 1)
    pos_j2 = find_player_position(grille, 2)

    if pos_j1 is None or pos_j2 is None:
        return 0

    # Distance jusqu'à l'objectif (ligne 0 pour joueur 2, ligne 8 pour joueur 1)
    distance_j1 = pos_j1[0]  # Distance de joueur 1 à sa ligne d'arrivée (ligne 8)
    distance_j2 = 8 - pos_j2[0]  # Distance de joueur 2 à sa ligne d'arrivée (ligne 0)

    # Plus la distance du joueur 1 est grande, mieux c'est pour l'IA (joueur 2)
    # Plus la distance du joueur 2 est petite, mieux c'est pour l'IA (joueur 2)
    return distance_j1 - 2 * distance_j2

def minimax(grille, murs, profondeur, alpha, beta, est_maximisant, tour_joueur):
    """
    Implémentation de l'algorithme minimax avec élagage alpha-beta
    - est_maximisant: True si c'est au tour du joueur maximisant (IA/joueur 2)
    - tour_joueur: 1 pour joueur humain, 2 pour IA
    """
    # Vérifier si la partie est terminée ou si on a atteint la profondeur maximale
    if profondeur == 0:
        return evaluer_position(grille, murs)

    pos_joueur = find_player_position(grille, tour_joueur)
    if pos_joueur is None:
        return 0

    # Vérifier si un joueur a gagné
    if (tour_joueur == 1 and pos_joueur[0] == 8) or (tour_joueur == 2 and pos_joueur[0] == 0):
        return float('inf') if est_maximisant else float('-inf')

    # Obtenir tous les coups possibles (déplacements)
    i, j = pos_joueur
    coups_possibles = get_possible_moves(i, j, tour_joueur, grille)

    # Si c'est au tour du joueur maximisant (IA/joueur 2)
    if est_maximisant:
        meilleur_score = float('-inf')
        for coup in coups_possibles:
            ni, nj = coup
            # Simuler le coup
            grille_temp = [ligne[:] for ligne in grille]
            grille_temp[i][j] = 0
            grille_temp[ni][nj] = tour_joueur

            # Appel récursif
            prochain_tour = 1 if tour_joueur == 2 else 2
            score = minimax(grille_temp, murs, profondeur - 1, alpha, beta, False, prochain_tour)

            meilleur_score = max(score, meilleur_score)
            alpha = max(alpha, meilleur_score)

            # Élagage
            if beta <= alpha:
                break

        return meilleur_score

    # Si c'est au tour du joueur minimisant (joueur humain)
    else:
        meilleur_score = float('inf')
        for coup in coups_possibles:
            ni, nj = coup
            # Simuler le coup
            grille_temp = [ligne[:] for ligne in grille]
            grille_temp[i][j] = 0
            grille_temp[ni][nj] = tour_joueur

            # Appel récursif
            prochain_tour = 1 if tour_joueur == 2 else 2
            score = minimax(grille_temp, murs, profondeur - 1, alpha, beta, True, prochain_tour)

            meilleur_score = min(score, meilleur_score)
            beta = min(beta, meilleur_score)

            # Élagage
            if beta <= alpha:
                break

        return meilleur_score

def meilleur_coup_ia(grille, murs, profondeur, murs_restants_ia=10):
    """
    Détermine le meilleur coup pour l'IA (joueur 2)
    Peut être un déplacement ou la pose d'un mur
    """
    pos_ia = find_player_position(grille, 2)
    if pos_ia is None:
        return None, None

    i, j = pos_ia
    coups_possibles = get_possible_moves(i, j, 2, grille)
    meilleur_score = float('-inf')
    meilleur_coup = None
    meilleur_type = None

    # Évaluer les déplacements possibles
    for coup in coups_possibles:
        ni, nj = coup
        grille_temp = [ligne[:] for ligne in grille]
        grille_temp[i][j] = 0
        grille_temp[ni][nj] = 2

        score = minimax(grille_temp, murs, profondeur - 1, float('-inf'), float('inf'), False, 1)

        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup = coup
            meilleur_type = "deplacement"

    # Évaluer la pose de murs si l'IA a encore des murs
    if murs_restants_ia > 0:
        for x in range(GRID_SIZE - 1):
            for y in range(GRID_SIZE - 1):
                # Essayer un mur horizontal
                mur_h = {'x': x, 'y': y, 'orientation': 'H'}
                if mur_est_valide(mur_h) and mur_h not in murs:
                    temp_murs = murs.copy()
                    temp_murs.append(mur_h)
                    
                    # Vérifier si le mur ne bloque pas complètement un joueur
                    player1_pos = find_player_position(grille, 1)
                    player2_pos = find_player_position(grille, 2)
                    if (has_path(player1_pos, 8, temp_murs) and 
                        has_path(player2_pos, 0, temp_murs)):
                        
                        score = minimax(grille, temp_murs, profondeur - 1, float('-inf'), float('inf'), False, 1)
                        if score > meilleur_score:
                            meilleur_score = score
                            meilleur_coup = mur_h
                            meilleur_type = "mur"
                
                # Essayer un mur vertical
                mur_v = {'x': x, 'y': y, 'orientation': 'V'}
                if mur_est_valide(mur_v) and mur_v not in murs:
                    temp_murs = murs.copy()
                    temp_murs.append(mur_v)
                    
                    # Vérifier si le mur ne bloque pas complètement un joueur
                    player1_pos = find_player_position(grille, 1)
                    player2_pos = find_player_position(grille, 2)
                    if (has_path(player1_pos, 8, temp_murs) and 
                        has_path(player2_pos, 0, temp_murs)):
                        
                        score = minimax(grille, temp_murs, profondeur - 1, float('-inf'), float('inf'), False, 1)
                        if score > meilleur_score:
                            meilleur_score = score
                            meilleur_coup = mur_v
                            meilleur_type = "mur"

    return meilleur_coup, meilleur_type

def mainPVE(difficulte=2):
    grille = creer_grille()
    tour_joueur = 1
    joueur_selectionne = None
    possible_moves = []

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
                        if gestion_clic_souris(event.pos, grille):
                            possible_moves = []
                            tour_joueur = 2
                        elif i is not None and j is not None and grille[i][j] == tour_joueur:
                            joueur_selectionne = (i, j)
                            possible_moves = get_possible_moves(i, j, tour_joueur, grille)

        if tour_joueur == 2:
            coup = meilleur_coup_ia(grille, murs, difficulte)

            if coup:
                ni, nj = coup
                pos_ia = find_player_position(grille, 2)
                if pos_ia:
                    i, j = pos_ia
                    grille[i][j] = 0
                    grille[ni][nj] = 2

                    # Vérification victoire IA
                    if ni == 0:
                        show_winner(2)
                        return

            tour_joueur = 1

        dessiner_grille(fenetre, grille, joueur_selectionne, possible_moves)
        dessiner_murs(fenetre)
        pygame.display.flip()

def difficulty_menu():
    button_width = 450
    button_height = 80
    button_spacing = 40
    total_height = button_height * 3 + button_spacing * 2 + 100

    while True:
        fenetre.fill(FOND)
        draw_text("Difficulté :", font_title, BUTTON_COLOR, fenetre, LARGEUR // 2, 100)

        start_y = (HAUTEUR - total_height) // 2 + 100
        draw_button(fenetre, "Facile", (LARGEUR - button_width) // 2, start_y, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: mainPVE(2))
        draw_button(fenetre, "Intermédiaire", (LARGEUR - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: mainPVE(4))
        draw_button(fenetre, "Difficile", (LARGEUR - button_width) // 2, start_y + (button_height + button_spacing) * 2, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: mainPVE(6))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

def mainPVP():
    grille = creer_grille()
    tour_joueur = 1
    joueur_selectionne = None
    possible_moves = []

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

if __name__ == "__main__":
    main_menu()
