cmake_minimum_required(VERSION 3.10)
project(ChessRobot)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)

# Add source files
set(SOURCES
	main.cpp
	dynamixel.cpp
	board_state_tracker.cpp
	target_position_calculator.cpp
)

# Include directories
include_directories(/usr/local/include)

# Link libraries
link_directories(/usr/local/lib)
# On Raspberry Pi (linux_sbc build), the SDK installs as libdxl_sbc_cpp.so
# Also link pthread and rt as required by the SDK build
set(LIBS dxl_sbc_cpp pthread rt)

# Create executable
add_executable(program ${SOURCES})
target_link_libraries(program ${LIBS})