#include "ArmMovement.hpp"
#include "Dynamixel.hpp"
#include "TargetPositionCalculator.hpp"
#include <iostream>

ArmMovement::ArmMovement()
    : BaseServo(1, -102.5, {200, 80, 30}),
      ShoulderServo(2, 175, {30, 12, 6}),
      ElbowServo(3, 45, {80, 12, 6}),
      WristServo(4, 227, {80, 12, 6})
{
    BaseServo.SetVelocityAndAcceleration(50, 20);
    ShoulderServo.SetVelocityAndAcceleration(50, 20);
    ElbowServo.SetVelocityAndAcceleration(50, 20);
    WristServo.SetVelocityAndAcceleration(50, 20);
}

void ArmMovement::MoveGripperToPosition(XYZ position) {
    // convert position to joint angles
    // set joint angles

    BaseServo.SetPosition(0.0);
    ShoulderServo.SetPosition(-10.0);
    ElbowServo.SetPosition(130.0);
    WristServo.SetPosition(0.0);
}

void ArmMovement::MoveGripperToJointAngles(JointAngles angles) {
    // convert position to joint angles
    // set joint angles

    BaseServo.SetPosition(angles.base);
    ShoulderServo.SetPosition(angles.shoulder);
    ElbowServo.SetPosition(angles.elbow);
    WristServo.SetPosition(angles.wrist);
}

void ArmMovement::MoveGripperToTile(int col, int row, double zHeight) {
    XYZ position = SquareToXYZ(col, row);
    std::cout << "Position: " << position.x << ", " << position.y << ", " << position.z << std::endl;
    JointAngles ja = XYZToJointAngles(position);
    std::cout << "Angles: " << ja.base << ", " << ja.shoulder << ", " << ja.elbow << ", " << ja.wrist << std::endl;
    MoveGripperToJointAngles(ja);
}