import pygame

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
largeur, hauteur = 900, 900
taille_case = (largeur) // 9

# Créer la fenêtre
fenetre = pygame.display.set_mode((largeur, hauteur))