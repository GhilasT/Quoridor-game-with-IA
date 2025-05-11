import tkinter as tk
from tkinter import ttk
import sys
import os
import importlib.util
import threading

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
        
        # Add progress tracking attributes
        self.progress_window = None
        self.progress_var = None
        self.progress_label = None
        self.progress_count_label = None
        self.result_text = None
        self.batch_thread = None
        
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
        
        # Instead of directly starting the game, create a progress window
        self.show_progress_window(num_matches, ia1_difficulty, ia2_difficulty)
        
    def show_progress_window(self, num_matches, ia1_difficulty, ia2_difficulty):
        """Create and show a progress window for batch simulations"""
        # Create a new top level window
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Simulation en cours")
        self.progress_window.configure(bg="#0a1428")
        self.progress_window.geometry("500x350")
        self.progress_window.transient(self.root)  # Make it a child of the main window
        self.progress_window.grab_set()  # Make it modal
        
        # Set difficulty names for display
        difficulty_names = {
            self.DIFFICULTY_EASY: "Facile",
            self.DIFFICULTY_MEDIUM: "Intermédiaire",
            self.DIFFICULTY_HARD: "Difficile"
        }
        ia1_name = difficulty_names.get(ia1_difficulty, "Inconnu")
        ia2_name = difficulty_names.get(ia2_difficulty, "Inconnu")
        
        # Title
        title_label = tk.Label(
            self.progress_window, 
            text=f"Simulation: {ia1_name} vs {ia2_name}", 
            font=('Nova Square', 18, 'bold'),
            bg="#0a1428",
            fg="#FFD700"
        )
        title_label.pack(pady=(20, 30))
        
        # Match counter
        self.progress_count_label = tk.Label(
            self.progress_window,
            text=f"Match: 0/{num_matches}",
            font=('Nova Square', 16),
            bg="#0a1428",
            fg="white"
        )
        self.progress_count_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            self.progress_window,
            variable=self.progress_var,
            maximum=num_matches,
            length=400,
            mode='determinate'
        )
        progress_bar.pack(pady=20)
        
        # Status label
        self.progress_label = tk.Label(
            self.progress_window,
            text="Initialisation...",
            font=('Nova Square', 14),
            bg="#0a1428",
            fg="#FFD700"
        )
        self.progress_label.pack(pady=(10, 20))
        
        # Results text widget
        self.result_text = tk.Text(
            self.progress_window,
            width=50,
            height=6,
            font=('Nova Square', 12),
            bg="#1a2438",
            fg="white"
        )
        self.result_text.pack(pady=10)
        self.result_text.insert(tk.END, "Les résultats apparaîtront ici à la fin de la simulation.\n")
        self.result_text.config(state=tk.DISABLED)  # Make it read-only initially
        
        # Now prepare the game parameters
        game_params = {
            'mode': 'BatchAI',
            'difficulty': self.selected_difficulty,
            'ai1_difficulty': ia1_difficulty,
            'ai2_difficulty': ia2_difficulty,
            'num_matches': num_matches,
            'progress_callback': self.update_progress,
            'result_callback': self.show_batch_results
        }
        
        # Save the game parameters for later use
        self.game_params = game_params
        
        # Start the simulation in a separate thread
        self.batch_thread = threading.Thread(target=self.run_batch_simulation, args=(game_params,))
        self.batch_thread.daemon = True
        self.batch_thread.start()
        
    def run_batch_simulation(self, game_params):
        """Run the batch simulation by calling the Pygame module"""
        try:
            # We're checking if the quoridor_game module is available
            if not hasattr(quoridor_game, "run_batch_simulations_with_progress"):
                self.progress_label.config(text="Erreur: fonction de simulation introuvable")
                return
                
            # Run the batch simulation with progress updates
            quoridor_game.run_batch_simulations_with_progress(
                game_params['ai1_difficulty'],
                game_params['ai2_difficulty'],
                game_params['num_matches'],
                game_params['progress_callback'],
                game_params['result_callback']
            )
        except Exception as e:
            self.progress_label.config(text=f"Erreur: {str(e)}")
            
    def update_progress(self, current_match, total_matches, status_text="En cours..."):
        """Update the progress bar and labels"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_var.set(current_match)
            self.progress_count_label.config(text=f"Match: {current_match}/{total_matches}")
            self.progress_label.config(text=status_text)
            # Force update the window
            self.progress_window.update_idletasks()
            
    def show_batch_results(self, results):
        """Show the batch simulation results"""
        if not self.progress_window or not self.progress_window.winfo_exists():
            return
            
        # Update status
        self.progress_label.config(text="Simulation terminée!")
        
        # Update results text
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # Format results
        difficulty_names = {
            self.DIFFICULTY_EASY: "Facile",
            self.DIFFICULTY_MEDIUM: "Intermédiaire",
            self.DIFFICULTY_HARD: "Difficile"
        }
        ia1_name = difficulty_names.get(self.selected_ai1_difficulty, "IA1")
        ia2_name = difficulty_names.get(self.selected_ai2_difficulty, "IA2")
        
        # Add results text
        self.result_text.insert(tk.END, f"Résultats finaux:\n")
        total = sum(results.values())
        if total > 0:
            self.result_text.insert(tk.END, f"- {ia1_name}: {results[1]} victoires ({results[1]/total*100:.1f}%)\n")
            self.result_text.insert(tk.END, f"- {ia2_name}: {results[2]} victoires ({results[2]/total*100:.1f}%)\n")
            self.result_text.insert(tk.END, f"- Matchs nuls: {results[0]} ({results[0]/total*100:.1f}%)\n")
        else:
            self.result_text.insert(tk.END, "Aucun match n'a été complété avec succès.\n")
        self.result_text.config(state=tk.DISABLED)
        
        # Add a close button
        close_button = tk.Button(
            self.progress_window,
            text="Fermer",
            font=('Nova Square', 14),
            bg="#FFD700",
            fg="#0a1428",
            command=self.progress_window.destroy
        )
        close_button.pack(pady=20)
        
        # Set the window to remain open until manually closed
        self.progress_window.protocol("WM_DELETE_WINDOW", self.progress_window.destroy)
    
    def start_game(self, mode):
        """
        Start the game with the selected mode and parameters
        
        Args:
            mode: Game mode ('PVP', 'PVE', or 'AIvsAI')
        """
        game_params = {
            'mode': mode,
            'difficulty': self.selected_difficulty
        }
        
        # For AI vs AI mode, we need to pass both AI difficulties
        if mode == 'AIvsAI':
            game_params.update({
                'ai1_difficulty': self.selected_ai1_difficulty,
                'ai2_difficulty': self.selected_ai2_difficulty
            })
            
        # Save the parameters for later use by the launcher
        self.game_params = game_params
        
        # Close the Tkinter window to allow Pygame to take focus
        # Unless this is a batch simulation which needs the Tkinter window
        if mode != 'BatchAI':
            self.root.destroy()
        
        # The launcher will pick up the game_params and start the game

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
