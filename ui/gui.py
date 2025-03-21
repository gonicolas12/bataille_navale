"""
Interface graphique pour le jeu de bataille navale.
"""

import tkinter as tk
from tkinter import messagebox, Frame, Button, Label, Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import time
import sys

# Ajout du répertoire racine au chemin Python pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.game_manager import GameManager
from utils.game_statistics import GameStatistics

class BattleshipGUI:
    """Interface graphique pour le jeu de bataille navale."""
    
    def __init__(self, root):
        """
        Initialise l'interface graphique.
        
        Args:
            root (tk.Tk): La fenêtre racine Tkinter
        """
        self.root = root
        self.root.title("Bataille Navale")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Initialiser le jeu
        self.game = GameManager()
        self.game.initialize_game()
        self.game_over = False
        
        # Initialiser les variables d'état
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
        
        # Configurer la fenêtre principale
        self.root.configure(bg=self.colors["background"])
        
        # Créer les frames
        self.create_frames()
        
        # Créer les grilles de jeu
        self.create_boards()
        
        # Créer les indicateurs de statut
        self.create_status_indicators()
        
        # Initialiser les variables d'état
        self.hover_position = None
        self.last_ai_move = None
        
        # Liaison des événements
        self.bind_events()
    
    def create_frames(self):
        """Crée les différents cadres de l'interface."""
        # Frame pour la grille du joueur
        self.player_frame = Frame(self.root, bg=self.colors["background"])
        self.player_frame.place(x=50, y=50, width=400, height=500)
        
        # Frame pour la grille de l'IA
        self.ai_frame = Frame(self.root, bg=self.colors["background"])
        self.ai_frame.place(x=550, y=50, width=400, height=500)
        
        # Frame pour les statistiques
        self.stats_frame = Frame(self.root, bg=self.colors["background"])
        self.stats_frame.place(x=50, y=580, width=900, height=100)
        
        # Frame pour les contrôles
        self.controls_frame = Frame(self.root, bg=self.colors["background"])
        self.controls_frame.place(x=950, y=50, width=200, height=500)
    
    def create_boards(self):
        """Crée les grilles de jeu."""
        # Grille du joueur
        Label(self.player_frame, text="Votre flotte", font=("Arial", 16), bg=self.colors["background"], fg="white").pack(pady=(0, 10))
        self.player_canvas = Canvas(self.player_frame, width=400, height=400, bg=self.colors["background"], highlightthickness=0)
        self.player_canvas.pack()
        
        # Grille de l'IA
        Label(self.ai_frame, text="Flotte ennemie", font=("Arial", 16), bg=self.colors["background"], fg="white").pack(pady=(0, 10))
        self.ai_canvas = Canvas(self.ai_frame, width=400, height=400, bg=self.colors["background"], highlightthickness=0)
        self.ai_canvas.pack()
        
        # Dessiner les grilles
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        self.draw_grid(self.ai_canvas, self.game.ai_board, show_ships=False)
    
    def draw_grid(self, canvas, board, show_ships=False):
        """
        Dessine une grille de jeu sur le canvas donné.
        
        Args:
            canvas (tk.Canvas): Le canvas sur lequel dessiner
            board (Board): La grille de jeu à représenter
            show_ships (bool, optional): Si True, affiche les navires. Par défaut False.
        """
        canvas.delete("all")  # Effacer le canvas
        
        cell_size = 35
        margin = 25
        
        # Dessiner les labels des colonnes (A-J)
        for i in range(10):
            canvas.create_text(
                margin + i * cell_size + cell_size // 2,
                margin // 2,
                text=chr(65 + i),
                font=("Arial", 10),
                fill="white"
            )
        
        # Dessiner les labels des lignes (1-10)
        for i in range(10):
            canvas.create_text(
                margin // 2,
                margin + i * cell_size + cell_size // 2,
                text=str(i + 1),
                font=("Arial", 10),
                fill="white"
            )
        
        # Dessiner la grille
        for i in range(10):
            for j in range(10):
                x1 = margin + j * cell_size
                y1 = margin + i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Déterminer la couleur de la cellule
                cell_value = board.grid[i][j]
                fill_color = self.colors["grid"]
                
                if cell_value == 1 and show_ships:  # Navire
                    fill_color = self.colors["ship"]
                elif cell_value == 2:  # Navire touché
                    fill_color = self.colors["hit"]
                elif cell_value == -1:  # Tir dans l'eau
                    fill_color = self.colors["miss"]
                
                # Si c'est la position survolée
                if self.hover_position == (i, j) and not self.game_over and canvas == self.ai_canvas:
                    fill_color = self.colors["hover"]
                
                # Si c'est le dernier coup de l'IA
                if self.last_ai_move == (i, j) and canvas == self.player_canvas:
                    canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="white")
                    canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
                    canvas.create_line(x1, y2, x2, y1, fill="black", width=2)
                else:
                    canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="white")
                
                # Si un navire est coulé, on l'affiche différemment
                if show_ships:
                    for ship in board.ships:
                        if ship.is_sunk():
                            for pos in ship.positions:
                                px, py = pos
                                if (i, j) == (px, py):
                                    sx1 = margin + j * cell_size
                                    sy1 = margin + i * cell_size
                                    sx2 = sx1 + cell_size
                                    sy2 = sy1 + cell_size
                                    canvas.create_rectangle(sx1, sy1, sx2, sy2, fill=self.colors["sunk"], outline="white")
    
    def create_status_indicators(self):
        """Crée les indicateurs de statut."""
        # Label de statut
        self.status_label = Label(
            self.stats_frame,
            text="Cliquez sur la grille ennemie pour commencer le jeu",
            font=("Arial", 12),
            bg=self.colors["background"],
            fg="white"
        )
        self.status_label.pack(pady=10)
        
        # Statistiques de la partie en cours
        self.stats_label = Label(
            self.stats_frame,
            text="Navires restants - Joueur: 5 | IA: 5",
            font=("Arial", 12),
            bg=self.colors["background"],
            fg="white"
        )
        self.stats_label.pack(pady=5)
        
        # Boutons dans le panneau de contrôle
        Label(
            self.controls_frame,
            text="Contrôles",
            font=("Arial", 14, "bold"),
            bg=self.colors["background"],
            fg="white"
        ).pack(pady=(0, 20))
        
        # Bouton pour commencer une nouvelle partie
        Button(
            self.controls_frame,
            text="Nouvelle Partie",
            font=("Arial", 12),
            bg="#2ecc71",
            fg="white",
            command=self.new_game
        ).pack(pady=10, fill=tk.X, padx=20)
        
        # Bouton pour voir les statistiques
        Button(
            self.controls_frame,
            text="Voir les Statistiques",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            command=self.show_statistics
        ).pack(pady=10, fill=tk.X, padx=20)
        
        # Bouton pour quitter
        Button(
            self.controls_frame,
            text="Quitter",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            command=self.root.quit
        ).pack(pady=10, fill=tk.X, padx=20)
    
    def bind_events(self):
        """Liaison des événements."""
        # Liaison des événements pour la grille de l'IA
        self.ai_canvas.bind("<Motion>", self.on_ai_grid_hover)
        self.ai_canvas.bind("<Button-1>", self.on_ai_grid_click)
        self.ai_canvas.bind("<Leave>", self.on_ai_grid_leave)
    
    def on_ai_grid_hover(self, event):
        """
        Gère le survol de la grille ennemie.
        
        Args:
            event (tk.Event): L'événement de survol
        """
        if self.game_over:
            return
        
        # Calculer la cellule survolée
        cell_size = 35
        margin = 25
        
        i = (event.y - margin) // cell_size
        j = (event.x - margin) // cell_size
        
        if 0 <= i < 10 and 0 <= j < 10:
            # Vérifier si la cellule a déjà été ciblée
            if (i, j) not in self.game.ai_board.shots:
                self.hover_position = (i, j)
                self.draw_grid(self.ai_canvas, self.game.ai_board)
    
    def on_ai_grid_leave(self, event):
        """
        Gère la sortie de la souris de la grille ennemie.
        
        Args:
            event (tk.Event): L'événement de sortie
        """
        self.hover_position = None
        self.draw_grid(self.ai_canvas, self.game.ai_board)
    
    def on_ai_grid_click(self, event):
        """
        Gère le clic sur la grille ennemie.
        
        Args:
            event (tk.Event): L'événement de clic
        """
        if self.game_over:
            return
        
        # Calculer la cellule cliquée
        cell_size = 35
        margin = 25
        
        i = (event.y - margin) // cell_size
        j = (event.x - margin) // cell_size
        
        if 0 <= i < 10 and 0 <= j < 10:
            position = (i, j)
            
            # Vérifier si la cellule a déjà été ciblée
            if position in self.game.ai_board.shots:
                self.status_label.config(text="Vous avez déjà tiré à cette position !")
                return
            
            # Effectuer le tir du joueur
            result = self.game.player_turn(position)
            
            # Mettre à jour l'affichage
            self.draw_grid(self.ai_canvas, self.game.ai_board)
            
            # Afficher le résultat
            if result == "miss":
                self.status_label.config(text="Raté !")
            elif result == "hit":
                self.status_label.config(text="Touché !")
            elif result[0] == "sunk":
                self.status_label.config(text=f"Coulé ! Vous avez coulé le {result[1]} !")
            
            # Mettre à jour les statistiques
            self.update_stats()
            
            # Vérifier si le jeu est terminé
            if self.game.is_game_over():
                self.end_game()
                return
            
            # Tour de l'IA
            self.root.after(1000, self.ai_turn)
    
    def ai_turn(self):
        """Gère le tour de l'IA."""
        # Afficher que l'IA réfléchit
        self.status_label.config(text="L'IA réfléchit...")
        self.root.update()
        
        # Simuler un temps de réflexion
        time.sleep(0.5)
        
        # L'IA joue son coup
        ai_position, ai_result = self.game.ai_turn()
        self.last_ai_move = ai_position
        
        # Mettre à jour l'affichage
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        
        # Afficher le résultat
        x, y = ai_position
        coord_letter = chr(65 + y)
        if ai_result == "miss":
            self.status_label.config(text=f"L'IA tire en {coord_letter}{x+1} et rate !")
        elif ai_result == "hit":
            self.status_label.config(text=f"L'IA tire en {coord_letter}{x+1} et touche un de vos navires !")
        elif ai_result[0] == "sunk":
            self.status_label.config(text=f"L'IA tire en {coord_letter}{x+1} et coule votre {ai_result[1]} !")
        
        # Mettre à jour les statistiques
        self.update_stats()
        
        # Vérifier si le jeu est terminé
        if self.game.is_game_over():
            self.end_game()
    
    def update_stats(self):
        """Met à jour les statistiques affichées."""
        player_ships_left = sum(1 for ship in self.game.player_board.ships if not ship.is_sunk())
        ai_ships_left = sum(1 for ship in self.game.ai_board.ships if not ship.is_sunk())
        
        self.stats_label.config(text=f"Navires restants - Joueur: {player_ships_left} | IA: {ai_ships_left}")
    
    def end_game(self):
        """Termine la partie et affiche le résultat."""
        self.game_over = True
        
        winner = self.game.get_winner()
        if winner == "player":
            self.status_label.config(text="Félicitations ! Vous avez gagné !")
            messagebox.showinfo("Fin de partie", "Félicitations ! Vous avez coulé tous les navires ennemis !")
        else:
            self.status_label.config(text="L'IA a gagné. Meilleure chance la prochaine fois !")
            messagebox.showinfo("Fin de partie", "L'IA a coulé tous vos navires. Meilleure chance la prochaine fois !")
        
        # Afficher les deux grilles avec tous les navires visibles
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        self.draw_grid(self.ai_canvas, self.game.ai_board, show_ships=True)
    
    def new_game(self):
        """Commence une nouvelle partie."""
        self.game = GameManager()
        self.game.initialize_game()
        self.game_over = False
        self.last_ai_move = None
        
        # Réinitialiser l'affichage
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        self.draw_grid(self.ai_canvas, self.game.ai_board, show_ships=False)
        
        self.status_label.config(text="Cliquez sur la grille ennemie pour commencer le jeu")
        self.update_stats()
    
    def show_statistics(self):
        """Affiche une fenêtre avec les statistiques de jeu."""
        # Utiliser la classe StatisticsView pour afficher les statistiques
        from utils.game_statistics import GameStatistics
        from ui.statistics_view import StatisticsView
        
        # Créer un dictionnaire de couleurs compatible avec StatisticsView
        colors = {
            "background": self.colors["background"],
            "text": "white",  # Ajouter cette clé manquante
            "button_success": "#2ecc71",
            "button_info": "#3498db",
            "button_danger": "#e74c3c"
        }
        
        stats_manager = GameStatistics()
        stats_view = StatisticsView(self.root, stats_manager, colors)
        stats_view.show_statistics_window()