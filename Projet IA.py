import sys
import pygame

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
largeur, hauteur = 900, 900
marge = 50
espacement = 5
taille_case = (largeur - 2*marge - 8*espacement) // 9

# Créer la fenêtre
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Quoridor")

# Constantes de couleurs
FOND = (64, 36, 18)
CASE = (250, 233, 192)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)

def creer_grille():
    # Initialiser une grille 9x9 avec des valeurs par défaut
    # 0 pour une cellule vide
    # 1 pour un mur horizontal
    # 2 pour un mur vertical
    # 3 pour le joueur 1
    # 4 pour le joueur 2
    grille = [[0 for _ in range(9)] for _ in range(9)]
    return grille

def dessiner_grille(fenetre):
    fenetre.fill(FOND)
    for x in range(9):
        for y in range(9):
            rect = pygame.Rect(x * (taille_case + espacement) + marge, y * (taille_case + espacement) + marge, taille_case, taille_case)
            pygame.draw.rect(fenetre, CASE, rect)
    pygame.display.flip()

# Boucle principale
def main():
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
        dessiner_grille(fenetre)


if __name__ == "__main__":
    main()