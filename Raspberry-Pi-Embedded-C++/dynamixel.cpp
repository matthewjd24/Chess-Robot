#include "dynamixel.hpp"
#include <dynamixel_sdk/dynamixel_sdk.h>
#include <string>
#include <array>
#include <iostream>
#include <thread>
#include <chrono>
#include <cmath>
#include <limits>

// Method implementations for DxlServo

// Constructor
DxlServo::DxlServo(
    uint8_t dxl_id,
    double offset_deg,
    std::array<int,3> speeds,
    double multiplier,
    uint8_t operating_mode,
    const std::string& port_name,
    int baud_rate,
    float protocol_version)
    : PORT_NAME(port_name),
      BAUD_RATE(baud_rate),
      PROTOCOL_VERSION(protocol_version),
      DXL_ID(dxl_id),
      operating_mode_(operating_mode),
      offset_(offset_deg),
      multiplier_(multiplier),
      MIN_POSITION(0),
      MAX_POSITION(4095),
      offset_center_(0.0),
      speeds_(speeds),
      last_set_torque_(std::numeric_limits<double>::quiet_NaN()),
      portHandler_(nullptr),
      packetHandler_(nullptr)
{
    offset_center_ = offset_ * 4095.0 / 360.0;

    // Initialize SDK handlers
    portHandler_   = dynamixel::PortHandler::getPortHandler(PORT_NAME.c_str());
    packetHandler_ = dynamixel::PacketHandler::getPacketHandler(PROTOCOL_VERSION);

    initialize();
    disable_torque();

    // Set initial operating mode
    uint8_t dxl_error = 0;
    int dxl_comm_result = packetHandler_->write1ByteTxRx(portHandler_, DXL_ID, ADDR_OPERATING_MODE, operating_mode_, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        throw std::runtime_error(std::string("Failed to set operating mode: ") + packetHandler_->getTxRxResult(dxl_comm_result));
    }
    if (dxl_error) {
        throw std::runtime_error(std::string("Servo error setting operating mode: ") + packetHandler_->getRxPacketError(dxl_error));
    }

    enable_torque();
}

// Destructor
DxlServo::~DxlServo() {
    try { close(); } catch (...) {}
}

void DxlServo::initialize() {
    if (!portHandler_->openPort())
        throw std::runtime_error("Failed to open port: " + PORT_NAME);
    if (!portHandler_->setBaudRate(BAUD_RATE))
        throw std::runtime_error("Failed to set baud rate: " + std::to_string(BAUD_RATE));
}

void DxlServo::torque_mode() {
    // Mirrors Python: writes 16 to Operating Mode (note: that’s actually PWM mode)
    disable_torque();
    uint8_t dxl_error = 0;
    int dxl_comm_result = packetHandler_->write1ByteTxRx(
        portHandler_, DXL_ID, ADDR_OPERATING_MODE, 16, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        std::cerr << "Failed to set Current Control Mode: "
                  << packetHandler_->getTxRxResult(dxl_comm_result) << "\n";
        return;
    } else if (dxl_error) {
        std::cerr << "Error setting mode: "
                  << packetHandler_->getRxPacketError(dxl_error) << "\n";
    }
    enable_torque();
}

void DxlServo::set_torque(double torque_nm) {
    if (!std::isnan(last_set_torque_) && torque_nm == last_set_torque_) return;

    // Python logic: torque -> current -> dxl units (0.00269 A per unit), write to address 102
    const double torque_constant = 1.78; // Nm/A
    double current_a = torque_nm / torque_constant;
    int dyna_units = static_cast<int>(current_a / 0.00269);

    std::cout << "Set torque " << torque_nm << " (" << dyna_units << " in dxl units)\n";
    last_set_torque_ = torque_nm;

    uint8_t dxl_error = 0;
    // Note: Python writes to address 102 specifically (not ADDR_GOAL_PWM=100)
    int dxl_comm_result = packetHandler_->write2ByteTxRx(
        portHandler_, DXL_ID, 102, dyna_units, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        std::cerr << "Failed to set goal PWM: "
                  << packetHandler_->getTxRxResult(dxl_comm_result) << "\n";
    } else if (dxl_error) {
        std::cerr << "Error setting goal PWM: "
                  << packetHandler_->getRxPacketError(dxl_error) << "\n";
    }
}

void DxlServo::set_pid_gains(uint16_t p_gain, uint16_t i_gain, uint16_t d_gain) {
    write2B(ADDR_POSITION_P_GAIN, p_gain, "P Gain");
    std::cout << "P Gain set to " << p_gain << ".\n";
    write2B(ADDR_POSITION_I_GAIN, i_gain, "I Gain");
    std::cout << "I Gain set to " << i_gain << ".\n";
    write2B(ADDR_POSITION_D_GAIN, d_gain, "D Gain");
    std::cout << "D Gain set to " << d_gain << ".\n";
}

void DxlServo::enable_torque() {
    uint8_t dxl_error = 0;
    packetHandler_->write1ByteTxRx(portHandler_, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE, &dxl_error);
}

void DxlServo::disable_torque() {
    uint8_t dxl_error = 0;
    packetHandler_->write1ByteTxRx(portHandler_, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE, &dxl_error);
}

