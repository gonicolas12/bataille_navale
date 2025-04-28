"""
Module pour l'affichage des statistiques dans l'interface graphique.
"""

import tkinter as tk
from tkinter import Frame, Label, Button, Toplevel, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
import pandas as pd

class StatisticsView:
    """Classe pour l'affichage des statistiques de jeu."""
    
    stats_window_instance = None
    
    def __init__(self, parent, statistics_manager, colors=None):
        """
        Initialise une vue de statistiques.
        
        Args:
            parent (tk.Tk ou tk.Toplevel): La fenêtre parente
            statistics_manager (GameStatistics): Le gestionnaire de statistiques
            colors (dict, optional): Dictionnaire de couleurs pour l'interface
        """
        self.parent = parent
        self.stats_manager = statistics_manager
        self.stats_window = None
        
        # Définir les couleurs par défaut si non données
        self.colors = colors or {
            "background": "#0a192f",
            "text": "#e2e8f0",
            "button_success": "#10b981",
            "button_info": "#3b82f6",
            "button_danger": "#ef4444"
        }
        
        # Charger les polices personnalisées
        self.load_custom_fonts()
    
    def load_custom_fonts(self):
        """Charge les polices personnalisées si disponibles, sinon utilise des alternatives système."""
        # Liste des polices possibles
        title_fonts = ["Montserrat", "Verdana", "Arial", "Helvetica"]
        text_fonts = ["Roboto", "Segoe UI", "Tahoma", "Arial"]
        
        # Trouver la première police disponible pour les titres
        self.title_font = None
        for font_name in title_fonts:
            if font_name.lower() in [f.lower() for f in font.families()]:
                self.title_font = font_name
                break
        if not self.title_font:
            self.title_font = "TkDefaultFont"
        
        # Trouver la première police disponible pour le texte
        self.text_font = None
        for font_name in text_fonts:
            if font_name.lower() in [f.lower() for f in font.families()]:
                self.text_font = font_name
                break
        if not self.text_font:
            self.text_font = "TkDefaultFont"
    
    def show_statistics_window(self):
        """Affiche une fenêtre avec les statistiques de jeu."""
        if StatisticsView.stats_window_instance is not None:
            try:
                # Si la fenêtre existe déjà, mettre au premier plan
                StatisticsView.stats_window_instance.deiconify()
                StatisticsView.stats_window_instance.lift()
                StatisticsView.stats_window_instance.focus_force()
                return
            except tk.TclError:
                # Si la fenêtre a été fermée mais pas correctement nettoyée
                StatisticsView.stats_window_instance = None
        
        # Créer une nouvelle fenêtre
        self.stats_window = Toplevel(self.parent)
        StatisticsView.stats_window_instance = self.stats_window
        
        self.stats_window.title("⚓ Statistiques Navales - Bataille Navale ⚓")
        
        # Maximiser la fenêtre au lieu d'utiliser le mode plein écran
        self.stats_window.state('zoomed')
                
        # Configurer le gestionnaire de fermeture pour nettoyer la référence
        self.stats_window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Cadre principal (utilisé pour centrer le contenu)
        main_frame = Frame(self.stats_window, bg=self.colors["background"])
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Frame pour le titre avec une bordure décorative
        title_frame = Frame(
            main_frame, 
            bg=self.colors["background"],
            highlightbackground="#60a5fa",
            highlightthickness=2
        )
        title_frame.pack(fill=tk.X, pady=(0, 25))
        
        Label(
            title_frame,
            text="⚓ STATISTIQUES DE BATAILLE NAVALE ⚓",
            font=(self.title_font, 22, "bold"),
            bg=self.colors["background"],
            fg="#60a5fa"
        ).pack(pady=15)
        
        # Frame pour les graphiques avec une bordure décorative
        graphs_frame = Frame(
            main_frame, 
            bg=self.colors["background"],
            highlightbackground="#8892b0",
            highlightthickness=1
        )
        graphs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Créer les figures pour matplotlib
        self._create_win_distribution_graph(graphs_frame)
        self._create_hit_rate_graph(graphs_frame)
        
        # Frame pour les statistiques textuelles
        text_stats_frame = Frame(main_frame, bg="#172a45")
        text_stats_frame.pack(fill=tk.X, pady=20)
        
        # Afficher quelques statistiques textuelles
        avg_game_length = self.stats_manager.get_average_game_length()
        wins = self.stats_manager.get_wins_by_player()
        total_games = wins["player"] + wins["ai"]
        
        # Améliorer l'affichage des statistiques avec des emojis et un meilleur formatage
        stats_label = Label(
            text_stats_frame,
            bg="#172a45",
            fg=self.colors["text"],
            font=(self.text_font, 13),
            justify=tk.CENTER,
            padx=20,
            pady=15
        )
        stats_label.pack(fill=tk.X)
        
        stats_text = (
            f"🎮 Parties jouées: {total_games}   |   "
            f"⏱️ Durée moyenne: {avg_game_length:.1f} tours   |   "
            f"🏆 Victoires joueur: {wins['player']}   |   "
            f"🤖 Victoires IA: {wins['ai']}"
        )
        stats_label.config(text=stats_text)
        
        # Frame pour les boutons avec un espace
        buttons_frame = Frame(main_frame, bg=self.colors["background"])
        buttons_frame.pack(pady=(15, 20))
        
        # Style commun pour les boutons
        button_style = {
            "font": (self.text_font, 12),
            "width": 18,
            "height": 2,
            "borderwidth": 0,
            "cursor": "hand2"
        }
        
        # Bouton pour générer une heatmap
        heatmap_btn = Button(
            buttons_frame,
            text="Générer Heatmap",
            bg=self.colors["button_success"],
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            command=self._generate_heatmap,
            **button_style
        )
        heatmap_btn.grid(row=0, column=0, padx=15, pady=10)
        
        # Effet de survol
        heatmap_btn.bind("<Enter>", lambda e: heatmap_btn.config(bg="#059669"))
        heatmap_btn.bind("<Leave>", lambda e: heatmap_btn.config(bg=self.colors["button_success"]))
        
        # Bouton pour exporter un rapport
        export_btn = Button(
            buttons_frame,
            text="Exporter Rapport",
            bg=self.colors["button_info"],
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            command=self._export_report,
            **button_style
        )
        export_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # Effet de survol
        export_btn.bind("<Enter>", lambda e: export_btn.config(bg="#2563eb"))
        export_btn.bind("<Leave>", lambda e: export_btn.config(bg=self.colors["button_info"]))
        
        # Bouton pour fermer la fenêtre
        close_btn = Button(
            buttons_frame,
            text="Fermer",
            bg=self.colors["button_danger"],
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            command=self._on_closing,
            **button_style
        )
        close_btn.grid(row=0, column=2, padx=15, pady=10)
        
        # Effet de survol
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#dc2626"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.colors["button_danger"]))
    
    def _on_closing(self):
        """Gère la fermeture de la fenêtre de statistiques."""
        # Réinitialiser la référence de l'instance de fenêtre
        StatisticsView.stats_window_instance = None
        self.stats_window.destroy()
    
    def _create_win_distribution_graph(self, parent_frame):
        """
        Crée et affiche le graphique de distribution des victoires.
        
        Args:
            parent_frame (tk.Frame): Frame parent pour le graphique
        """
        # Créer un conteneur pour le graphique
        graph_container = Frame(parent_frame, bg=self.colors["background"])
        graph_container.grid(row=0, column=0, padx=20, pady=15, sticky="nsew")
        
        # Obtenir les données
        wins = self.stats_manager.get_wins_by_player()
        
        # Configurer le style de matplotlib
        plt.style.use('dark_background')
        
        # Créer la figure
        fig = plt.figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#172a45')  # Couleur de fond
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#172a45')  # Couleur de fond du graphique
        
        colors = ['#60a5fa', '#f97316']
        
        # Tracer le graphique
        bars = ax.bar(['Joueur', 'IA'], [wins["player"], wins["ai"]], color=colors, width=0.6, edgecolor='none', alpha=0.9)
        
        # Ajouter un titre
        ax.set_title('Distribution des Victoires', fontsize=16, color='white', pad=15)
        
        # Personnaliser les axes
        ax.set_ylabel('Nombre de victoires', fontsize=12, color='white', labelpad=10)
        ax.tick_params(axis='both', colors='white', labelsize=11)
        
        # S'assurer que l'axe y commence à 0 et a une valeur minimale de 5
        ax.set_ylim(0, max(5, wins["player"] + 1, wins["ai"] + 1))
        
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(int(height)), ha='center', va='bottom', fontsize=14, color='white', fontweight='bold')
        
        # Supprimer les bordures du graphique
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Ajouter de l'espace autour du graphique
        fig.tight_layout(pad=3.0)
        
        # Ajouter la figure au cadre
        canvas = FigureCanvasTkAgg(fig, graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ajouter un titre au cadre
        Label(
            graph_container,
            text="Distribution des Victoires",
            font=(self.title_font, 14, "bold"),
            bg=self.colors["background"],
            fg="#60a5fa"  # Bleu ciel
        ).pack(pady=(15, 5))
    
    def _create_hit_rate_graph(self, parent_frame):
        """
        Crée et affiche le graphique des taux de réussite.
        
        Args:
            parent_frame (tk.Frame): Frame parent pour le graphique
        """
        # Créer un conteneur pour le graphique
        graph_container = Frame(parent_frame, bg=self.colors["background"])
        graph_container.grid(row=0, column=1, padx=20, pady=15, sticky="nsew")
        
        # Configurer le système de grille pour centrer les graphiques
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        
        # Obtenir les données
        hit_rates = self.stats_manager.get_hit_miss_ratio()
        
        # Configurer le style de matplotlib
        plt.style.use('dark_background')
        
        # Créer la figure
        fig = plt.figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#172a45')  # Couleur de fond
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#172a45')  # Couleur de fond du graphique
        
        # Couleurs pour les barres
        colors = ['#60a5fa', '#f97316']
        
        # Tracer le graphique
        bars = ax.bar(['Joueur', 'IA'], [hit_rates["player"] * 100, hit_rates["ai"] * 100], color=colors, width=0.6, edgecolor='none', alpha=0.9)
        
        # Ajouter un titre
        ax.set_title('Taux de Réussite des Tirs (%)', fontsize=16, color='white', pad=15)
        
        # Personnaliser les axes
        ax.set_ylabel('Pourcentage (%)', fontsize=12, color='white', labelpad=10)
        ax.tick_params(axis='both', colors='white', labelsize=11)
        
        # Configurer l'axe y
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{height:.1f}%", ha='center', va='bottom', fontsize=14, color='white', fontweight='bold')
        
        # Supprimer les bordures du graphique
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Ajouter de l'espace autour du graphique
        fig.tight_layout(pad=3.0)
        
        # Ajouter la figure au cadre
        canvas = FigureCanvasTkAgg(fig, graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ajouter un titre au cadre
        Label(
            graph_container,
            text="Taux de Réussite des Tirs",
            font=(self.title_font, 14, "bold"),
            bg=self.colors["background"],
            fg="#60a5fa"
        ).pack(pady=(15, 5))
    
    def _generate_heatmap(self):
        """Génère et affiche une heatmap des positions ciblées."""
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        
        # Générer la heatmap
        file_path = "data/shots_heatmap.png"
        
        # Configurer matplotlib
        plt.style.use('dark_background')
        
        # Charger les données pour la heatmap
        self.stats_manager.reload_data()
        game_data = self.stats_manager.game_data
        
        if game_data.empty:
            self._show_info_dialog(
                "Aucune donnée disponible", 
                "Il n'y a pas de données suffisantes pour générer une heatmap."
            )
            return
        
        # Créer une matrice 10x10 pour stocker le nombre de tirs à chaque position
        heatmap_data = np.zeros((10, 10))
        
        # Parcourir les données pour remplir la heatmap
        for _, row in game_data.iterrows():
            if pd.notna(row['position']):  # Vérifier que la position n'est pas NaN
                position = row['position'].split(',')
                if len(position) == 2:  # Vérifier que la position est valide
                    try:
                        x, y = int(position[0]), int(position[1])
                        if 0 <= x < 10 and 0 <= y < 10:
                            heatmap_data[x][y] += 1
                    except ValueError:
                        # Ignorer les positions mal formatées
                        pass
        
        # Créer la figure
        fig = plt.figure(figsize=(10, 8))
        fig.patch.set_facecolor('#0a192f')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#172a45')
        
        # apparence de la heatmap
        cmap = plt.cm.hot  # Utiliser la colormap "hot" pour la heatmap
        img = ax.imshow(heatmap_data, cmap=cmap, interpolation='nearest')
        
        # Ajouter une barre de couleur
        cbar = plt.colorbar(img, ax=ax, pad=0.01)
        cbar.set_label('Nombre de tirs', color='white', fontsize=12, labelpad=15)
        cbar.ax.tick_params(colors='white')
        
        # Ajouter un titre
        ax.set_title('Heatmap des Positions Ciblées', color='white', fontsize=18, pad=20)
        
        # Personnaliser les axes
        ax.set_xlabel('Colonne (A-J)', color='white', fontsize=12, labelpad=10)
        ax.set_ylabel('Ligne (1-10)', color='white', fontsize=12, labelpad=10)
        
        # Convertir les indices de colonnes en lettres (A-J)
        column_labels = [chr(65 + i) for i in range(10)]
        ax.set_xticks(np.arange(10))
        ax.set_xticklabels(column_labels, fontsize=11, color='white')
        
        # Convertir les indices de lignes en nombres (1-10)
        row_labels = [str(i + 1) for i in range(10)]
        ax.set_yticks(np.arange(10))
        ax.set_yticklabels(row_labels, fontsize=11, color='white')
        
        # Ajout des lignes de grille
        ax.grid(color='white', linestyle='-', linewidth=0.5, alpha=0.3)
        plt.setp(ax.get_xticklabels(), ha="center")
        
        # Ajuster les marges
        plt.tight_layout()
        
        # Sauvegarder la figure
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self._show_info_dialog(
            "Heatmap Générée",
            f"Heatmap générée avec succès !\nFichier sauvegardé: {file_path}"
        )
    
    def _export_report(self):
        """Exporte un rapport textuel des statistiques."""
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        
        # Exporter le rapport
        file_path = "data/statistics_report.txt"
        self.stats_manager.export_statistics_report(file_path)
        
        self._show_info_dialog(
            "Rapport Exporté",
            f"Rapport exporté avec succès !\nFichier sauvegardé: {file_path}"
        )
    
    def _show_info_dialog(self, title, message):
        """
        Affiche une boîte de dialogue d'information.
        
        Args:
            title (str): Titre de la boîte de dialogue
            message (str): Message à afficher
        """
        # Créer une fenêtre de dialogue personnalisée
        dialog = Toplevel(self.stats_window)
        dialog.title(title)
        dialog.geometry("450x200")
        dialog.configure(bg=self.colors["background"])
        dialog.resizable(False, False)
        
        # Rendre la fenêtre modale
        dialog.transient(self.stats_window)
        dialog.grab_set()
        
        # Centrer sur l'écran parent
        dialog.update_idletasks()
        parent_x = self.stats_window.winfo_x()
        parent_y = self.stats_window.winfo_y()
        parent_width = self.stats_window.winfo_width()
        parent_height = self.stats_window.winfo_height()
        
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        Label(
            dialog,
            text=title,
            font=(self.title_font, 16, "bold"),
            bg=self.colors["background"],
            fg="#60a5fa"
        ).pack(pady=(20, 10))
        
        Label(
            dialog,
            text=message,
            font=(self.text_font, 12),
            bg=self.colors["background"],
            fg=self.colors["text"],
            justify=tk.CENTER,
            wraplength=400
        ).pack(pady=10, padx=20)
        
        ok_button = Button(
            dialog,
            text="OK",
            font=(self.text_font, 12),
            bg=self.colors["button_info"],
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            command=dialog.destroy,
            width=10,
            borderwidth=0,
            cursor="hand2"
        )
        ok_button.pack(pady=15)
        
        # Effet de survol
        ok_button.bind("<Enter>", lambda e: ok_button.config(bg="#2563eb"))
        ok_button.bind("<Leave>", lambda e: ok_button.config(bg=self.colors["button_info"]))
        
        # Centrer le bouton
        dialog.update_idletasks()
        
        # Mettre le focus sur le bouton OK
        ok_button.focus_set()
        
        # Lier la touche Entrée au bouton OK
        dialog.bind("<Return>", lambda event: dialog.destroy())
        dialog.wait_window()