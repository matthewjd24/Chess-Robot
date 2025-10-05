#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

enum class PieceColor : uint8_t { None = 0, White = 1, Black = 2 };

struct TileAnalysis {
    PieceColor pieceOnTile{PieceColor::None};
};

class BoardStateTracker {
public:
    BoardStateTracker();

    void reset_start_position();

    std::string convert_to_fen() const;

    std::string run_analysis_of_board(const std::vector<TileAnalysis>& analyses);

    const std::array<std::array<char, 9>, 9>& board() const { return board_; }

    std::string responseMove;


private:
    std::array<std::array<char, 9>, 9> board_{}; // empty squares are '\0'
};
