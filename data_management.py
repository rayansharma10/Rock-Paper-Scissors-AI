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

    def plot_win_rate(self, ax: Optional[plt.Axes] = None, exclude_ties: bool = False, show_draw_rate: bool = True, show_ai_rate: bool = True) -> plt.Axes:
        """Plot cumulative player win rate and (optionally) draw and AI win rates.

        - Player win rate is either p/rounds or p/(p+a) when exclude_ties=True.
        - AI win rate mirrors the player logic.
        - Draw rate is ties/rounds.
        Returns the axes used."""
        # player win history (already supports exclude_ties)
        hist_p = self.win_rate_history(exclude_ties=exclude_ties)

        # compute ai win rate history and draw rate history
        hist_a: List[float] = []
        hist_d: List[float] = []
        p = a = t = 0
        for i, (_, _, res) in enumerate(self.rounds, start=1):
            if res == "player":
                p += 1
            elif res == "ai":
                a += 1
            else:
                t += 1

            if exclude_ties:
                denom = p + a
                hist_p_val = (p / denom) if denom > 0 else 0.0
                hist_a_val = (a / denom) if denom > 0 else 0.0
            else:
                hist_p_val = p / i
                hist_a_val = a / i

            hist_d.append(t / i)
            hist_a.append(hist_a_val)

        if ax is None:
            fig, ax = plt.subplots()
        else:
            # clear existing artists for an in-place redraw
            ax.clear()

        rounds = list(range(1, len(hist_p) + 1))
        # player line
        ax.plot(rounds, hist_p, marker="o", linestyle="-", color="#2c7fb8", label="Player win rate")
        # ai line
        if show_ai_rate and hist_a:
            ax.plot(range(1, len(hist_a) + 1), hist_a, marker="^", linestyle=":", color="#984ea3", label="AI win rate")
        # draw line
        if show_draw_rate and hist_d:
            ax.plot(range(1, len(hist_d) + 1), hist_d, marker="s", linestyle="--", color="#ff7f00", label="Draw rate")

        # dynamic y-limits based on all plotted series
        vals = []
        if hist_p:
            vals.extend(hist_p)
        if hist_a:
            vals.extend(hist_a)
        if hist_d:
            vals.extend(hist_d)

        if vals:
            ymin = max(0.0, min(vals) - 0.05)
            ymax = min(1.0, max(vals) + 0.05)
            if ymax - ymin < 0.01:
                ymin = max(0.0, ymin - 0.02)
                ymax = min(1.0, ymax + 0.02)
            ax.set_ylim(ymin, ymax)

            # annotate last values
            last_x = len(rounds)
            if hist_p:
                ax.annotate(f"P {hist_p[-1]*100:.1f}%", xy=(last_x, hist_p[-1]), xytext=(last_x, hist_p[-1] + (ymax - ymin) * 0.04), ha="center", fontsize=9, color="#2c7fb8")
            if show_ai_rate and hist_a:
                ax.annotate(f"A {hist_a[-1]*100:.1f}%", xy=(last_x, hist_a[-1]), xytext=(last_x, hist_a[-1] - (ymax - ymin) * 0.04), ha="center", fontsize=9, color="#984ea3")
            if show_draw_rate and hist_d:
                ax.annotate(f"D {hist_d[-1]*100:.1f}%", xy=(last_x, hist_d[-1]), xytext=(last_x, hist_d[-1] - (ymax - ymin) * 0.08), ha="center", fontsize=9, color="#ff7f00")
        else:
            ax.set_ylim(0, 1)

        ax.set_xlabel("Round")
        ax.set_ylabel("Rate")
        ax.set_title("Cumulative Rates")
        ax.grid(alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
        return ax

    def plot_last_moves(self, n: int = 7, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Plain-text display of the last `n` rounds (larger text).

        Renders two horizontal text lines (Player and AI). Winner move is green.
        """
        last = self.rounds[-n:]
        pad = n - len(last)
        padded = [None] * pad + last

        if ax is None:
            fig, ax = plt.subplots(figsize=(max(4.0, n * 0.6), 1.8))
        else:
            ax.clear()

        ax.set_xlim(0, n + 1)
        ax.set_ylim(0, 3)
        ax.axis("off")

        # larger monospace font for alignment
        label_font = dict(fontsize=11, fontfamily="monospace", color="#222")
        move_font = dict(fontsize=14, fontfamily="monospace")

        # leading labels
        ax.text(0.2, 2.2, "Player:", ha="left", va="center", **label_font)
        ax.text(0.2, 1.0, "AI:", ha="left", va="center", **label_font)

        # color used to indicate the winner for a round
        win_color = "#4daf4a"

        for i, item in enumerate(padded, start=1):
            if item is None:
                p_text = "-"
                a_text = "-"
                p_color = a_color = "#222"
            else:
                p_text, a_text, res = item
                p_color = a_color = "#222"
                if res == "player":
                    p_color = win_color
                elif res == "ai":
                    a_color = win_color

            ax.text(i, 2.2, p_text, ha="center", va="center", color=p_color, **move_font)
            ax.text(i, 1.0, a_text, ha="center", va="center", color=a_color, **move_font)

        ax.set_title(f"Last {n} rounds", fontsize=10)
        return ax

    def combined_figure(self, n: int = 7, exclude_ties: bool = False) -> matplotlib.figure.Figure:
        """Return a matplotlib Figure containing the win-rate plot and last-moves plot.

        This is convenient for saving or embedding into a GUI canvas.
        """
        fig = plt.figure(constrained_layout=True, figsize=(8, 4.5))
        gs = fig.add_gridspec(2, 1, height_ratios=[2, 1.2])
        ax0 = fig.add_subplot(gs[0, 0])
        ax1 = fig.add_subplot(gs[1, 0])

        self.plot_win_rate(ax=ax0, exclude_ties=exclude_ties)
        self.plot_last_moves(n=n, ax=ax1)

        return fig


__all__ = ["DataManager"]
