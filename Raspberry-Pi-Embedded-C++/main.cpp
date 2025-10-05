using namespace std;
#include <iostream>
#include <chrono>
#include <thread>
//#include "Dynamixel.hpp"
//#include "BoardStateTracker.hpp"
//#include "TargetPositionCalculator.hpp"
#include "ArmMovement.hpp"

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

    armMovement.MoveGripperToTile(1, 1, 0.0);
    std::this_thread::sleep_for(std::chrono::milliseconds(2000));

    armMovement.BaseServo.Close();
    armMovement.ShoulderServo.Close();
    armMovement.ElbowServo.Close();
    armMovement.WristServo.Close();
    return 0;
}