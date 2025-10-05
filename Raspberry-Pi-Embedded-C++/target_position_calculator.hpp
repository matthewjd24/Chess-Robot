#pragma once

#include <cstdint>

// Minimal 3D coordinate type
struct XYZ {
	double x{0.0};
	double y{0.0};
	double z{0.0};
};

XYZ SquareToXYZ(int col, int row);


