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
murs = [
    # {'x': 2, 'y': 3, 'orientation': 'H'},  #Exemple Mur horizontal entre les cases
    # {'x': 5, 'y': 4, 'orientation': 'V'},  #Exemple Mur vertical entre les cases
]

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

        dessiner_grille(fenetre,grille)
        dessiner_murs(fenetre)
        pygame.display.flip()

if __name__ == "__main__":
    main()