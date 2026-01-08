from gui import RPSGui

# Temporary score tracking
p_score = 0
a_score = 0

def handle_game_round(user_move):
    global p_score, a_score
    
    # 1. HERE is where you will call ai.predict()
    ai_move = "P" # Placeholder
    
    # 2. Simple logic to test the GUI
    result = "AI Wins!" # Placeholder logic
    a_score += 1
    
    # 3. Tell the GUI to update its labels
    app.update_display(user_move, ai_move, result, p_score, a_score)

if __name__ == "__main__":
    # Create the app and pass it our game function
    app = RPSGui(on_move_callback=handle_game_round)
    app.run()