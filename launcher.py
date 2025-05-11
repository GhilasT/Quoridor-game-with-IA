"""
Launcher script for Quoridor game
This handles the transition between Tkinter menus and Pygame game
"""
import sys
import os
import importlib.util

# Add the directory to path so we can import from it
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the menu module
try:
    from quoridor_menus import launch_menu
except ImportError as e:
    print(f"Error importing menu module: {e}")
    sys.exit(1)

# Import the game module
try:
    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Projet IA.py")
    spec = importlib.util.spec_from_file_location("quoridor_game", game_path)
    quoridor_game = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quoridor_game)
    
    # Verify that the necessary function exists
    if not hasattr(quoridor_game, "launch_game"):
        print("Error: launch_game function not found in the game module")
        sys.exit(1)
except Exception as e:
    print(f"Error importing game module: {e}")
    sys.exit(1)

def main():
    """Main entry point that handles the transition between menus and game"""
    # First launch the Tkinter menu
    game_params = launch_menu()
    
    # Then, if we have game parameters, launch the Pygame game
    if game_params:
        # Check if this is a batch simulation with callbacks
        if game_params.get('mode') == 'BatchAI' and game_params.get('progress_callback'):
            # In this case, we don't want to destroy the Tkinter window
            # as it will be used to display progress
            quoridor_game.launch_game(game_params)
        else:
            # For all other modes, ensure Tkinter is completely shut down
            import tkinter as tk
            for widget in tk._default_root.winfo_children():
                widget.destroy()
            tk._default_root.destroy()
            
            # Now launch the game in the main thread
            quoridor_game.launch_game(game_params)

if __name__ == "__main__":
    main()
