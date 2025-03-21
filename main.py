"""
Point d'entrée principal du jeu de Bataille Navale
"""

import sys
import os

# Ajout du répertoire racine au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.gui import BattleshipGUI
import tkinter as tk

def main():
    """Fonction principale de l'application."""
    root = tk.Tk()
    app = BattleshipGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()