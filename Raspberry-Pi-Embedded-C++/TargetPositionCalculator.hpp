#pragma once

#include <cstdint>
// Forward declarations to avoid circular includes. Include ArmMovement.hpp where definitions are needed.
struct XYZ;
struct JointAngles;



XYZ SquareToXYZ(int col, int row);

JointAngles XYZToJointAngles(const XYZ& position);
