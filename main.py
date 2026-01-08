from gui import RPSGui
from data_management import DataManager

# Temporary score tracking
p_score = 0
a_score = 0

# create a shared DataManager
dm = DataManager()

def handle_game_round(user_move):
    global p_score, a_score

    # 1. HERE is where you will call ai.predict()
    ai_move = "P" # Placeholder

    # 2. Simple logic to test the GUI
    if user_move == ai_move:
        result = "It's a Tie!"
    elif (user_move == "R" and ai_move == "S") or (user_move == "S" and ai_move == "P") or (user_move == "P" and ai_move == "R"):
        result = "You Win!"
        p_score += 1
    else:
        result = "AI Wins!"
        a_score += 1

    # record round in DataManager (normalize result to 'player'|'ai'|'tie')
    dm.record_round(user_move, ai_move, result)

    # 3. Tell the GUI to update its labels
    app.update_display(user_move, ai_move, result, p_score, a_score)

    # 4. Update live stats plot
    app.update_stats(dm)

if __name__ == "__main__":
    # Create the app and pass it our game function and DataManager
    app = RPSGui(on_move_callback=handle_game_round, data_manager=dm)
    app.run()