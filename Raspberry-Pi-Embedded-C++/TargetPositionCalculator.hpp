#pragma once

#include <cstdint>
// Forward declarations to avoid circular includes. Include ArmMovement.hpp where definitions are needed.
struct XYZ;
struct JointAngles;



XYZ SquareToXYZ(int col, int row);

JointAngles XYZToJointAngles(const XYZ& position);

// Forward kinematics: given base/shoulder/elbow/wrist joint angles (deg),
// compute the end-effector XYZ position using the same link lengths and
// angle conventions as XYZToJointAngles.
XYZ JointAnglesToXYZ(const JointAngles& angles);
