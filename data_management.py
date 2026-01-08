"""data_management.py
Modular tracking and plotting utilities for Rock-Paper-Scissors.

Public API:
- DataManager: record rounds, compute win rates, and produce matplotlib figures.
"""
from typing import List, Tuple, Optional
import re
import matplotlib
import matplotlib.pyplot as plt

MOVE_SET = {"R", "P", "S"}
MOVE_COLOR = {"R": "#e41a1c", "P": "#377eb8", "S": "#4daf4a"}


class DataManager:
    """Tracks rounds and provides plotting helpers.

    Design goals:
    - Keep internal state small and serializable (list of simple tuples).
    - Provide plotting functions that accept an optional `ax` so they can be
      embedded in a larger figure or UI later.
    """

    def __init__(self) -> None:
        # rounds: list of tuples (player_move, ai_move, result_str)
        # result_str: 'player', 'ai', or 'tie'
        self.rounds: List[Tuple[str, str, str]] = []

    def record_round(self, player_move: str, ai_move: str, result: Optional[str] = None) -> None:
        """Record a completed round.

        player_move and ai_move should be 'R', 'P', or 'S'. If `result` is not
        provided, it will be inferred using standard RPS rules.
        """
        player_move = player_move.upper()
        ai_move = ai_move.upper()
        if player_move not in MOVE_SET or ai_move not in MOVE_SET:
            raise ValueError("Moves must be one of 'R', 'P', or 'S'")

        if result is None:
            result_norm = self._infer_result(player_move, ai_move)
        else:
            result_norm = self._normalize_result_string(result)

        self.rounds.append((player_move, ai_move, result_norm))

    def _infer_result(self, player: str, ai: str) -> str:
        if player == ai:
            return "tie"
        beats = {"R": "S", "P": "R", "S": "P"}
        if beats[player] == ai:
            return "player"
        return "ai"

    def _normalize_result_string(self, result: str) -> str:
        # normalize by removing punctuation and checking keywords
        r = result.strip().lower()
        r_clean = re.sub(r"[^a-z ]", "", r)

        # player indicators
        if (
            "player" in r_clean
            or r_clean == "p"
            or ("you" in r_clean and "win" in r_clean)
            or "player wins" in r_clean
            or "you win" in r_clean
            or ("win" in r_clean and "ai" not in r_clean and "lose" not in r_clean)
        ):
            return "player"

        # ai indicators
        if (
            "ai" in r_clean
            or r_clean == "a"
            or "computer" in r_clean
            or ("you" in r_clean and "lose" in r_clean)
            or "ai wins" in r_clean
        ):
            return "ai"

        return "tie"

    def counts(self) -> Tuple[int, int, int]:
        """Return (player_wins, ai_wins, ties)"""
        p = sum(1 for _, _, res in self.rounds if res == "player")
        a = sum(1 for _, _, res in self.rounds if res == "ai")
        t = sum(1 for _, _, res in self.rounds if res == "tie")
        return p, a, t

    def win_rate_history(self, exclude_ties: bool = False) -> List[float]:
        """Return cumulative player win rate after each round.

        If exclude_ties is True, ties are not counted in the denominator.
        """
        history: List[float] = []
        p = 0
        a = 0
        t = 0
        for i, (_, _, res) in enumerate(self.rounds, start=1):
            if res == "player":
                p += 1
            elif res == "ai":
                a += 1
            else:
                t += 1

            if exclude_ties:
                denom = p + a
                history.append((p / denom) if denom > 0 else 0.0)
            else:
                history.append(p / i)
        return history

    def plot_win_rate(self, ax: Optional[plt.Axes] = None, exclude_ties: bool = False) -> plt.Axes:
        """Plot cumulative player win rate over rounds. Returns the axes used."""
        hist = self.win_rate_history(exclude_ties=exclude_ties)
        if ax is None:
            fig, ax = plt.subplots()
        else:
            # clear existing artists for an in-place redraw
            ax.clear()
        ax.plot(range(1, len(hist) + 1), hist, marker="o", linestyle="-", color="#2c7fb8")
        # dynamic y-limits that stay within [0,1] but give a little padding
        if hist:
            ymin = max(0.0, min(hist) - 0.05)
            ymax = min(1.0, max(hist) + 0.05)
            # if flat line (ymin==ymax), expand a tiny bit
            if ymax - ymin < 0.01:
                ymin = max(0.0, ymin - 0.02)
                ymax = min(1.0, ymax + 0.02)
            ax.set_ylim(ymin, ymax)
            # annotate last value
            last_x = len(hist)
            last_y = hist[-1]
            ax.annotate(f"{last_y*100:.1f}%", xy=(last_x, last_y), xytext=(last_x, last_y + (ymax - ymin) * 0.04),
                        ha="center", fontsize=9, color="#2c7fb8")
        else:
            ax.set_ylim(0, 1)
        ax.set_xlabel("Round")
        ax.set_ylabel("Player win rate")
        ax.set_title("Cumulative Player Win Rate")
        ax.grid(alpha=0.3)
        return ax

    def plot_last_moves(self, n: int = 3, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Compact, text-based display of the last `n` moves for player and AI.

        This renders small colored text boxes for each move; intended to be
        visually small when embedded in the UI.
        """
        last = self.rounds[-n:]
        pad = n - len(last)
        padded = [None] * pad + last

        if ax is None:
            # keep the subplot compact
            fig, ax = plt.subplots(figsize=(max(1.2, n * 0.9), 0.9))
        else:
            # clear for in-place redraw
            ax.clear()

        ax.set_xlim(0.5, n + 0.5)
        ax.set_ylim(0, 2)
        ax.axis('off')

        # draw small text boxes: top row = Player, bottom row = AI
        for i, item in enumerate(padded, start=1):
            if item is None:
                p_text = '-'
                a_text = '-'
                p_color = '#ddd'
                a_color = '#ddd'
            else:
                p_text, a_text, _ = item
                p_color = MOVE_COLOR.get(p_text, '#999')
                a_color = MOVE_COLOR.get(a_text, '#999')

            # player (top)
            ax.text(i, 1.6, p_text, ha='center', va='center', fontsize=9,
                    color='white', fontweight='bold',
                    bbox=dict(facecolor=p_color, edgecolor='none', boxstyle='round,pad=0.2'))
            # label small 'P' above the player boxes
            ax.text(i, 1.85, 'P', ha='center', va='center', fontsize=7, color='#444')

            # ai (bottom)
            ax.text(i, 0.6, a_text, ha='center', va='center', fontsize=9,
                    color='white', fontweight='bold',
                    bbox=dict(facecolor=a_color, edgecolor='none', boxstyle='round,pad=0.2'))
            # label small 'A' below the ai boxes
            ax.text(i, 0.35, 'A', ha='center', va='center', fontsize=7, color='#444')

        ax.set_title(f"Last {n} moves", fontsize=9)
        return ax

    def combined_figure(self, n: int = 3, exclude_ties: bool = False) -> matplotlib.figure.Figure:
        """Return a matplotlib Figure containing the win-rate plot and last-moves plot.

        This is convenient for saving or embedding into a GUI canvas.
        """
        fig = plt.figure(constrained_layout=True, figsize=(6, 4))
        gs = fig.add_gridspec(2, 1, height_ratios=[2, 1])
        ax0 = fig.add_subplot(gs[0, 0])
        ax1 = fig.add_subplot(gs[1, 0])

        self.plot_win_rate(ax=ax0, exclude_ties=exclude_ties)
        self.plot_last_moves(n=n, ax=ax1)

        return fig


__all__ = ["DataManager"]
