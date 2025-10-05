#include "Dynamixel.hpp"
#include <dynamixel_sdk/dynamixel_sdk.h>
#include <string>
#include <array>
#include <iostream>
#include <thread>
#include <chrono>
#include <cmath>
#include <limits>

// Constructor
DxlServo::DxlServo(
    uint8_t dxlId,
    double offsetDeg,
    std::array<int,3> speedsIn,
    double multiplierVal,
    uint8_t operatingMode,
    const std::string& portName,
    int baudRate,
    float protocolVersion)
    : PORT_NAME(portName),
      BAUD_RATE(baudRate),
      PROTOCOL_VERSION(protocolVersion),
      DXL_ID(dxlId),
      operating_mode_(operatingMode),
      offset_(offsetDeg),
      multiplier_(multiplierVal),
      MIN_POSITION(0),
      MAX_POSITION(4095),
      offset_center_(0.0),
      speeds_(speedsIn),
      last_set_torque_(std::numeric_limits<double>::quiet_NaN()),
      portHandler_(nullptr),
      packetHandler_(nullptr)
{
    offset_center_ = offset_ * 4095.0 / 360.0;

    // Initialize SDK handlers
    portHandler_   = dynamixel::PortHandler::getPortHandler(PORT_NAME.c_str());
    packetHandler_ = dynamixel::PacketHandler::getPacketHandler(PROTOCOL_VERSION);

    Initialize();
    DisableTorque();

    // Set initial operating mode
    uint8_t dxlError = 0;
    int dxlCommResult = packetHandler_->write1ByteTxRx(
        portHandler_, DXL_ID, ADDR_OPERATING_MODE, operating_mode_, &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        throw std::runtime_error(std::string("Failed to set operating mode: ")
                                 + packetHandler_->getTxRxResult(dxlCommResult));
    }
    if (dxlError) {
        throw std::runtime_error(std::string("Servo error setting operating mode: ")
                                 + packetHandler_->getRxPacketError(dxlError));
    }

    EnableTorque();
}

DxlServo::~DxlServo() {
    try { Close(); } catch (...) {}
}

void DxlServo::Initialize() {
    if (!portHandler_->openPort())
        throw std::runtime_error("Failed to open port: " + PORT_NAME);
    if (!portHandler_->setBaudRate(BAUD_RATE))
        throw std::runtime_error("Failed to set baud rate: " + std::to_string(BAUD_RATE));
}

void DxlServo::TorqueMode() {
    // Mirrors Python: writes 16 to Operating Mode (PWM/current mode)
    DisableTorque();
    uint8_t dxlError = 0;
    int dxlCommResult = packetHandler_->write1ByteTxRx(
        portHandler_, DXL_ID, ADDR_OPERATING_MODE, 16, &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        std::cerr << "Failed to set Current Control Mode: "
                  << packetHandler_->getTxRxResult(dxlCommResult) << "\n";
        return;
    } else if (dxlError) {
        std::cerr << "Error setting mode: "
                  << packetHandler_->getRxPacketError(dxlError) << "\n";
    }
    EnableTorque();
}

void DxlServo::SetTorque(double torqueNm) {
    if (!std::isnan(last_set_torque_) && torqueNm == last_set_torque_) return;

    const double torqueConstant = 1.78; // Nm/A
    double currentA = torqueNm / torqueConstant;
    int dynaUnits = static_cast<int>(currentA / 0.00269);

    std::cout << "Set torque " << torqueNm << " (" << dynaUnits << " in dxl units)\n";
    last_set_torque_ = torqueNm;

    uint8_t dxlError = 0;
    // Address 102: Goal Current on many X-series (per Python reference)
    int dxlCommResult = packetHandler_->write2ByteTxRx(
        portHandler_, DXL_ID, 102, dynaUnits, &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        std::cerr << "Failed to set goal current: "
                  << packetHandler_->getTxRxResult(dxlCommResult) << "\n";
    } else if (dxlError) {
        std::cerr << "Error setting goal current: "
                  << packetHandler_->getRxPacketError(dxlError) << "\n";
    }
}

void DxlServo::SetPIDGains(uint16_t pGain, uint16_t iGain, uint16_t dGain) {
    Write2B(ADDR_POSITION_P_GAIN, pGain, "P Gain");
    std::cout << "P Gain set to " << pGain << ".\n";
    Write2B(ADDR_POSITION_I_GAIN, iGain, "I Gain");
    std::cout << "I Gain set to " << iGain << ".\n";
    Write2B(ADDR_POSITION_D_GAIN, dGain, "D Gain");
    std::cout << "D Gain set to " << dGain << ".\n";
}

void DxlServo::EnableTorque() {
    uint8_t dxlError = 0;
    packetHandler_->write1ByteTxRx(portHandler_, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE, &dxlError);
}

void DxlServo::DisableTorque() {
    uint8_t dxlError = 0;
    packetHandler_->write1ByteTxRx(portHandler_, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, &dxlError);
}

