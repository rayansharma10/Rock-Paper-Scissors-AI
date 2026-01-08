"""Quick smoke test for data_management.DataManager

Run this script to generate `sample_stats.png` in the repo root.
"""
from data_management import DataManager


def main():
    dm = DataManager()
    sample = [
        ("R", "P"),  # ai wins
        ("P", "P"),  # tie
        ("S", "P"),  # player wins
        ("R", "S"),  # player wins
        ("S", "R"),  # ai wins
    ]
    for p, a in sample:
        dm.record_round(p, a)

    fig = dm.combined_figure(n=3)
    fig.savefig("sample_stats.png", dpi=150)
    print("Wrote sample_stats.png")


if __name__ == "__main__":
    main()
