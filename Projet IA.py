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
FOND = (64, 36, 18)
CASE = (250, 233, 192)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
JOUEUR1 = (130, 9, 5)
JOUEUR2 = (11, 30, 74)
MUR = (35, 82, 250)
MUR_PREVIEW = (78, 126, 255)
HIGHLIGHT = (173, 216, 230, 100)
CASE_SOMBRE = (200, 183, 142)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (70, 70, 70)
TEXT_COLOR = (255, 255, 255)

# Police
font = pygame.font.SysFont(None, 70)

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

    draw_text(text, font, TEXT_COLOR, surface, x + width // 2, y + height // 2)

def main_menu():
    button_width = 400
    button_height = 80
    button_spacing = 50
    total_height = button_height * 2 + button_spacing

    while True:
        fenetre.fill(FOND)
        draw_text("Quorridor - Menu Principal", font, TEXT_COLOR, fenetre, LARGEUR // 2, 150)

        start_y = (HAUTEUR - total_height) // 2
        draw_button(fenetre, "Jouer Vs Joueur", (LARGEUR - button_width) // 2, start_y, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, mainPVP)
        draw_button(fenetre, "Joueur Vs IA", (LARGEUR - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height, BUTTON_COLOR, BUTTON_HOVER_COLOR, difficulty_menu)

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
