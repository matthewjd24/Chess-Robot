// handles low level control of the servos in the joints of the arm

#ifndef DYNAMIXEL_HPP
#define DYNAMIXEL_HPP

#include <dynamixel_sdk/dynamixel_sdk.h>
#include <string>
#include <array>
#include <iostream>
#include <thread>
#include <chrono>
#include <cmath>
#include <limits>

class DxlServo {
public:
    static constexpr int ADDR_POSITION_P_GAIN = 84;
    static constexpr int ADDR_POSITION_I_GAIN = 82;
    static constexpr int ADDR_POSITION_D_GAIN = 80;
    static constexpr int ADDR_PROFILE_VELOCITY = 112;
    static constexpr int ADDR_PROFILE_ACCELERATION = 108;
    static constexpr int ADDR_GOAL_VELOCITY = 104;
    static constexpr int ADDR_OPERATING_MODE = 11;
    static constexpr int ADDR_GOAL_POSITION = 116;
    static constexpr int ADDR_PRESENT_POSITION = 132;
    static constexpr int ADDR_TORQUE_ENABLE = 64;
    static constexpr int ADDR_GOAL_PWM = 100;
    static constexpr int ADDR_PRESENT_PWM = 124;

    static constexpr uint8_t OPERATING_MODE_TORQUE = 0;
    static constexpr uint8_t OPERATING_MODE_VELOCITY = 1;
    static constexpr uint8_t OPERATING_MODE_POSITION = 3;

    static constexpr uint8_t TORQUE_ENABLE = 1;
    static constexpr uint8_t TORQUE_DISABLE = 0;

    DxlServo(uint8_t dxl_id, double offset_deg, std::array<int, 3> speeds, double multiplier = 1.0,
             uint8_t operating_mode = OPERATING_MODE_POSITION, const std::string& port_name = "/dev/ttyUSB0",
             int baud_rate = 57600, float protocol_version = 2.0f);

    ~DxlServo();

    void Initialize();
    void TorqueMode();
    void SetTorque(double torque_nm);
    void SetPIDGains(uint16_t p_gain, uint16_t i_gain, uint16_t d_gain);
    void EnableTorque();
    void DisableTorque();
    int GetPresentPosition();
    double GetPresentPositionDegrees();
    void SetVelocityAndAcceleration(uint32_t velocity, uint32_t acceleration);
    void MoveToWithVelocity(double goal_deg);
    double ConvertServoPositionToDegrees(int servo_position) const;
    void SetPosition(double pos_deg, int velocity = -1);
    void Close();
    int ConvertDegreesToServoPosition(double pos_deg) const;

private:
    void Write2B(int addr, uint16_t val, const char* what);
    void Write4B(int addr, uint32_t val, const char* what);

private:
    std::string PORT_NAME;
    int BAUD_RATE;
    float PROTOCOL_VERSION;
    uint8_t DXL_ID;
    uint8_t operating_mode_;
    double offset_;
    double multiplier_;
    int MIN_POSITION;
    int MAX_POSITION;
    double offset_center_;
    std::array<int, 3> speeds_;
    double last_set_torque_;

    dynamixel::PortHandler* portHandler_{nullptr};
    dynamixel::PacketHandler* packetHandler_{nullptr};
};

#endif // DYNAMIXEL_HPP