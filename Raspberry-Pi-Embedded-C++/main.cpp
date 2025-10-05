#include <iostream>
#include <chrono>
#include <thread>
#include "dynamixel.hpp"
#include "board_state_tracker.hpp"
#include "target_position_calculator.hpp"
using namespace std;

// Copy to pi:
// scp -r "C:\Users\matt\Documents\GitHub\Chess-Robot\Raspberry-Pi-Embedded-C++\."  matt@10.0.0.188:/home/matt/Chess-Robot/Cpp
// I copy files to the pi instead of remotely accessing the pi folder with VSCode because the pi makes annoying sounds when I do that :)
// Compile on Pi:
// cmake ..; make


int main() {
    cout << "Hello, Raspberry Pi!" << endl;
    cout << SquareToXYZ(8,8).x << "," << SquareToXYZ(8,8).y << "," << SquareToXYZ(8,8).z << endl;
    return 0;

    DxlServo base_servo(1, -102.5, {200, 80, 30});
    DxlServo shoulder_servo(2, 175, {30, 12, 6});
    DxlServo elbow_servo(3, 45, {80, 12, 6});
    DxlServo wrist_servo(4, 227, {80, 12, 6});
    base_servo.set_velocity_and_acceleration(50, 20);
    shoulder_servo.set_velocity_and_acceleration(50, 20);
    elbow_servo.set_velocity_and_acceleration(50, 20);
    wrist_servo.set_velocity_and_acceleration(50, 20);


    base_servo.set_position(0.0);
    shoulder_servo.set_position(-10.0);
    elbow_servo.set_position(130.0);
    wrist_servo.set_position(0.0);

    std::this_thread::sleep_for(std::chrono::milliseconds(2000));

    base_servo.close();
    shoulder_servo.close();
    elbow_servo.close();
    wrist_servo.close();
    return 0;
}