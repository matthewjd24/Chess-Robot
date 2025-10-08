using namespace std;
#include <iostream>
#include <chrono>
#include <thread>
//#include "Dynamixel.hpp"
//#include "BoardStateTracker.hpp"
#include "ArmMovement.hpp"
#include "TargetPositionCalculator.hpp"

// Copy to pi:
// scp -r "C:\Users\matt\Documents\GitHub\Chess-Robot\Raspberry-Pi-Embedded-C++\."  matt@10.0.0.188:/home/matt/Chess-Robot/Cpp
// I copy files to the pi instead of remotely accessing the pi folder with VSCode because the pi makes annoying sounds when I do that :)
// Compile on Pi:
// cmake ..; make

enum class RobotState : uint8_t { WaitingForButtonPress = 0, Moving = 1 };

int main() {

    cout << "Hello, Raspberry Pi!" << endl;
    //cout << SquareToXYZ(8,8).x << "," << SquareToXYZ(8,8).y << "," << SquareToXYZ(8,8).z << endl;
    ArmMovement armMovement;

    bool buttonPressed = false;
    if (buttonPressed){
        // do turn
        // update board state
        // decide move
        // move arm

        buttonPressed = false;
    }

    int targetCol = 0;
    int targetRow = 0;
    double targetZ = 0.5;

    //JointAngles ja = armMovement.GetTargetAngles(targetCol, targetRow, targetZ);
    //armMovement.MoveGripperToTile(targetCol, targetRow, targetZ);
    // JointAngles ja = {0.0, 0.0, 90.0, 90.0};
    // armMovement.MoveGripperToJointAngles(ja);

    armMovement.DisableTorqueAllServos();
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    double counter = 0.0;
    while(true){
        JointAngles ja = armMovement.GetCurrentAngles();
        XYZ pos = JointAnglesToXYZ(ja);
        //cout << "Angle: " << ja.base << endl;
        cout << "Position: " << pos.x << ", " << pos.y << ", " << pos.z << endl;

        // cout << "Base - Target: " << ja.base << ", Actual: " << base << endl;
        // cout << "Shoulder - Target: " << ja.shoulder << ", Actual: " << shoulder << endl;
        // cout << "Elbow - Target: " << ja.elbow << ", Actual: " << elbow << endl;
        // cout << "Wrist - Target: " << ja.wrist << ", Actual: " << wrist << endl;
        // cout << "-----" << endl;
        // cout << "Base - Current: " << ja.base << endl;
        // cout << "Shoulder - Current: " << ja.shoulder << endl;
        // cout << "Elbow - Current: " << ja.elbow << endl;
        // cout << "Wrist - Current: " << ja.wrist << endl;
        // cout << "-----" << endl;
        counter += 0.2;
         //if (counter > 5.0) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    armMovement.BaseServo.Close();
    armMovement.ShoulderServo.Close();
    armMovement.ElbowServo.Close();
    armMovement.WristServo.Close();
    return 0;
}