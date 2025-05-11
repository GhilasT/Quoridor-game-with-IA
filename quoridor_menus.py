import tkinter as tk
from tkinter import ttk
import sys
import os
import importlib.util

# Import our game module
try:
    # Add the directory to path so we can import from it
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import the game module (Projet IA.py)
    spec = importlib.util.spec_from_file_location(
        "quoridor_game", 
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Projet IA.py")
    )
    quoridor_game = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quoridor_game)
    
    # Verify that the necessary function exists
    if not hasattr(quoridor_game, "launch_game"):
        print("Error: launch_game function not found in the game module")
except Exception as e:
    print(f"Error importing game module: {e}")
    quoridor_game = None

class QuoridorMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quoridor")
        self.root.configure(bg="#0a1428")  # Dark blue background matching the Pygame theme
        
        # Maximize the window (but not fullscreen)
        self.root.state('zoomed')  # This works on Windows
        
        # For Linux/Mac compatibility
        # Delay the maximization slightly to ensure it works on all platforms
        self.root.update_idletasks()
        self.root.after(10, self._maximize_window)

        # Constants
        self.DIFFICULTY_EASY = 2
        self.DIFFICULTY_MEDIUM = 5
        self.DIFFICULTY_HARD = 7
        
        # Game state variables
        self.selected_mode = None
        self.selected_difficulty = self.DIFFICULTY_MEDIUM
        self.selected_ai1_difficulty = self.DIFFICULTY_MEDIUM
        self.selected_ai2_difficulty = self.DIFFICULTY_MEDIUM
        self.num_matches = 100
        self.game_params = None
        
        # Create the main menu
        self.create_main_menu()
        
        # Configure style for ttk widgets
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Nova Square', 14), background='#FFD700', foreground='#0a1428')
        self.style.configure('TLabel', font=('Nova Square', 16), background='#0a1428', foreground='#FFFFFF')
        self.style.map('TButton', 
                      background=[('active', '#FFEB64')],
                      foreground=[('active', '#0a1428')])
    
    def _maximize_window(self):
        """Cross-platform function to maximize the window"""
        if sys.platform == 'darwin':  # macOS
            # On macOS, use applescript to maximize
            try:
                from subprocess import call
                call(['/usr/bin/osascript', '-e', 
                      'tell application "System Events" to set frontmost of process "Python" to true'])
                call(['/usr/bin/osascript', '-e', 
                      'tell application "System Events" to keystroke "f" using {control down, command down}'])
            except Exception:
                # If applescript fails, try to use the window manager directly
                self.root.wm_attributes('-zoomed', True)
        elif sys.platform in ['linux', 'linux2']:  # Linux
            self.root.attributes('-zoomed', True)
        # Windows uses 'zoomed' state which is already set in __init__

    def create_main_menu(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Title
        title_label = tk.Label(self.root, text="QUORIDOR", 
                             font=('Nova Square', 72, 'bold'), 
                             fg="#FFD700", bg="#0a1428")
        title_label.pack(pady=(100, 50))
        
        # Frame for buttons
        button_frame = tk.Frame(self.root, bg="#0a1428")
        button_frame.pack(pady=20)
        
        # Buttons
        button_width = 25
        button_height = 2
        
        pvp_button = tk.Button(button_frame, text="Joueur vs Joueur", 
                             font=('Nova Square', 16),
                             bg="#FFD700", fg="#0a1428",
                             width=button_width, height=button_height,
                             command=lambda: self.start_game('PVP'))
        pvp_button.pack(pady=10)
        
        pve_button = tk.Button(button_frame, text="Joueur vs IA", 
                             font=('Nova Square', 16),
                             bg="#FFD700", fg="#0a1428",
                             width=button_width, height=button_height,
                             command=self.show_difficulty_menu)
        pve_button.pack(pady=10)
        
        ai_vs_ai_button = tk.Button(button_frame, text="IA vs IA", 
                                  font=('Nova Square', 16),
                                  bg="#FFD700", fg="#0a1428",
                                  width=button_width, height=button_height,
                                  command=self.show_ai_vs_ai_menu)
        ai_vs_ai_button.pack(pady=10)
        
        batch_ai_button = tk.Button(button_frame, text="Batch IA vs IA", 
                                  font=('Nova Square', 16),
                                  bg="#FFD700", fg="#0a1428",
                                  width=button_width, height=button_height,
                                  command=self.show_batch_ai_menu)
        batch_ai_button.pack(pady=10)
        
        # Quit button
        quit_button = tk.Button(self.root, text="Quitter", 
                             font=('Nova Square', 14),
                             bg="#8B0000", fg="white",
                             width=15, height=1,
                             command=self.root.destroy)
        quit_button.pack(side=tk.BOTTOM, pady=20)
    
    def show_difficulty_menu(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Title
        title_label = tk.Label(self.root, text="Difficulté", 
                             font=('Nova Square', 48, 'bold'), 
                             fg="#FFD700", bg="#0a1428")
        title_label.pack(pady=(100, 50))
        
        # Frame for buttons
        button_frame = tk.Frame(self.root, bg="#0a1428")
        button_frame.pack(pady=20)
        
        # Difficulty buttons
        button_width = 20
        button_height = 2
        
        easy_button = tk.Button(button_frame, text="Facile", 
                              font=('Nova Square', 16),
                              bg="#FFD700", fg="#0a1428",
                              width=button_width, height=button_height,
                              command=lambda: self.set_difficulty_and_start(self.DIFFICULTY_EASY))
        easy_button.pack(pady=10)
        
        medium_button = tk.Button(button_frame, text="Intermédiaire", 
                                font=('Nova Square', 16),
                                bg="#FFD700", fg="#0a1428",
                                width=button_width, height=button_height,
                                command=lambda: self.set_difficulty_and_start(self.DIFFICULTY_MEDIUM))
        medium_button.pack(pady=10)
        
        hard_button = tk.Button(button_frame, text="Difficile", 
                              font=('Nova Square', 16),
                              bg="#FFD700", fg="#0a1428",
                              width=button_width, height=button_height,
                              command=lambda: self.set_difficulty_and_start(self.DIFFICULTY_HARD))
        hard_button.pack(pady=10)
        
        # Back button
        back_button = tk.Button(self.root, text="Retour", 
                              font=('Nova Square', 14),
                              bg="#555555", fg="white",
                              width=15, height=1,
                              command=self.create_main_menu)
        back_button.pack(side=tk.BOTTOM, pady=20)
    
    def set_difficulty_and_start(self, difficulty):
        self.selected_difficulty = difficulty
        self.start_game('PVE')
    
    def show_ai_vs_ai_menu(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Title for IA1
        title_label = tk.Label(self.root, text="Difficulté IA1 (rouge)", 
                             font=('Nova Square', 36, 'bold'), 
                             fg="#FFD700", bg="#0a1428")
        title_label.pack(pady=(80, 30))
        
        # Frame for buttons for IA1
        ia1_frame = tk.Frame(self.root, bg="#0a1428")
        ia1_frame.pack(pady=10)
        
        # IA1 difficulty buttons
        button_width = 15
        button_height = 1
        
        ia1_easy = tk.Button(ia1_frame, text="Facile", 
                           font=('Nova Square', 14),
                           bg="#FFD700", fg="#0a1428",
                           width=button_width, height=button_height,
                           command=lambda: self.set_ia1_difficulty(self.DIFFICULTY_EASY))
        ia1_easy.grid(row=0, column=0, padx=10)
        
        ia1_medium = tk.Button(ia1_frame, text="Intermédiaire", 
                             font=('Nova Square', 14),
                             bg="#FFD700", fg="#0a1428",
                             width=button_width, height=button_height,
                             command=lambda: self.set_ia1_difficulty(self.DIFFICULTY_MEDIUM))
        ia1_medium.grid(row=0, column=1, padx=10)
        
        ia1_hard = tk.Button(ia1_frame, text="Difficile", 
                           font=('Nova Square', 14),
                           bg="#FFD700", fg="#0a1428",
                           width=button_width, height=button_height,
                           command=lambda: self.set_ia1_difficulty(self.DIFFICULTY_HARD))
        ia1_hard.grid(row=0, column=2, padx=10)
        
        # Title for IA2
        title_label2 = tk.Label(self.root, text="Difficulté IA2 (bleu)", 
                              font=('Nova Square', 36, 'bold'), 
                              fg="#FFD700", bg="#0a1428")
        title_label2.pack(pady=(30, 30))
        
        # Frame for buttons for IA2
        ia2_frame = tk.Frame(self.root, bg="#0a1428")
        ia2_frame.pack(pady=10)
        
        # IA2 difficulty buttons
        ia2_easy = tk.Button(ia2_frame, text="Facile", 
                           font=('Nova Square', 14),
                           bg="#FFD700", fg="#0a1428",
                           width=button_width, height=button_height,
                           command=lambda: self.set_ia2_difficulty_and_start(self.DIFFICULTY_EASY))
        ia2_easy.grid(row=0, column=0, padx=10)
        
        ia2_medium = tk.Button(ia2_frame, text="Intermédiaire", 
                             font=('Nova Square', 14),
                             bg="#FFD700", fg="#0a1428",
                             width=button_width, height=button_height,
                             command=lambda: self.set_ia2_difficulty_and_start(self.DIFFICULTY_MEDIUM))
        ia2_medium.grid(row=0, column=1, padx=10)
        
        ia2_hard = tk.Button(ia2_frame, text="Difficile", 
                           font=('Nova Square', 14),
                           bg="#FFD700", fg="#0a1428",
                           width=button_width, height=button_height,
                           command=lambda: self.set_ia2_difficulty_and_start(self.DIFFICULTY_HARD))
        ia2_hard.grid(row=0, column=2, padx=10)
        
        # Back button
        back_button = tk.Button(self.root, text="Retour", 
                              font=('Nova Square', 14),
                              bg="#555555", fg="white",
                              width=15, height=1,
                              command=self.create_main_menu)
        back_button.pack(side=tk.BOTTOM, pady=20)
    
    def set_ia1_difficulty(self, difficulty):
        self.selected_ai1_difficulty = difficulty
        # Update button colors or show confirmation
    
    def set_ia2_difficulty_and_start(self, difficulty):
        self.selected_ai2_difficulty = difficulty
        self.start_game('AIvsAI')
    
    def show_batch_ai_menu(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Title
        title_label = tk.Label(self.root, text="BATCH IA vs IA", 
                             font=('Nova Square', 36, 'bold'), 
                             fg="#FFD700", bg="#0a1428")
        title_label.pack(pady=(50, 30))
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#0a1428")
        main_frame.pack(pady=20)
        
        # IA1 difficulty selection
        tk.Label(main_frame, text="IA 1 (Rouge):", font=('Nova Square', 16), 
               fg="white", bg="#0a1428").grid(row=0, column=0, sticky='w', pady=10)
        
        ia1_frame = tk.Frame(main_frame, bg="#0a1428")
        ia1_frame.grid(row=0, column=1, pady=10)
        
        ia1_var = tk.StringVar(value=str(self.DIFFICULTY_MEDIUM))
        
        ia1_easy = tk.Radiobutton(ia1_frame, text="Facile", variable=ia1_var, value=str(self.DIFFICULTY_EASY),
                                font=('Nova Square', 14), bg="#0a1428", fg="white", selectcolor="#0a1428",
                                activebackground="#0a1428", activeforeground="white")
        ia1_easy.pack(side=tk.LEFT, padx=10)
        
        ia1_medium = tk.Radiobutton(ia1_frame, text="Intermédiaire", variable=ia1_var, value=str(self.DIFFICULTY_MEDIUM),
                                  font=('Nova Square', 14), bg="#0a1428", fg="white", selectcolor="#0a1428",
                                  activebackground="#0a1428", activeforeground="white")
        ia1_medium.pack(side=tk.LEFT, padx=10)
        
        ia1_hard = tk.Radiobutton(ia1_frame, text="Difficile", variable=ia1_var, value=str(self.DIFFICULTY_HARD),
                                font=('Nova Square', 14), bg="#0a1428", fg="white", selectcolor="#0a1428",
                                activebackground="#0a1428", activeforeground="white")
        ia1_hard.pack(side=tk.LEFT, padx=10)
        
        # IA2 difficulty selection
        tk.Label(main_frame, text="IA 2 (Bleu):", font=('Nova Square', 16), 
               fg="white", bg="#0a1428").grid(row=1, column=0, sticky='w', pady=10)
        
        ia2_frame = tk.Frame(main_frame, bg="#0a1428")
        ia2_frame.grid(row=1, column=1, pady=10)
        
        ia2_var = tk.StringVar(value=str(self.DIFFICULTY_MEDIUM))
        
        ia2_easy = tk.Radiobutton(ia2_frame, text="Facile", variable=ia2_var, value=str(self.DIFFICULTY_EASY),
                                font=('Nova Square', 14), bg="#0a1428", fg="white", selectcolor="#0a1428",
                                activebackground="#0a1428", activeforeground="white")
        ia2_easy.pack(side=tk.LEFT, padx=10)
        
        ia2_medium = tk.Radiobutton(ia2_frame, text="Intermédiaire", variable=ia2_var, value=str(self.DIFFICULTY_MEDIUM),
                                  font=('Nova Square', 14), bg="#0a1428", fg="white", selectcolor="#0a1428",
                                  activebackground="#0a1428", activeforeground="white")
        ia2_medium.pack(side=tk.LEFT, padx=10)
        
        ia2_hard = tk.Radiobutton(ia2_frame, text="Difficile", variable=ia2_var, value=str(self.DIFFICULTY_HARD),
                                font=('Nova Square', 14), bg="#0a1428", fg="white", selectcolor="#0a1428",
                                activebackground="#0a1428", activeforeground="white")
        ia2_hard.pack(side=tk.LEFT, padx=10)
        
        # Number of matches
        num_matches_frame = tk.Frame(main_frame, bg="#0a1428")
        num_matches_frame.grid(row=2, column=0, columnspan=2, pady=30)
        
        tk.Label(num_matches_frame, text="Nombre de matchs:", font=('Nova Square', 16), 
               fg="white", bg="#0a1428").pack(side=tk.LEFT, padx=10)
        
        self.num_matches_var = tk.StringVar(value=str(self.num_matches))
        
        # Register validation function
        vcmd = (self.root.register(self.validate_numeric_input), '%P')
        
        # Decrement button
        dec_button = tk.Button(num_matches_frame, text="-", 
                             font=('Nova Square', 16),
                             bg="#FFD700", fg="#0a1428",
                             width=2, height=1,
                             command=self.decrement_matches)
        dec_button.pack(side=tk.LEFT, padx=10)
        
        # Entry field for number of matches
        matches_entry = tk.Entry(num_matches_frame, textvariable=self.num_matches_var, 
                               font=('Nova Square', 18, 'bold'), 
                               fg="#FFD700", bg="#1a2438", width=4,
                               justify=tk.CENTER, validate="key", validatecommand=vcmd)
        matches_entry.pack(side=tk.LEFT, padx=10)
        
        # Increment button
        inc_button = tk.Button(num_matches_frame, text="+", 
                             font=('Nova Square', 16),
                             bg="#FFD700", fg="#0a1428",
                             width=2, height=1,
                             command=self.increment_matches)
        inc_button.pack(side=tk.LEFT, padx=10)
        
        # Launch button
        launch_frame = tk.Frame(self.root, bg="#0a1428")
        launch_frame.pack(pady=30)
        
        launch_button = tk.Button(launch_frame, text="LANCER", 
                                font=('Nova Square', 18, 'bold'),
                                bg="#008000", fg="white",
                                width=15, height=1,
                                command=lambda: self.start_batch_simulation(int(ia1_var.get()), int(ia2_var.get())))
        launch_button.pack()
        
        # Back button
        back_button = tk.Button(self.root, text="Retour", 
                              font=('Nova Square', 14),
                              bg="#555555", fg="white",
                              width=15, height=1,
                              command=self.create_main_menu)
        back_button.pack(side=tk.BOTTOM, pady=20)
        
    def validate_numeric_input(self, new_value):
        """Validate that the input is numeric and positive"""
        if new_value == "":
            return True  # Allow empty field temporarily
        
        try:
            value = int(new_value)
            if value > 0:
                return True
            else:
                return False
        except ValueError:
            return False
    
    def increment_matches(self):
        try:
            self.num_matches = int(self.num_matches_var.get()) + 1
        except ValueError:
            self.num_matches = 1  # Default if invalid
        self.num_matches_var.set(str(self.num_matches))
    
    def decrement_matches(self):
        try:
            current_value = int(self.num_matches_var.get())
            if current_value > 1:
                self.num_matches = current_value - 1
                self.num_matches_var.set(str(self.num_matches))
        except ValueError:
            self.num_matches = 1  # Default if invalid
            self.num_matches_var.set(str(self.num_matches))

    def start_batch_simulation(self, ia1_difficulty, ia2_difficulty):
        try:
            num_matches = int(self.num_matches_var.get())
            if num_matches < 1:
                num_matches = 1
        except ValueError:
            num_matches = 1  # Default if invalid
        
        self.num_matches = num_matches
        self.selected_ai1_difficulty = ia1_difficulty
        self.selected_ai2_difficulty = ia2_difficulty
        self.start_game('BatchAI')
    
    def start_game(self, mode):
        """Starts the game with the selected options using the Pygame module"""
        self.selected_mode = mode
        
        # Prepare game parameters
        game_params = {
            'mode': mode,
            'difficulty': self.selected_difficulty,
            'ai1_difficulty': self.selected_ai1_difficulty,
            'ai2_difficulty': self.selected_ai2_difficulty,
            'num_matches': self.num_matches
        }
        
        # Save the game parameters for later use
        self.game_params = game_params
        
        # Close the Tkinter window properly
        self.root.quit()

def launch_menu():
    root = tk.Tk()
    app = QuoridorMenuApp(root)
    root.mainloop()
    
    # Get the saved game parameters
    game_params = getattr(app, 'game_params', None)
    
    # Return the selected options after the Tkinter window is closed
    return game_params

if __name__ == "__main__":
    # Launch the menu first
    game_params = launch_menu()
    
    # Launch the game with the selected options if Tkinter menu was closed properly
    # and not closed by clicking the window's X button
    if game_params and quoridor_game:
        quoridor_game.launch_game(game_params)
