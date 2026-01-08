import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class RPSGui:
    def __init__(self, on_move_callback, data_manager=None):
        """
        on_move_callback: A function from main.py that handles the game logic
        data_manager: optional DataManager instance to show live stats
        """
        self.root = tk.Tk()
        self.root.title("AI Pattern Learner - RPS")
        self.root.geometry("650x500")
        self.on_move_callback = on_move_callback
        self.data_manager = data_manager

        # UI Styles
        self.font_main = ("Helvetica", 12)
        self.font_header = ("Helvetica", 16, "bold")

        self._setup_ui()

    def _setup_ui(self):
        # top header
        header = tk.Label(self.root, text="Can you beat the AI?", font=self.font_header)
        header.pack(pady=(10, 0))

        # main content: left = controls, right = plot
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=8)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", anchor="n", fill="y", padx=(0, 8))

        self.score_label = tk.Label(left_frame, text="Score: Player 0 - AI 0", font=self.font_main)
        self.score_label.pack()

        # Display area for last round
        self.display_label = tk.Label(
            left_frame,
            text="Make your first move to start learning!",
            font=self.font_main,
            fg="blue",
            wraplength=240,
            justify="center",
        )
        self.display_label.pack(pady=8)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=6)

        # We use lambda to pass the specific move string to our callback
        tk.Button(btn_frame, text="Rock", width=12, height=2,
                  command=lambda: self.on_move_callback("R")).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Paper", width=12, height=2,
                  command=lambda: self.on_move_callback("P")).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Scissors", width=12, height=2,
                  command=lambda: self.on_move_callback("S")).grid(row=0, column=2, padx=5)

        # 4. Stats / Plot area (matplotlib canvas will be inserted here)
        self.plot_frame = tk.Frame(main_frame, bd=1, relief="sunken")
        self.plot_frame.pack(side="right", fill="both", expand=True)

        # create a persistent matplotlib Figure and Axes so we can update in-place
        import matplotlib.pyplot as _plt
        self.fig = _plt.figure(constrained_layout=True, figsize=(6, 4))
        gs = self.fig.add_gridspec(2, 1, height_ratios=[2, 1])
        self.ax0 = self.fig.add_subplot(gs[0, 0])
        self.ax1 = self.fig.add_subplot(gs[1, 0])

        self._figure_canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self._figure_canvas.get_tk_widget().pack(fill="both", expand=True)

        # If a data_manager was passed, draw the initial stats
        if self.data_manager is not None:
            # draw once in-place
            self.update_stats(self.data_manager)

    def update_display(self, player_move, ai_move, result, p_score, a_score):
        """Updates the text on the screen after a round"""
        self.display_label.config(
            text=f"You chose {player_move} | AI chose {ai_move}\nResult: {result}"
        )
        self.score_label.config(text=f"Score: Player {p_score} - AI {a_score}")

    def _embed_figure(self, fig):
        """Legacy helper kept for compatibility but not used when using persistent axes."""
        # If someone passes a full Figure, replace the canvas (not used by default)
        if self._figure_canvas is not None:
            try:
                self._figure_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self._figure_canvas = None

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        self._figure_canvas = canvas

    def update_stats(self, data_manager):
        """Request a combined figure from DataManager and embed it."""
        # update the persistent axes in-place to minimize redraw work
        data_manager.plot_win_rate(ax=self.ax0)
        data_manager.plot_last_moves(n=3, ax=self.ax1)

        # efficient redraw
        try:
            # force an immediate draw so the GUI updates right away
            self._figure_canvas.draw()
            # ensure Tk processes redraw events
            self._figure_canvas.get_tk_widget().update_idletasks()
        except Exception:
            # fallback to full embed if something goes wrong
            fig = data_manager.combined_figure()
            self._embed_figure(fig)

    def run(self):
        self.root.mainloop()