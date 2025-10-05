#include "target_position_calculator.hpp"

XYZ SquareToXYZ(int col, int row) {
    double firstColX = -6.224;
    double firstRowY = 5.983;
    double boardZ = -4.02;

    double interSquareDistance = 1.7756;

    XYZ result;
    result.x = firstColX + (col - 1) * interSquareDistance;
    result.y = firstRowY + (row - 1) * interSquareDistance;
    result.z = boardZ;
    return result;
}