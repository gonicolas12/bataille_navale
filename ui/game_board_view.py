"""
Module pour l'affichage des grilles de jeu dans l'interface graphique.
"""

import tkinter as tk

class GameBoardView:
    """Classe pour l'affichage et la gestion des grilles de jeu."""
    
    def __init__(self, canvas, board, cell_size=35, margin=25, show_ships=False, is_player_board=True):
        """
        Initialise une vue de grille de jeu.
        
        Args:
            canvas (tk.Canvas): Le canvas sur lequel dessiner
            board (Board): La grille de jeu à représenter
            cell_size (int, optional): Taille d'une cellule en pixels. Par défaut 35.
            margin (int, optional): Marge autour de la grille en pixels. Par défaut 25.
            show_ships (bool, optional): Si True, affiche les navires. Par défaut False.
            is_player_board (bool, optional): Si True, c'est la grille du joueur. Par défaut True.
        """
        self.canvas = canvas
        self.board = board
        self.cell_size = cell_size
        self.margin = margin
        self.show_ships = show_ships
        self.is_player_board = is_player_board
        self.hover_position = None
        self.last_ai_move = None
        
        # Couleurs
        self.colors = {
            "background": "#3a4f6a",
            "grid": "#cad8e6",
            "ship": "#2c3e50",
            "hit": "#e74c3c",
            "miss": "#3498db",
            "sunk": "#c0392b",
            "hover": "#f1c40f"
        }
    
    def draw(self):
        """Dessine la grille sur le canvas."""
        self.canvas.delete("all")  # Effacer le canvas
        
        # Dessiner les labels des colonnes (A-J)
        for i in range(10):
            self.canvas.create_text(
                self.margin + i * self.cell_size + self.cell_size // 2,
                self.margin // 2,
                text=chr(65 + i),
                font=("Arial", 10),
                fill="white"
            )
        
        # Dessiner les labels des lignes (1-10)
        for i in range(10):
            self.canvas.create_text(
                self.margin // 2,
                self.margin + i * self.cell_size + self.cell_size // 2,
                text=str(i + 1),
                font=("Arial", 10),
                fill="white"
            )
        
        # Dessiner la grille
        for i in range(10):
            for j in range(10):
                x1 = self.margin + j * self.cell_size
                y1 = self.margin + i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Déterminer la couleur de la cellule
                cell_value = self.board.grid[i][j]
                fill_color = self.colors["grid"]
                
                if cell_value == 1 and self.show_ships:  # Navire
                    fill_color = self.colors["ship"]
                elif cell_value == 2:  # Navire touché
                    fill_color = self.colors["hit"]
                elif cell_value == -1:  # Tir dans l'eau
                    fill_color = self.colors["miss"]
                
                # Si c'est la position survolée
                if self.hover_position == (i, j) and not self.is_player_board:
                    fill_color = self.colors["hover"]
                
                # Si c'est le dernier coup de l'IA
                if self.last_ai_move == (i, j) and self.is_player_board:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="white")
                    self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
                    self.canvas.create_line(x1, y2, x2, y1, fill="black", width=2)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="white")
                
                # Si un navire est coulé, on l'affiche différemment
                if self.show_ships:
                    for ship in self.board.ships:
                        if ship.is_sunk():
                            for pos in ship.positions:
                                px, py = pos
                                if (i, j) == (px, py):
                                    sx1 = self.margin + j * self.cell_size
                                    sy1 = self.margin + i * self.cell_size
                                    sx2 = sx1 + self.cell_size
                                    sy2 = sy1 + self.cell_size
                                    self.canvas.create_rectangle(sx1, sy1, sx2, sy2, fill=self.colors["sunk"], outline="white")
    
    def set_hover_position(self, position):
        """
        Définit la position survolée.
        
        Args:
            position (tuple ou None): Position (x, y) survolée, ou None si aucune
        """
        self.hover_position = position
        self.draw()
    
    def set_last_ai_move(self, position):
        """
        Définit la dernière position jouée par l'IA.
        
        Args:
            position (tuple ou None): Position (x, y) du dernier coup de l'IA
        """
        self.last_ai_move = position
        self.draw()
    
    def get_cell_from_coords(self, x, y):
        """
        Convertit des coordonnées de pixel en coordonnées de cellule.
        
        Args:
            x (int): Coordonnée X en pixels
            y (int): Coordonnée Y en pixels
            
        Returns:
            tuple ou None: Coordonnées (row, col) de la cellule, ou None si hors grille
        """
        # Convertir les coordonnées en pixels en coordonnées de cellule
        row = (y - self.margin) // self.cell_size
        col = (x - self.margin) // self.cell_size
        
        # Vérifier si les coordonnées sont dans la grille
        if 0 <= row < 10 and 0 <= col < 10:
            return (row, col)
        return None
    
    def highlight_ships(self, show=True):
        """
        Active ou désactive l'affichage des navires.
        
        Args:
            show (bool, optional): Si True, affiche les navires. Par défaut True.
        """
        self.show_ships = show
        self.draw()