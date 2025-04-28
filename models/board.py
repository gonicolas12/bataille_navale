"""
Classe représentant la grille de jeu.
"""

import numpy as np
import random

class Board:
    """Classe représentant la grille de jeu."""
    
    def __init__(self, size=10):
        """
        Initialise une nouvelle grille de jeu.
        
        Args:
            size (int, optional): Taille de la grille. Par défaut 10.
        """
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.ships = []
        self.shots = []  # Liste des coups joués [(x, y), ...]
        
    def add_ship(self, ship):
        """
        Ajoute un navire à la grille.
        
        Args:
            ship (Ship): Le navire à ajouter
        """
        self.ships.append(ship)
        for pos in ship.positions:
            x, y = pos
            self.grid[x][y] = 1  # 1 indique la présence d'un navire
    
    def place_ship_randomly(self, ship):
        """
        Place un navire aléatoirement sur la grille.
        
        Args:
            ship (Ship): Le navire à placer
            
        Returns:
            bool: True si le placement a réussi, False sinon
        """
        placed = False
        attempts = 0
        max_attempts = 100  # Éviter les boucles infinies
        
        while not placed and attempts < max_attempts:
            attempts += 1
            
            # Choisir une orientation (0 = horizontal, 1 = vertical)
            orientation = random.randint(0, 1)
            
            if orientation == 0:  # Horizontal
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - ship.size)
                positions = [(x, y + i) for i in range(ship.size)]
            else:  # Vertical
                x = random.randint(0, self.size - ship.size)
                y = random.randint(0, self.size - 1)
                positions = [(x + i, y) for i in range(ship.size)]
            
            # Vérifier si les positions sont valides (pas de collision avec d'autres navires)
            valid = True
            for pos in positions:
                px, py = pos
                if self.grid[px][py] != 0:
                    valid = False
                    break
            
            if valid:
                ship.place(positions)
                self.add_ship(ship)
                placed = True
                
        return placed
    
    def receive_shot(self, position):
        """
        Reçoit un tir à une position donnée et retourne le résultat.
        
        Args:
            position (tuple): Position (x, y) du tir
            
        Returns:
            str ou tuple: Le résultat du tir ('miss', 'hit', 'already_shot' ou ('sunk', ship_name))
        """
        x, y = position
        
        if position in self.shots:
            return "already_shot"
        
        self.shots.append(position)
        
        # Vérifier si un navire est touché
        for ship in self.ships:
            if ship.hit(position):
                self.grid[x][y] = 2  # 2 indique un navire touché
                if ship.is_sunk():
                    return "sunk", ship.name
                return "hit"
        
        self.grid[x][y] = -1  # -1 indique un tir dans l'eau
        return "miss"
    
    def all_ships_sunk(self):
        """
        Vérifie si tous les navires sont coulés.
        
        Returns:
            bool: True si tous les navires sont coulés, False sinon
        """
        return all(ship.is_sunk() for ship in self.ships)
    
    def get_valid_moves(self):
        """
        Retourne toutes les positions valides pour un tir.
        
        Returns:
            list: Liste de tuples (x, y) représentant les positions valides
        """
        valid_moves = []
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) not in self.shots:
                    valid_moves.append((x, y))
        return valid_moves