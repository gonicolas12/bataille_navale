"""
Module pour l'affichage des statistiques dans l'interface graphique.
"""

import tkinter as tk
from tkinter import Frame, Label, Button, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class StatisticsView:
    """Classe pour l'affichage des statistiques de jeu."""
    
    # Variable de classe pour suivre l'instance active de la fenêtre de statistiques
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
        
        # Définir les couleurs par défaut si non fournies
        self.colors = colors or {
            "background": "#3a4f6a",
            "text": "white",
            "button_success": "#2ecc71",
            "button_info": "#3498db",
            "button_danger": "#e74c3c"
        }
    
    def show_statistics_window(self):
        """Affiche une fenêtre avec les statistiques de jeu."""
        # Vérifier si une fenêtre de statistiques est déjà ouverte
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
        
        self.stats_window.title("Statistiques de jeu - Bataille Navale")
        # Augmenter la taille de la fenêtre
        self.stats_window.geometry("1000x700")
        self.stats_window.configure(bg=self.colors["background"])
        
        # Configurer le gestionnaire de fermeture pour nettoyer la référence
        self.stats_window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Cadre principal (utilisé pour centrer le contenu)
        main_frame = Frame(self.stats_window, bg=self.colors["background"])
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Frame pour le titre
        title_frame = Frame(main_frame, bg=self.colors["background"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        Label(
            title_frame,
            text="STATISTIQUES DE JEU",
            font=("Arial", 18, "bold"),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack()
        
        # Frame pour les graphiques
        graphs_frame = Frame(main_frame, bg=self.colors["background"])
        graphs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Créer les figures pour matplotlib avec une taille plus grande
        self._create_win_distribution_graph(graphs_frame)
        self._create_hit_rate_graph(graphs_frame)
        
        # Frame pour les statistiques textuelles
        text_stats_frame = Frame(main_frame, bg=self.colors["background"])
        text_stats_frame.pack(fill=tk.X, pady=20)
        
        # Afficher quelques statistiques textuelles
        avg_game_length = self.stats_manager.get_average_game_length()
        wins = self.stats_manager.get_wins_by_player()
        total_games = wins["player"] + wins["ai"]
        
        stats_text = (
            f"Parties jouées: {total_games}  |  "
            f"Durée moyenne: {avg_game_length:.1f} tours  |  "
            f"Victoires joueur: {wins['player']}  |  "
            f"Victoires IA: {wins['ai']}"
        )
        Label(
            text_stats_frame,
            text=stats_text,
            font=("Arial", 12),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack(pady=10)
        
        # Frame pour les boutons (centré)
        buttons_frame = Frame(main_frame, bg=self.colors["background"])
        buttons_frame.pack(pady=(0, 20))
        
        # Bouton pour générer une heatmap
        Button(
            buttons_frame,
            text="Générer Heatmap",
            font=("Arial", 12),
            bg=self.colors["button_success"],
            fg="white",
            width=15,
            command=self._generate_heatmap
        ).grid(row=0, column=0, padx=10, pady=10)
        
        # Bouton pour exporter un rapport
        Button(
            buttons_frame,
            text="Exporter Rapport",
            font=("Arial", 12),
            bg=self.colors["button_info"],
            fg="white",
            width=15,
            command=self._export_report
        ).grid(row=0, column=1, padx=10, pady=10)
        
        # Bouton pour fermer la fenêtre
        Button(
            buttons_frame,
            text="Fermer",
            font=("Arial", 12),
            bg=self.colors["button_danger"],
            fg="white",
            width=15,
            command=self._on_closing
        ).grid(row=0, column=2, padx=10, pady=10)
    
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
        # Créer un conteneur pour le graphique (pour le centrage)
        graph_container = Frame(parent_frame, bg=self.colors["background"])
        graph_container.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        # Obtenir les données
        wins = self.stats_manager.get_wins_by_player()
        
        # Créer la figure avec une taille plus grande
        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Tracer le graphique
        bars = ax.bar(['Joueur', 'IA'], [wins["player"], wins["ai"]], color=['#3498db', '#e74c3c'])
        ax.set_title('Distribution des victoires', fontsize=14)
        ax.set_ylabel('Nombre de victoires', fontsize=12)
        
        # S'assurer que l'axe y commence à 0 et a une valeur minimale de 5
        ax.set_ylim(0, max(5, wins["player"] + 1, wins["ai"] + 1))
        
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(int(height)), ha='center', va='bottom', fontsize=12)
        
        # Ajouter de l'espace autour du graphique
        fig.tight_layout(pad=3.0)
        
        # Ajouter la figure au cadre
        canvas = FigureCanvasTkAgg(fig, graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ajouter un titre au cadre
        Label(
            graph_container,
            text="Distribution des victoires",
            font=("Arial", 12, "bold"),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack()
    
    def _create_hit_rate_graph(self, parent_frame):
        """
        Crée et affiche le graphique des taux de réussite.
        
        Args:
            parent_frame (tk.Frame): Frame parent pour le graphique
        """
        # Créer un conteneur pour le graphique (pour le centrage)
        graph_container = Frame(parent_frame, bg=self.colors["background"])
        graph_container.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        
        # Configurer le système de grille pour centrer les graphiques
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        
        # Obtenir les données
        hit_rates = self.stats_manager.get_hit_miss_ratio()
        
        # Créer la figure avec une taille plus grande
        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Tracer le graphique
        bars = ax.bar(['Joueur', 'IA'], [hit_rates["player"] * 100, hit_rates["ai"] * 100], color=['#3498db', '#e74c3c'])
        ax.set_title('Taux de réussite des tirs (%)', fontsize=14)
        ax.set_ylabel('Pourcentage (%)', fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{height:.1f}%", ha='center', va='bottom', fontsize=12)
        
        # Ajouter de l'espace autour du graphique
        fig.tight_layout(pad=3.0)
        
        # Ajouter la figure au cadre
        canvas = FigureCanvasTkAgg(fig, graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ajouter un titre au cadre
        Label(
            graph_container,
            text="Taux de réussite des tirs",
            font=("Arial", 12, "bold"),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack()
    
    def _generate_heatmap(self):
        """Génère et affiche une heatmap des positions ciblées."""
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        
        # Générer la heatmap
        file_path = "data/shots_heatmap.png"
        self.stats_manager.generate_heatmap(file_path)
        
        # Informer l'utilisateur
        info_window = Toplevel(self.stats_window)
        info_window.title("Heatmap générée")
        info_window.geometry("400x150")
        info_window.configure(bg=self.colors["background"])
        info_window.resizable(False, False)
        
        # Centrer sur l'écran
        info_window.update_idletasks()
        width = info_window.winfo_width()
        height = info_window.winfo_height()
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        Label(
            info_window,
            text="Heatmap générée avec succès !",
            font=("Arial", 14),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack(pady=(20, 10))
        
        Label(
            info_window,
            text=f"Fichier sauvegardé: {file_path}",
            font=("Arial", 10),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack(pady=10)
        
        Button(
            info_window,
            text="OK",
            font=("Arial", 12),
            bg=self.colors["button_info"],
            fg="white",
            command=info_window.destroy
        ).pack(pady=10)
    
    def _export_report(self):
        """Exporte un rapport textuel des statistiques."""
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        
        # Exporter le rapport
        file_path = "data/statistics_report.txt"
        self.stats_manager.export_statistics_report(file_path)
        
        # Informer l'utilisateur
        info_window = Toplevel(self.stats_window)
        info_window.title("Rapport exporté")
        info_window.geometry("400x150")
        info_window.configure(bg=self.colors["background"])
        info_window.resizable(False, False)
        
        # Centrer sur l'écran
        info_window.update_idletasks()
        width = info_window.winfo_width()
        height = info_window.winfo_height()
        x = (info_window.winfo_screenwidth() // 2) - (width // 2)
        y = (info_window.winfo_screenheight() // 2) - (height // 2)
        info_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        Label(
            info_window,
            text="Rapport exporté avec succès !",
            font=("Arial", 14),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack(pady=(20, 10))
        
        Label(
            info_window,
            text=f"Fichier sauvegardé: {file_path}",
            font=("Arial", 10),
            bg=self.colors["background"],
            fg=self.colors["text"]
        ).pack(pady=10)
        
        Button(
            info_window,
            text="OK",
            font=("Arial", 12),
            bg=self.colors["button_info"],
            fg="white",
            command=info_window.destroy
        ).pack(pady=10)