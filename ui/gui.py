"""
Interface graphique.
"""

import tkinter as tk
from tkinter import messagebox, Frame, Button, Label, Canvas, PhotoImage, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.styles import Theme
import os
import time
import sys
import random

# Ajout du répertoire racine au chemin Python pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.game_manager import GameManager
from utils.game_statistics import GameStatistics

class BattleshipGUI:
    """Interface graphique pour le jeu."""
    
    def __init__(self, root):
        """
        Initialise l'interface graphique.
        
        Args:
            root (tk.Tk): La fenêtre racine Tkinter
        """
        self.root = root
        self.root.title("Bataille Navale | ⚓ Édition Python ⚓")
        self.root.geometry("1280x800")
        self.root.minsize(1200, 800)  # Taille minimale

        # Mettre la fenêtre en mode plein écran au démarrage
        self.root.state('zoomed')
        
        # Charger les polices personnalisées
        self.load_custom_fonts()
        
        # Initialiser le jeu
        self.game = GameManager()
        self.game.initialize_game()
        self.game_over = False
        
        # Initialiser les variables d'état
        self.hover_position = None
        self.last_ai_move = None
        self.explosion_image = None
        self.splash_image = None
        
        # Animation des résultats
        self.animation_in_progress = False
        self.animation_step = 0
        self.animation_result = None
        self.animation_position = None

        # Variable pour contrôler les tours
        self.player_turn_active = True

        # Palette de couleurs (OCEAN_DEEP, MODERN_NAVY, PIRATE, RETRO)
        self.colors = Theme.get_theme("OCEAN_DEEP")
        
        # Configurer la fenêtre principale
        self.root.configure(bg=self.colors["background"])
        
        self.create_frames()
        self.create_boards()
        self.create_status_indicators()
        self.create_animated_title()
        
        # Liaison des événements
        self.bind_events()
    
    def load_custom_fonts(self):
        """Charge les polices personnalisées si disponibles, sinon utilise des alternatives système."""
        # Liste des polices à essayer dans l'ordre de préférence
        title_fonts = ["Montserrat", "Verdana", "Arial", "Helvetica"]
        text_fonts = ["Roboto", "Segoe UI", "Tahoma", "Arial"]
        
        # Trouver la première police disponible pour les titres
        self.title_font = None
        for font_name in title_fonts:
            if font_name.lower() in [f.lower() for f in font.families()]:
                self.title_font = font_name
                break
        if not self.title_font:
            self.title_font = "TkDefaultFont"  # Police par défaut si aucune n'est disponible
        
        # Trouver la première police disponible pour le texte
        self.text_font = None
        for font_name in text_fonts:
            if font_name.lower() in [f.lower() for f in font.families()]:
                self.text_font = font_name
                break
        if not self.text_font:
            self.text_font = "TkDefaultFont"  # Police par défaut si aucune n'est disponible
    
    def create_animated_title(self):
        """Crée un titre animé pour le jeu."""
        self.title_label = Label(
            self.root,
            text="⚓ BATAILLE NAVALE ⚓",
            font=(self.title_font, 24, "bold"),
            bg=self.colors["background"],
            fg=self.colors["title"]
        )
        self.title_label.place(relx=0.5, y=18, anchor="n")
        
        # Animation du titre (changement de couleur)
        self.animate_title()
    
    def animate_title(self):
        """Anime le titre en faisant varier sa couleur."""
        # Liste de couleurs pour l'animation
        title_colors = [
            self.colors["title"],
            "#4f46e5",
            "#3b82f6",
            "#0ea5e9",
            "#3b82f6",
            "#4f46e5",
        ]
        
        # Obtenir l'index de la couleur actuelle
        current_color = self.title_label.cget("fg")
        try:
            color_index = title_colors.index(current_color)
        except ValueError:
            color_index = 0
        
        # Passer à la couleur suivante
        next_color_index = (color_index + 1) % len(title_colors)
        next_color = title_colors[next_color_index]
        
        # Changer la couleur du titre
        self.title_label.config(fg=next_color)
        
        # Planifier la prochaine animation (toutes les 1500 ms)
        self.root.after(1500, self.animate_title)
    
    def create_frames(self):
        """Crée les différents cadres de l'interface avec des effets visuels."""
        # Cadre principal qui contient tout
        self.main_frame = Frame(self.root, bg=self.colors["background"])
        self.main_frame.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.9, anchor="center")
        
        # Disposition en trois colonnes
        # Colonne 1: Tableau du joueur (35% de la largeur)
        # Colonne 2: Panneau de contrôle (20% de la largeur)
        # Colonne 3: Tableau de l'IA (35% de la largeur)
        
        # Frame pour la grille du joueur (à gauche)
        self.player_frame = Frame(
            self.main_frame, 
            bg=self.colors["secondary_bg"], 
            highlightbackground=self.colors["grid"], 
            highlightthickness=2,
            borderwidth=0
        )
        self.player_frame.place(relx=0.225, rely=0.45, relwidth=0.35, relheight=0.7, anchor="center")
        
        # Frame pour les contrôles (au milieu)
        self.controls_frame = Frame(
            self.main_frame, 
            bg=self.colors["secondary_bg"],
            highlightbackground=self.colors["grid"], 
            highlightthickness=1,
            borderwidth=0
        )
        # Positionnement au centre
        self.controls_frame.place(relx=0.5, rely=0.45, relwidth=0.18, relheight=0.7, anchor="center")
        
        # Frame pour la grille de l'IA (à droite)
        self.ai_frame = Frame(
            self.main_frame, 
            bg=self.colors["secondary_bg"], 
            highlightbackground=self.colors["grid"], 
            highlightthickness=2,
            borderwidth=0
        )
        self.ai_frame.place(relx=0.775, rely=0.45, relwidth=0.35, relheight=0.7, anchor="center")
        
        # Frame pour les statistiques (en bas)
        self.stats_frame = Frame(self.main_frame, bg=self.colors["secondary_bg"])
        self.stats_frame.place(relx=0.5, rely=0.9, relwidth=0.9, relheight=0.15, anchor="center")
    
    def create_button(self, parent, text, command, bg_color=None, hover_color=None):
        """
        Crée un bouton stylisé avec effet de survol.
        
        Args:
            parent: Le widget parent
            text: Le texte du bouton
            command: La fonction à exécuter au clic
            bg_color: Couleur de fond (par défaut: couleur du bouton)
            hover_color: Couleur au survol (par défaut: couleur de survol du bouton)
        
        Returns:
            Button: Le bouton créé
        """
        if bg_color is None:
            bg_color = self.colors["button"]["bg"]
        if hover_color is None:
            hover_color = self.colors["button"]["hover"]
            
        btn = Button(
            parent,
            text=text,
            font=(self.text_font, 12),
            bg=bg_color,
            fg=self.colors["button"]["fg"],
            activebackground=hover_color,
            activeforeground=self.colors["button"]["fg"],
            relief=tk.RAISED,
            borderwidth=0,
            padx=10,
            pady=8,
            cursor="hand2",
            command=command
        )
        
        # Effet de survol
        btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))
        
        return btn
    
    def create_boards(self):
        """Crée les grilles de jeu."""
        # Grille du joueur
        Label(
            self.player_frame, 
            text="VOTRE FLOTTE", 
            font=(self.title_font, 16, "bold"), 
            bg=self.colors["secondary_bg"], 
            fg=self.colors["text"]
        ).pack(pady=(15, 5))
        
        Label(
            self.player_frame, 
            text="Défendez vos navires contre l'ennemi", 
            font=(self.text_font, 10), 
            bg=self.colors["secondary_bg"], 
            fg=self.colors["grid"]
        ).pack(pady=(0, 10))
        
        self.player_canvas = Canvas(
            self.player_frame, 
            width=400, 
            height=400, 
            bg=self.colors["secondary_bg"], 
            highlightthickness=0
        )
        self.player_canvas.pack(pady=10, expand=True)
        
        # Grille de l'IA
        Label(
            self.ai_frame, 
            text="FLOTTE ENNEMIE", 
            font=(self.title_font, 16, "bold"), 
            bg=self.colors["secondary_bg"], 
            fg=self.colors["text"]
        ).pack(pady=(15, 5))
        
        Label(
            self.ai_frame, 
            text="Cliquez pour attaquer", 
            font=(self.text_font, 10), 
            bg=self.colors["secondary_bg"], 
            fg=self.colors["grid"]
        ).pack(pady=(0, 10))
        
        self.ai_canvas = Canvas(
            self.ai_frame, 
            width=400, 
            height=400, 
            bg=self.colors["secondary_bg"], 
            highlightthickness=0
        )
        self.ai_canvas.pack(pady=10, expand=True)
        
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
        corner_radius = 3  # Rayon des coins arrondis pour les cellules
        
        # Dessiner un fond pour la grille
        canvas.create_rectangle(
            margin - 5, 
            margin - 5, 
            margin + 10 * cell_size + 5, 
            margin + 10 * cell_size + 5, 
            fill=self.colors["background"],
            outline=self.colors["grid"],
            width=2
        )
        
        # Dessiner les labels des colonnes (A-J)
        for i in range(10):
            canvas.create_text(
                margin + i * cell_size + cell_size // 2,
                margin // 2,
                text=chr(65 + i),
                font=(self.text_font, 11, "bold"),
                fill=self.colors["title"]
            )
        
        # Dessiner les labels des lignes (1-10)
        for i in range(10):
            canvas.create_text(
                margin // 2,
                margin + i * cell_size + cell_size // 2,
                text=str(i + 1),
                font=(self.text_font, 11, "bold"),
                fill=self.colors["title"]
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
                outline_color = self.colors["background"]
                outline_width = 1
                
                if cell_value == 1 and show_ships:  # Navire
                    fill_color = self.colors["ship"]
                elif cell_value == 2:  # Navire touché
                    fill_color = self.colors["hit"]
                elif cell_value == -1:  # Tir dans l'eau
                    fill_color = self.colors["miss"]
                
                # Si c'est la position survolée
                if self.hover_position == (i, j) and not self.game_over and canvas == self.ai_canvas:
                    fill_color = self.colors["hover"]
                    outline_color = self.colors["text"]
                    outline_width = 2
                
                # Si c'est le dernier coup de l'IA
                if self.last_ai_move == (i, j) and canvas == self.player_canvas:
                    outline_color = self.colors["text"]
                    outline_width = 2
                
                # Dessiner la cellule avec des coins arrondis
                self.create_rounded_rectangle(
                    canvas, 
                    x1, y1, x2, y2, 
                    radius=corner_radius, 
                    fill=fill_color, 
                    outline=outline_color,
                    width=outline_width
                )
                
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
                                    self.create_rounded_rectangle(
                                        canvas, 
                                        sx1, sy1, sx2, sy2, 
                                        radius=corner_radius, 
                                        fill=self.colors["sunk"], 
                                        outline=self.colors["text"],
                                        width=2
                                    )
                
                # Si c'est le dernier coup de l'IA, ajouter une croix
                if self.last_ai_move == (i, j) and canvas == self.player_canvas:
                    padding = 5
                    canvas.create_line(
                        x1 + padding, y1 + padding, 
                        x2 - padding, y2 - padding, 
                        fill=self.colors["text"], 
                        width=2
                    )
                    canvas.create_line(
                        x1 + padding, y2 - padding, 
                        x2 - padding, y1 + padding, 
                        fill=self.colors["text"], 
                        width=2
                    )
    
    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=5, **kwargs):
        """
        Dessine un rectangle avec des coins arrondis.
        
        Args:
            canvas: Le canvas sur lequel dessiner
            x1, y1: Coordonnées du coin supérieur gauche
            x2, y2: Coordonnées du coin inférieur droit
            radius: Rayon des coins arrondis
            **kwargs: Arguments supplémentaires pour create_polygon
        """
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def create_status_indicators(self):
        """Crée les indicateurs de statut."""
        # Frame pour les indicateurs de statut
        status_container = Frame(self.stats_frame, bg=self.colors["secondary_bg"])
        status_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Label de statut
        self.status_label = Label(
            status_container,
            text="Cliquez sur la grille ennemie pour commencer le jeu",
            font=(self.text_font, 13, "bold"),
            bg=self.colors["secondary_bg"],
            fg=self.colors["highlight"]
        )
        self.status_label.pack(pady=(5, 10))
        
        # Statistiques de la partie en cours
        self.stats_label = Label(
            status_container,
            text="Navires restants - Joueur: 5 | IA: 5",
            font=(self.text_font, 12),
            bg=self.colors["secondary_bg"],
            fg=self.colors["text"]
        )
        self.stats_label.pack(pady=5)
        
        # Boutons dans le panneau de contrôle
        Label(
            self.controls_frame,
            text="CONTRÔLES",
            font=(self.title_font, 16, "bold"),
            bg=self.colors["secondary_bg"],
            fg=self.colors["title"]
        ).pack(pady=(20, 25))
        
        # Ajouter un espace flexible au-dessus du bouton pour centrer verticalement
        Frame(self.controls_frame, bg=self.colors["secondary_bg"]).pack(expand=True, fill=tk.BOTH)

        # Bouton pour commencer une nouvelle partie
        self.create_button(
            self.controls_frame,
            text="Nouvelle Partie",
            command=self.new_game,
            bg_color="#10b981",
            hover_color="#059669"
        ).pack(pady=17, fill=tk.X, padx=25)

        # Bouton pour voir les statistiques
        self.create_button(
            self.controls_frame,
            text="Voir les Statistiques",
            command=self.show_statistics
        ).pack(pady=17, fill=tk.X, padx=25)

        # Bouton pour quitter
        self.create_button(
            self.controls_frame,
            text="Quitter",
            command=self.root.quit,
            bg_color="#ef4444",
            hover_color="#dc2626"
        ).pack(pady=17, fill=tk.X, padx=25)

        # Ajouter un espace flexible en dessous du bouton pour centrer verticalement
        Frame(self.controls_frame, bg=self.colors["secondary_bg"]).pack(expand=True, fill=tk.BOTH)
        

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
        if self.game_over or self.animation_in_progress:
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
        if self.game_over or self.animation_in_progress:
            return
        
        # Vérifier si c'est le tour du joueur (nouvelle vérification)
        if hasattr(self, 'player_turn_active') and not self.player_turn_active:
            self.status_label.config(
                text="Ce n'est pas votre tour ! Attendez que l'IA joue.",
                fg=self.colors["hit"]
            )
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
                self.status_label.config(
                    text="Vous avez déjà tiré à cette position !",
                    fg=self.colors["hit"]
                )
                return
            
            # Désactiver le tour du joueur pendant l'animation et le tour de l'IA
            self.player_turn_active = False
            
            # Effectuer le tir du joueur
            result = self.game.player_turn(position)
            
            # Mettre à jour l'affichage
            self.draw_grid(self.ai_canvas, self.game.ai_board)
            
            # Animer le résultat
            self.animation_result = result
            self.animation_position = position
            self.animation_in_progress = True
            self.animate_shot_result()
    
    def animate_shot_result(self):
        """Anime le résultat d'un tir avec des effets visuels."""
        if not self.animation_in_progress:
            return
        
        # Récupérer les informations du tir
        result = self.animation_result
        position = self.animation_position
        
        # Afficher le résultat textuel
        if self.animation_step == 0:
            result_text = ""
            result_color = self.colors["text"]
            
            if result == "miss":
                result_text = "À l'eau ! Votre tir a raté la cible."
                result_color = self.colors["miss"]
            elif result == "hit":
                result_text = "Touché ! Vous avez atteint un navire ennemi !"
                result_color = self.colors["hit"]
            elif result[0] == "sunk":
                result_text = f"Coulé ! Vous avez détruit le {result[1]} ennemi !"
                result_color = self.colors["sunk"]
            
            self.status_label.config(text=result_text, fg=result_color)
            self.animation_step += 1
            self.root.after(300, self.animate_shot_result)
            return
        
        # Terminer l'animation
        if self.animation_step >= 1:
            self.animation_in_progress = False
            self.animation_step = 0
            
            # Mettre à jour les statistiques
            self.update_stats()
            
            # Vérifier si le jeu est terminé
            if self.game.is_game_over():
                self.end_game()
                return
            
            # Tour de l'IA
            self.root.after(1000, self.ai_turn)
    
    def ai_turn(self):
        """Gère le tour de l'IA avec des animations."""
        # Afficher que l'IA réfléchit
        self.status_label.config(
            text="L'IA analyse la situation...",
            fg=self.colors["title"]
        )
        self.root.update()
        
        # Simuler un temps de réflexion
        time.sleep(random.uniform(0.5, 1.0))
        
        # L'IA joue son coup
        ai_position, ai_result = self.game.ai_turn()
        self.last_ai_move = ai_position
        
        # Mettre à jour l'affichage
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        
        # Afficher le résultat
        x, y = ai_position
        coord_letter = chr(65 + y)
        
        result_text = ""
        result_color = self.colors["text"]
        
        if ai_result == "miss":
            result_text = f"L'IA tire en {coord_letter}{x+1} et rate !"
            result_color = self.colors["miss"]
        elif ai_result == "hit":
            result_text = f"L'IA tire en {coord_letter}{x+1} et touche un de vos navires !"
            result_color = self.colors["hit"]
        elif ai_result[0] == "sunk":
            result_text = f"L'IA tire en {coord_letter}{x+1} et coule votre {ai_result[1]} !"
            result_color = self.colors["sunk"]
        
        self.status_label.config(text=result_text, fg=result_color)
        
        # Mettre à jour les statistiques
        self.update_stats()
        
        # Vérifier si le jeu est terminé
        if self.game.is_game_over():
            self.end_game()
        else:
            # Réactiver le tour du joueur
            self.player_turn_active = True
            self.status_label.config(
                text="À votre tour ! Cliquez sur la grille ennemie pour tirer.",
                fg=self.colors["highlight"]
            )
    
    def update_stats(self):
        """Met à jour les statistiques affichées."""
        player_ships_left = sum(1 for ship in self.game.player_board.ships if not ship.is_sunk())
        ai_ships_left = sum(1 for ship in self.game.ai_board.ships if not ship.is_sunk())
        
        # Formater le texte avec des emojis et des couleurs
        stats_text = f"Navires restants - Joueur: {player_ships_left} ⚓ | IA: {ai_ships_left} ⚓"
        self.stats_label.config(text=stats_text)
        
        # Changer la couleur si un joueur est en danger (1 navire ou moins)
        if player_ships_left <= 1:
            self.stats_label.config(fg=self.colors["hit"])
        elif ai_ships_left <= 1:
            self.stats_label.config(fg=self.colors["highlight"])
        else:
            self.stats_label.config(fg=self.colors["text"])
    
    def end_game(self):
        """Termine la partie et affiche le résultat avec des animations."""
        self.game_over = True
        
        winner = self.game.get_winner()
        if winner == "player":
            self.status_label.config(
                text="🏆 VICTOIRE ! 🏆 Vous avez anéanti la flotte ennemie !",
                fg=self.colors["highlight"],
                font=(self.title_font, 14, "bold")
            )
            messagebox.showinfo(
                "Victoire navale", 
                "Félicitations Amiral ! Vous avez coulé tous les navires ennemis !"
            )
        else:
            self.status_label.config(
                text="☠️ DÉFAITE ! ☠️ Votre flotte a été détruite par l'ennemi.",
                fg=self.colors["hit"],
                font=(self.title_font, 14, "bold")
            )
            messagebox.showinfo(
                "Défaite", 
                "L'IA a coulé tous vos navires. Meilleure chance la prochaine fois, Capitaine !"
            )
        
        # Afficher les deux grilles avec tous les navires visibles
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        self.draw_grid(self.ai_canvas, self.game.ai_board, show_ships=True)
    
    def new_game(self):
        """Commence une nouvelle partie avec des effets visuels."""
        # Animation de démarrage
        self.status_label.config(
            text="Préparation des flottes en cours...",
            fg=self.colors["title"],
            font=(self.text_font, 13, "bold")
        )
        self.root.update()
        
        # Simuler un temps de chargement
        time.sleep(0.5)
        
        # Réinitialiser le jeu
        self.game = GameManager()
        self.game.initialize_game()
        self.game_over = False
        self.last_ai_move = None
        self.animation_in_progress = False
        self.player_turn_active = True
        
        # Réinitialiser l'affichage
        self.draw_grid(self.player_canvas, self.game.player_board, show_ships=True)
        self.draw_grid(self.ai_canvas, self.game.ai_board, show_ships=False)
        
        self.status_label.config(
            text="Nouvelle bataille commencée. Cliquez sur la grille ennemie pour attaquer !",
            fg=self.colors["highlight"],
            font=(self.text_font, 13, "bold")
        )
        self.update_stats()
    
    def show_statistics(self):
        """Affiche une fenêtre avec les statistiques de jeu."""
        # Utiliser la classe StatisticsView pour afficher les statistiques
        from utils.game_statistics import GameStatistics
        from ui.statistics_view import StatisticsView
        
        # Créer un dictionnaire de couleurs compatible avec StatisticsView
        colors = {
            "background": self.colors["background"],
            "text": self.colors["text"],
            "button_success": "#10b981",  # Vert
            "button_info": self.colors["button"]["bg"],
            "button_danger": "#ef4444"  # Rouge
        }
        
        stats_manager = GameStatistics()
        stats_view = StatisticsView(self.root, stats_manager, colors)
        stats_view.show_statistics_window()