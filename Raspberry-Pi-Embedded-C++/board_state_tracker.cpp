#include "board_state_tracker.hpp"

#include <algorithm>
#include <sstream>

BoardStateTracker::BoardStateTracker() {
    // Initialize all to empty
    for (int i = 0; i <= 8; ++i) {
        for (int j = 0; j <= 8; ++j) board_[i][j] = '\0';
    }
    reset_start_position();
}

void BoardStateTracker::reset_start_position() {
    // clear
    for (int i = 1; i <= 8; ++i) for (int j = 1; j <= 8; ++j) board_[i][j] = '\0';

    // White pieces uppercase on ranks 1-2
    board_[1][1] = 'R'; 
    board_[1][2] = 'N'; 
    board_[1][3] = 'B'; 
    board_[1][4] = 'Q';
    board_[1][5] = 'K'; 
    board_[1][6] = 'B'; 
    board_[1][7] = 'N'; 
    board_[1][8] = 'R';
    for (int j = 1; j <= 8; ++j) board_[2][j] = 'P';

    // Black pieces lowercase on ranks 7-8
    board_[8][1] = 'r'; 
    board_[8][2] = 'n'; 
    board_[8][3] = 'b'; 
    board_[8][4] = 'q';
    board_[8][5] = 'k'; 
    board_[8][6] = 'b'; 
    board_[8][7] = 'n'; 
    board_[8][8] = 'r';
    for (int j = 1; j <= 8; ++j) board_[7][j] = 'p';
}

std::string BoardStateTracker::convert_to_fen() const {
    std::ostringstream fen;
    fen << "position fen ";

    for (int row = 8; row >= 1; --row) {
        int emptyCount = 0;
        for (int col = 1; col <= 8; ++col) {
            char piece = board_[row][col];
            if (piece == '\0') {
                emptyCount++;
            } else {
                if (emptyCount > 0) {
                    fen << emptyCount;
                    emptyCount = 0;
                }
                fen << piece;
            }
        }
        if (emptyCount > 0) fen << emptyCount;
        if (row > 1) fen << '/';
    }

    fen << " b KQkq - 0 1";
    return fen.str();
}

std::string BoardStateTracker::run_analysis_of_board(const std::vector<TileAnalysis>& analyses) {
    return "Not implemented";
}
