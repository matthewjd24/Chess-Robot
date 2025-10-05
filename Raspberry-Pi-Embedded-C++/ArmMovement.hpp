#pragma once

// Needed for DxlServo member variables
#include "Dynamixel.hpp"

struct XYZ {
	double x{0.0};
	double y{0.0};
	double z{0.0};
};

struct JointAngles {
    double base{0.0};
    double shoulder{0.0};
    double elbow{0.0};
    double wrist{0.0};
};

class ArmMovement {
public:
    ArmMovement();
    void MoveGripperToTile(int col, int row, double zHeight);
    void MoveGripperToPosition(XYZ position);
    void MoveGripperToJointAngles(JointAngles angles);
    DxlServo BaseServo;
    DxlServo ShoulderServo;
    DxlServo ElbowServo;
    DxlServo WristServo;
};