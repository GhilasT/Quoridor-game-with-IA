import pygame

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
largeur, hauteur = 900, 900
taille_case = (largeur) // 9

# Créer la fenêtre
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Quoridor")


def creer_grille_quoridor():
    # Initialiser une grille 9x9 avec des valeurs par défaut de 0 (pour dire que les cellules sont vide)
    grille = [[0 for _ in range(9)] for _ in range(9)]

# Boucle principale
def main():
    #TODO ajouter un quit event
    while True: 
        ...
    

if __name__ == "__main__":
    main()