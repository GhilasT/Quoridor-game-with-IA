import sys
import pygame

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
murs = [
    # {'x': 2, 'y': 3, 'orientation': 'H'},  #Exemple Mur horizontal entre les cases
    # {'x': 5, 'y': 4, 'orientation': 'V'},  #Exemple Mur vertical entre les cases
]
mur_preview = None

def dessiner_murs(surface):
    for mur in murs:
        if mur['orientation'] == 'H':
            # Calcul horizontal avec marges et espacements
            x = MARGE + mur['x'] * (TAILLE_CASE + ESPACEMENT)
            y = MARGE + (mur['y'] + 1) * (TAILLE_CASE + ESPACEMENT) - ESPACEMENT
            largeur = 2 * TAILLE_CASE + ESPACEMENT
            hauteur = ESPACEMENT
        else:
            # Calcul vertical avec marges et espacements
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
        
def mur_est_valide(mur):
    if mur['orientation'] == 'H':
        return (0 <= mur['x'] <= GRID_SIZE-2 and 
                0 <= mur['y'] <= GRID_SIZE-2)
    else:
        return (0 <= mur['x'] <= GRID_SIZE-2 and 
                0 <= mur['y'] <= GRID_SIZE-2)

def gestion_clic_souris(pos_souris):
    # Cordonnées de la grille sans les marges
    x_relatif = pos_souris[0] - MARGE
    y_relatif = pos_souris[1] - MARGE

    # Verifier si le clic est dans la grille
    if x_relatif < 0 or y_relatif < 0:
        return
    if x_relatif > GRID_SIZE*(TAILLE_CASE + ESPACEMENT) - ESPACEMENT:
        return
    if y_relatif > GRID_SIZE*(TAILLE_CASE + ESPACEMENT) - ESPACEMENT:
        return

    # Calculer la case
    case_x = x_relatif // (TAILLE_CASE + ESPACEMENT)
    case_y = y_relatif // (TAILLE_CASE + ESPACEMENT)
    case_x = min(case_x, GRID_SIZE-2)
    case_y = min(case_y, GRID_SIZE-2)
    
    #caculer l'offset
    offset_x = x_relatif % (TAILLE_CASE + ESPACEMENT)
    offset_y = y_relatif % (TAILLE_CASE + ESPACEMENT)

    
    # Détecter l'orientation
    seuil = 10  # Seuil de détection
    if abs(offset_y - (TAILLE_CASE + ESPACEMENT)) < seuil:
        murs.append({'x': case_x, 'y': case_y, 'orientation': 'H'})
    elif abs(offset_x - (TAILLE_CASE + ESPACEMENT)) < seuil:
        murs.append({'x': case_x, 'y': case_y, 'orientation': 'V'})
        
    nouveau_mur = None
    if abs(offset_y - (TAILLE_CASE + ESPACEMENT)) < seuil:
        nouveau_mur = {'x': case_x, 'y': case_y, 'orientation': 'H'}
    elif abs(offset_x - (TAILLE_CASE + ESPACEMENT)) < seuil:
        nouveau_mur = {'x': case_x, 'y': case_y, 'orientation': 'V'}

    if nouveau_mur: 
        if mur_est_valide(nouveau_mur) and nouveau_mur not in murs:
            murs.append(nouveau_mur)

# Réutiliser du code de la fonction de gestion du clic pour gérer le survol de la souris    
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
    # Initialiser une grille 9x9 avec des valeurs par défaut
    # 0 pour une cellule vide
    # 1 pour le joueur 1
    # 2 pour le joueur 2
    grille = [[0 for _ in range(9)] for _ in range(9)]
    
    grille[0][4] = 1
    grille[8][4] = 2
    return grille

def dessiner_grille(fenetre, grille):
    fenetre.fill(FOND)
    for x in range(9):
        for y in range(9):
            rect = pygame.Rect(x * (TAILLE_CASE + ESPACEMENT) + MARGE, y * (TAILLE_CASE + ESPACEMENT) + MARGE, TAILLE_CASE, TAILLE_CASE)
            pygame.draw.rect(fenetre, CASE, rect)
    
    for i in range(9):
        for j in range(9):
            if grille[i][j] == 1:
                pygame.draw.circle(fenetre, JOUEUR1, (j * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE // 2, i * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE // 2), TAILLE_CASE // 3)
            elif grille[i][j] == 2:
                pygame.draw.circle(fenetre, JOUEUR2, (j * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE // 2, i * (TAILLE_CASE + ESPACEMENT) + MARGE + TAILLE_CASE // 2), TAILLE_CASE // 3)

# Boucle principale
def main():
    grille = creer_grille()
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
                gestion_clic_souris(event.pos)
        
        if event.type == pygame.MOUSEMOTION:
                gestion_hover_souris(event.pos)
        
        dessiner_grille(fenetre,grille)
        dessiner_murs(fenetre)
        pygame.display.flip()

if __name__ == "__main__":
    main()