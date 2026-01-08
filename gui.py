import tkinter as tk
from tkinter import ttk

class RPSGui:
    def __init__(self, on_move_callback):
        """
        on_move_callback: A function from main.py that handles the game logic
        """
        self.root = tk.Tk()
        self.root.title("AI Pattern Learner - RPS")
        self.root.geometry("450x400")
        self.on_move_callback = on_move_callback
        
        # UI Styles
        self.font_main = ("Helvetica", 12)
        self.font_header = ("Helvetica", 16, "bold")
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. Header & Scores
        tk.Label(self.root, text="Can you beat the AI?", font=self.font_header).pack(pady=10)
        
        self.score_label = tk.Label(self.root, text="Score: Player 0 - AI 0", font=self.font_main)
        self.score_label.pack()

        # 2. Display Area (Result of the last round)
        self.display_label = tk.Label(
            self.root, 
            text="Make your first move to start learning!", 
            font=self.font_main, 
            fg="blue",
            wraplength=350
        )
        self.display_label.pack(pady=30)

        # 3. Control Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        # We use lambda to pass the specific move string to our callback
        tk.Button(btn_frame, text="Rock", width=12, height=2, 
                  command=lambda: self.on_move_callback("R")).grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="Paper", width=12, height=2, 
                  command=lambda: self.on_move_callback("P")).grid(row=0, column=1, padx=5)
        
        tk.Button(btn_frame, text="Scissors", width=12, height=2, 
                  command=lambda: self.on_move_callback("S")).grid(row=0, column=2, padx=5)

    def update_display(self, player_move, ai_move, result, p_score, a_score):
        """Updates the text on the screen after a round"""
        self.display_label.config(
            text=f"You chose {player_move} | AI chose {ai_move}\nResult: {result}"
        )
        self.score_label.config(text=f"Score: Player {p_score} - AI {a_score}")

    def run(self):
        self.root.mainloop()