int DxlServo::get_present_position() {
    uint8_t dxl_error = 0;
    uint32_t pos = 0;
    int dxl_comm_result = packetHandler_->read4ByteTxRx(
        portHandler_, DXL_ID, ADDR_PRESENT_POSITION, &pos, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        throw std::runtime_error(std::string("Read position failed: ")
                                 + packetHandler_->getTxRxResult(dxl_comm_result));
    }
    if (dxl_error) {
        throw std::runtime_error(std::string("Servo error on read: ")
                                 + packetHandler_->getRxPacketError(dxl_error));
    }

    // Mirror Python’s wrap logic
    int present_position = static_cast<int>(pos);
        if (present_position > (1 << 31)) {
            present_position = MAX_POSITION + present_position - (1ULL << 32);
    }
    if (present_position > 4095) {
        present_position -= 4095;
    }
    return present_position;
}

double DxlServo::get_present_position_degrees() {
    return convert_servo_position_to_degrees(get_present_position());
}

void DxlServo::set_velocity_and_acceleration(uint32_t velocity, uint32_t acceleration) {
    write4B(ADDR_PROFILE_VELOCITY,     velocity,     "Profile Velocity");
    write4B(ADDR_PROFILE_ACCELERATION, acceleration, "Profile Acceleration");
    std::cout << "Profile Velocity set to " << velocity
              << ", Acceleration set to " << acceleration << ".\n";
}

void DxlServo::move_to_with_velocity(double goal_deg) {
    const int stop_threshold = 10; // same as Python
    int goal_position = convert_degrees_to_servo_position(goal_deg);

    std::cout << "Moving servo " << int(DXL_ID) << " to " << goal_position
              << " with velocity control.\n";

    while (true) {
        int present_position = get_present_position();
        int raw_diff = goal_position - present_position;

        // Wrap to [-2048, 2047]
        if (raw_diff > (MAX_POSITION / 2)) raw_diff -= MAX_POSITION;
        else if (raw_diff < -(MAX_POSITION / 2)) raw_diff += MAX_POSITION;

        int error = std::abs(raw_diff);

        int new_velocity = speeds_[0];
        if (error < 100)      new_velocity = speeds_[2];
        else if (error < 250) new_velocity = speeds_[1];

        if (raw_diff < 0) new_velocity = -new_velocity;

        if (error < stop_threshold) break;

        write4B(ADDR_GOAL_VELOCITY, static_cast<uint32_t>(new_velocity), "Goal Velocity");
        std::cout << "Moving... Current: " << present_position
                  << ", Target: " << goal_position
                  << ", Error: " << error
                  << ", Velocity: " << new_velocity << "\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    // Immediate stop (no ramp)
    write4B(ADDR_GOAL_VELOCITY, 0u, "Goal Velocity");
    std::cout << "Now at " << get_present_position() << ", stopping.\n";
}

double DxlServo::convert_servo_position_to_degrees(int servo_position) const {
    const double servo_values_per_degree = double(MAX_POSITION) / 360.0;
    double result = (servo_position - offset_center_) / (servo_values_per_degree * multiplier_);
    if (result > 180.0) result -= 360.0;
    return std::round(result * 100.0) / 100.0; // round to 2 decimals
}

void DxlServo::set_position(double pos_deg, int velocity) {
    if (operating_mode_ != OPERATING_MODE_POSITION) {
        throw std::runtime_error("Servo is not in position control mode.");
    }

    if (velocity >= 0) {
        write4B(ADDR_PROFILE_VELOCITY, static_cast<uint32_t>(velocity), "Profile Velocity");
    }
    write4B(ADDR_PROFILE_ACCELERATION, 50u, "Profile Acceleration");

    int goal_position = convert_degrees_to_servo_position(pos_deg);
    uint8_t dxl_error = 0;
    int dxl_comm_result = packetHandler_->write4ByteTxRx(
        portHandler_, DXL_ID, ADDR_GOAL_POSITION, static_cast<uint32_t>(goal_position), &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        throw std::runtime_error(std::string("Failed to set goal position: ")
                                 + packetHandler_->getTxRxResult(dxl_comm_result));
    }
    if (dxl_error) {
        throw std::runtime_error(std::string("Error from servo: ")
                                 + packetHandler_->getRxPacketError(dxl_error));
    }
}

void DxlServo::close() {
    if (portHandler_) {
        portHandler_->closePort();
        // std::cout << "Port closed.\n";
    }
}

int DxlServo::convert_degrees_to_servo_position(double pos_deg) const {
    const double servo_values_per_degree = double(MAX_POSITION) / 360.0;
    int result = int(offset_center_ + (pos_deg * servo_values_per_degree) * multiplier_);
    if (result < 0) result += MAX_POSITION;
    return result;
}

// IO helpers
void DxlServo::write2B(int addr, uint16_t val, const char* what) {
    uint8_t dxl_error = 0;
    int dxl_comm_result = packetHandler_->write2ByteTxRx(
        portHandler_, DXL_ID, addr, val, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getTxRxResult(dxl_comm_result));
    }
    if (dxl_error) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getRxPacketError(dxl_error));
    }
}

void DxlServo::write4B(int addr, uint32_t val, const char* what) {
    uint8_t dxl_error = 0;
    int dxl_comm_result = packetHandler_->write4ByteTxRx(
        portHandler_, DXL_ID, addr, val, &dxl_error);
    if (dxl_comm_result != COMM_SUCCESS) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getTxRxResult(dxl_comm_result));
    }
    if (dxl_error) {
        throw std::runtime_error(std::string(what) + " Error: "
                                 + packetHandler_->getRxPacketError(dxl_error));
    }
}

