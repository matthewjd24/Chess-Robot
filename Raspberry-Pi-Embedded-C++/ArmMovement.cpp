#include "ArmMovement.hpp"
#include "Dynamixel.hpp"
#include "TargetPositionCalculator.hpp"
#include <iostream>

ArmMovement::ArmMovement()
    : BaseServo(1, 256, {200, 80, 30}, -1.0),
      ShoulderServo(2, 177.5, {30, 12, 6}),
      ElbowServo(3, 44, {80, 12, 6}),
      WristServo(4, 231, {80, 12, 6})
{
    BaseServo.SetVelocityAndAcceleration(30, 15);
    ShoulderServo.SetVelocityAndAcceleration(30, 15);
    ElbowServo.SetVelocityAndAcceleration(30, 15);
    WristServo.SetVelocityAndAcceleration(30, 15);
}

void ArmMovement::MoveGripperToPosition(XYZ position) {
    // convert position to joint angles
    // set joint angles

    // BaseServo.SetPosition(0.0);
    // ShoulderServo.SetPosition(-10.0);
    // ElbowServo.SetPosition(130.0);
    // WristServo.SetPosition(0.0);
}

void ArmMovement::MoveGripperToJointAngles(JointAngles angles) {
    // convert position to joint angles
    // set joint angles

    BaseServo.SetPosition(angles.base);
    ShoulderServo.SetPosition(angles.shoulder);
    ElbowServo.SetPosition(angles.elbow);
    WristServo.SetPosition(angles.wrist);
}

JointAngles ArmMovement::GetTargetAngles(int col, int row, double zHeight){
    if(col == 0){
        XYZ position = {0.0, 5.0, 6.5};
        JointAngles ja = XYZToJointAngles(position);
        std::cout << "Position: " << position.x << ", " << position.y << ", " << position.z << std::endl;
        return ja;
    }
    else {
        zHeight += 5.2;
        XYZ position = SquareToXYZ(col, row);
        position.z += zHeight;
        std::cout << "Position: " << position.x << ", " << position.y << ", " << position.z << std::endl;
        JointAngles ja = XYZToJointAngles(position);
        return ja;
    }
}

void ArmMovement::MoveGripperToTile(int col, int row, double zHeight) {
    JointAngles ja = GetTargetAngles(col, row, zHeight);
    MoveGripperToJointAngles(ja);
}

JointAngles ArmMovement::GetCurrentAngles(){
    JointAngles ja;
    ja.base = BaseServo.GetPresentPositionDegrees();
    ja.shoulder = ShoulderServo.GetPresentPositionDegrees();
    ja.elbow = ElbowServo.GetPresentPositionDegrees();
    ja.wrist = WristServo.GetPresentPositionDegrees();
    return ja;
}

void ArmMovement::DisableTorqueAllServos() {
    BaseServo.DisableTorque();
    ShoulderServo.DisableTorque();
    ElbowServo.DisableTorque();
    WristServo.DisableTorque();
}

void ArmMovement::EnableTorqueAllServos() {
    BaseServo.EnableTorque();
    ShoulderServo.EnableTorque();
    ElbowServo.EnableTorque();
    WristServo.EnableTorque();
}