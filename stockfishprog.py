import chess
import chess.engine

def stockfish_recommended_move(board, time_limit=0.1):
    # Start the Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci("C:\\Projects\\stockfish\\stockfish-windows-x86-64.exe")
    
    # Get the best move recommended by Stockfish
    result = engine.play(board, chess.engine.Limit(time=time_limit))
    
    # Close the engine
    engine.quit()
    
    return result.move

# Initialize the board with the starting position
board = chess.Board("rnbBkbnr/ppp3pp/3pp3/5p2/3P4/5N2/PPP1PPPP/RN1QKB1R b KQkq - 0 1")

# Get the recommended move
recommended_move = stockfish_recommended_move(board)
print(recommended_move)
