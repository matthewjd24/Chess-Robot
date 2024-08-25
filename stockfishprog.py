import chess
import chess.engine

def board_to_fen(board_array):
    fen = ""

    for row in reversed(range(1,9)):
        empty_count = 0
        for col in range(1,9):
            square = board_array[col][row]
            if square == "":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                is_white = square[0] == 'w'
                letter = square[1]
                if(is_white):
                    letter = letter.upper()
                fen += letter
        if empty_count > 0:
            fen += str(empty_count)
        fen += "/"
    
    # Remove the trailing slash
    fen = fen[:-1] + " b KQkq - 0 2"
    fen = "k7" + fen[1:]
    
    return fen

def stockfish_recommended_move(board_fen, time_limit=0.1):
    board = chess.Board(board_fen)
    engine = chess.engine.SimpleEngine.popen_uci("C:\\Projects\\stockfish\\stockfish-windows-x86-64.exe")
    best_move = engine.play(board, chess.engine.Limit(time=time_limit))
    info = engine.analyse(board, chess.engine.Limit(time=time_limit))
    score_display = "error with score display"
    score = info['score'].relative
    if score.is_mate():
        # If it's a mate score, display it as mate in X moves
        score_display = f"M{score.mate()}"
    else:
        # Otherwise, convert centipawn to a pawn-based score
        score_display = score.score() / 100.0  # Convert to 'pawns'
        score_display = f"{score_display:.2f}"  # Format to 2 decimal places
    
    engine.quit()
    return best_move.move, score_display


# Get the recommended move
#recommended_move = stockfish_recommended_move("rnbBkbnr/ppp3pp/3pp3/5p2/3P4/5N2/PPP1PPPP/RN1QKB1R b KQkq - 0 1")
#print(recommended_move)