int DxlServo::GetPresentPosition() {
    uint8_t dxlError = 0;
    uint32_t pos = 0;
    int dxlCommResult = packetHandler_->read4ByteTxRx(
        portHandler_, DXL_ID, ADDR_PRESENT_POSITION, &pos, &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        throw std::runtime_error(std::string("Read position failed: ")
                                 + packetHandler_->getTxRxResult(dxlCommResult));
    }
    if (dxlError) {
        throw std::runtime_error(std::string("Servo error on read: ")
                                 + packetHandler_->getRxPacketError(dxlError));
    }

    int presentPosition = static_cast<int>(pos);
    if (presentPosition > (1 << 31)) {
        presentPosition = MAX_POSITION + presentPosition - (1ULL << 32);
    }
    if (presentPosition > 4095) {
        presentPosition -= 4095;
    }
    return presentPosition;
}

double DxlServo::GetPresentPositionDegrees() {
    return ConvertServoPositionToDegrees(GetPresentPosition());
}

void DxlServo::SetVelocityAndAcceleration(uint32_t velocity, uint32_t acceleration) {
    Write4B(ADDR_PROFILE_VELOCITY,     velocity,     "Profile Velocity");
    Write4B(ADDR_PROFILE_ACCELERATION, acceleration, "Profile Acceleration");
    std::cout << "Profile Velocity set to " << velocity << ", Acceleration set to " << acceleration << ".\n";
}

void DxlServo::MoveToWithVelocity(double goalDeg) {
    const int stopThreshold = 10; // same as Python
    int goalPosition = ConvertDegreesToServoPosition(goalDeg);

    std::cout << "Moving servo " << int(DXL_ID) << " to " << goalPosition
              << " with velocity control.\n";

    while (true) {
        int presentPosition = GetPresentPosition();
        int rawDiff = goalPosition - presentPosition;

        // Wrap to [-2048, 2047]
        if (rawDiff > (MAX_POSITION / 2)) rawDiff -= MAX_POSITION;
        else if (rawDiff < -(MAX_POSITION / 2)) rawDiff += MAX_POSITION;

        int errorVal = std::abs(rawDiff);

        int newVelocity = speeds_[0];
        if (errorVal < 100)      newVelocity = speeds_[2];
        else if (errorVal < 250) newVelocity = speeds_[1];

        if (rawDiff < 0) newVelocity = -newVelocity;

        if (errorVal < stopThreshold) break;

        Write4B(ADDR_GOAL_VELOCITY, static_cast<uint32_t>(newVelocity), "Goal Velocity");
        std::cout << "Moving... Current: " << presentPosition
                  << ", Target: " << goalPosition
                  << ", Error: " << errorVal
                  << ", Velocity: " << newVelocity << "\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    // Immediate stop (no ramp)
    Write4B(ADDR_GOAL_VELOCITY, 0u, "Goal Velocity");
    std::cout << "Now at " << GetPresentPosition() << ", stopping.\n";
}

double DxlServo::ConvertServoPositionToDegrees(int servoPosition) const {
    const double servoValuesPerDegree = double(MAX_POSITION) / 360.0;
    double result = (servoPosition - offset_center_) / (servoValuesPerDegree * multiplier_);
    if (result > 180.0) result -= 360.0;
    return std::round(result * 100.0) / 100.0; // round to 2 decimals
}

void DxlServo::SetPosition(double posDeg, int velocity) {
    if (operating_mode_ != OPERATING_MODE_POSITION) {
        throw std::runtime_error("Servo is not in position control mode.");
    }

    if (velocity >= 0) {
        Write4B(ADDR_PROFILE_VELOCITY, static_cast<uint32_t>(velocity), "Profile Velocity");
    }
    Write4B(ADDR_PROFILE_ACCELERATION, 50u, "Profile Acceleration");

    int goalPosition = ConvertDegreesToServoPosition(posDeg);
    uint8_t dxlError = 0;
    int dxlCommResult = packetHandler_->write4ByteTxRx(
        portHandler_, DXL_ID, ADDR_GOAL_POSITION, static_cast<uint32_t>(goalPosition), &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        throw std::runtime_error(std::string("Failed to set goal position: ")
                                 + packetHandler_->getTxRxResult(dxlCommResult));
    }
    if (dxlError) {
        throw std::runtime_error(std::string("Error from servo: ")
                                 + packetHandler_->getRxPacketError(dxlError));
    }
}

void DxlServo::Close() {
    if (portHandler_) {
        portHandler_->closePort();
    }
}

int DxlServo::ConvertDegreesToServoPosition(double posDeg) const {
    const double servoValuesPerDegree = double(MAX_POSITION) / 360.0;
    int result = int(offset_center_ + (posDeg * servoValuesPerDegree) * multiplier_);
    if (result < 0) result += MAX_POSITION;
    return result;
}

// IO helpers
void DxlServo::Write2B(int addr, uint16_t val, const char* what) {
    uint8_t dxlError = 0;
    int dxlCommResult = packetHandler_->write2ByteTxRx(
        portHandler_, DXL_ID, addr, val, &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getTxRxResult(dxlCommResult));
    }
    if (dxlError) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getRxPacketError(dxlError));
    }
}

void DxlServo::Write4B(int addr, uint32_t val, const char* what) {
    uint8_t dxlError = 0;
    int dxlCommResult = packetHandler_->write4ByteTxRx(
        portHandler_, DXL_ID, addr, val, &dxlError);
    if (dxlCommResult != COMM_SUCCESS) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getTxRxResult(dxlCommResult));
    }
    if (dxlError) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getRxPacketError(dxlError));
    }
}

