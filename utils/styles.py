"""
Module de styles pour l'interface utilisateur de la bataille navale.
Contient des thèmes prédéfinis et des fonctions d'aide pour personnaliser l'interface.
"""

class Theme:
    """Classe de gestion des thèmes pour l'interface utilisateur."""
    
    # Thème marin (Ocean Deep) - Thème par défaut
    OCEAN_DEEP = {
        "background": "#0a192f",       # Bleu nuit profond
        "secondary_bg": "#172a45",     # Bleu marine
        "grid": "#8892b0",             # Gris bleuté
        "ship": "#1e3a8a",             # Bleu marine foncé
        "hit": "#ef4444",              # Rouge vif
        "miss": "#38bdf8",             # Bleu clair
        "sunk": "#b91c1c",             # Rouge foncé
        "hover": "#f59e0b",            # Jaune orangé
        "text": "#e2e8f0",             # Blanc cassé
        "title": "#60a5fa",            # Bleu ciel
        "highlight": "#10b981",        # Vert turquoise
        "button": {
            "bg": "#3b82f6",           # Bleu primaire
            "hover": "#2563eb",        # Bleu foncé
            "fg": "#ffffff"            # Blanc
        }
    }
    
    # Thème Pirate
    PIRATE = {
        "background": "#1a1a2e",       # Bleu très foncé
        "secondary_bg": "#16213e",     # Bleu nuit
        "grid": "#7f8c8d",             # Gris
        "ship": "#2c3e50",             # Bleu gris foncé
        "hit": "#c0392b",              # Rouge bordeaux
        "miss": "#3498db",             # Bleu
        "sunk": "#922b21",             # Rouge sombre
        "hover": "#f39c12",            # Orange
        "text": "#d1d5db",             # Gris clair
        "title": "#f1c40f",            # Jaune or
        "highlight": "#27ae60",        # Vert
        "button": {
            "bg": "#e67e22",           # Orange
            "hover": "#d35400",        # Orange foncé
            "fg": "#ffffff"            # Blanc
        }
    }
    
    # Thème Moderne
    MODERN_NAVY = {
        "background": "#111827",       # Gris très foncé
        "secondary_bg": "#1f2937",     # Gris foncé
        "grid": "#9ca3af",             # Gris moyen
        "ship": "#374151",             # Gris ardoise
        "hit": "#dc2626",              # Rouge
        "miss": "#0ea5e9",             # Bleu cyan
        "sunk": "#991b1b",             # Rouge foncé
        "hover": "#fbbf24",            # Jaune
        "text": "#f3f4f6",             # Blanc grisé
        "title": "#93c5fd",            # Bleu lavande
        "highlight": "#34d399",        # Turquoise
        "button": {
            "bg": "#4f46e5",           # Indigo
            "hover": "#4338ca",        # Indigo foncé
            "fg": "#ffffff"            # Blanc
        }
    }
    
    # Thème Rétro
    RETRO = {
        "background": "#2c3639",       # Gris anthracite
        "secondary_bg": "#3f4e4f",     # Gris vert
        "grid": "#a27b5c",             # Brun clair
        "ship": "#395b64",             # Bleu gris
        "hit": "#cd5c5c",              # Rouge indien
        "miss": "#a5c9ca",             # Bleu gris clair
        "sunk": "#8b0000",             # Rouge foncé
        "hover": "#deb887",            # Brun burlywood
        "text": "#f5eddc",             # Beige clair
        "title": "#e7f6f2",            # Blanc cassé
        "highlight": "#698269",        # Vert olive
        "button": {
            "bg": "#a27b5c",           # Brun clair
            "hover": "#875c44",        # Brun
            "fg": "#ffffff"            # Blanc
        }
    }
    
    @classmethod
    def get_theme(cls, theme_name="OCEAN_DEEP"):
        """
        Récupère un thème par son nom.
        
        Args:
            theme_name (str): Nom du thème (OCEAN_DEEP, PIRATE, MODERN_NAVY, RETRO)
            
        Returns:
            dict: Dictionnaire de couleurs du thème
        """
        theme_map = {
            "OCEAN_DEEP": cls.OCEAN_DEEP,
            "PIRATE": cls.PIRATE,
            "MODERN_NAVY": cls.MODERN_NAVY,
            "RETRO": cls.RETRO
        }
        
        return theme_map.get(theme_name.upper(), cls.OCEAN_DEEP)


def apply_button_style(button, colors, hover=True):
    """
    Applique un style à un bouton.
    
    Args:
        button (tk.Button): Le bouton à styliser
        colors (dict): Dictionnaire de couleurs du thème
        hover (bool): Si True, ajoute un effet de survol
    """
    button.config(
        bg=colors["button"]["bg"],
        fg=colors["button"]["fg"],
        activebackground=colors["button"]["hover"],
        activeforeground=colors["button"]["fg"],
        relief="flat",
        borderwidth=0,
        cursor="hand2"
    )
    
    if hover:
        button.bind("<Enter>", lambda e: button.config(bg=colors["button"]["hover"])) # Changement de couleur au survol
        button.bind("<Leave>", lambda e: button.config(bg=colors["button"]["bg"])) # Retour à la couleur d'origine


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=5, **kwargs):
    """
    Crée un rectangle avec des coins arrondis sur un canvas.
    
    Args:
        canvas (tk.Canvas): Le canvas sur lequel dessiner
        x1, y1 (int): Coordonnées du coin supérieur gauche
        x2, y2 (int): Coordonnées du coin inférieur droit
        radius (int): Rayon des coins arrondis
        **kwargs: Arguments supplémentaires pour create_polygon
        
    Returns:
        int: ID du polygone créé
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