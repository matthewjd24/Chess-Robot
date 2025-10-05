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

    void ResetStartPosition();

    std::string ConvertToFEN() const;

    std::string RunAnalysisOfBoard(const std::vector<TileAnalysis>& analyses);

    const std::array<std::array<char, 9>, 9>& board() const { return board_; }

    std::string responseMove;


private:
    std::array<std::array<char, 9>, 9> board_{}; // empty squares are '\0'
};
