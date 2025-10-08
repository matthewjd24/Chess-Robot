#include "TargetPositionCalculator.hpp"
#include "ArmMovement.hpp"
#include <cmath>

XYZ SquareToXYZ(int col, int row) {
    double firstColX = -6.224;
    double firstRowY = 5.983;
    double boardZ = -4.02;

    double interSquareDistance = 1.7756;

    XYZ result;
    result.x = firstColX + (col - 1) * interSquareDistance;
    result.y = firstRowY + (row - 1) * interSquareDistance;
    result.z = 0.0;
    return result;
}

JointAngles XYZToJointAngles(const XYZ& position){
    double x = sqrt(position.x * position.x + position.z * position.z);
    double y = position.y;
    double baseAngle, shoulderAngle, elbowAngle, wristAngle;
    double L1 = 9.8;
    double L2 = 10.0;

    double cosVal = (x * x + y * y - L1 * L1 - L2 * L2) / (2.0 * L1 * L2);
    double sinVal = -sqrt(1.0 - cosVal * cosVal);

    elbowAngle = atan2(sinVal, cosVal) * 180.0 / M_PI;

    double k1 = L1 + L2 * cosVal;
    double k2 = L2 * sinVal;

    shoulderAngle = ((atan2(y, x) - atan2(k2, k1)) * 180.0 / M_PI - 90.0);
    elbowAngle *= -1.0;

    baseAngle = atan2(position.x, position.y) * 180.0 / M_PI;
    wristAngle = 180.0 - (shoulderAngle + elbowAngle); //+4.0;

    return JointAngles{baseAngle, shoulderAngle, elbowAngle, wristAngle};
}

XYZ JointAnglesToXYZ(const JointAngles& angles) {
    const double L1 = 9.84;
    const double L2 = 9.84;
    XYZ out;

    // apply offset from first link
    out.x = 0.0;
    out.y = L1 * std::sin(angles.shoulder * M_PI / 180.0);
    out.z = L1 * std::cos(angles.shoulder * M_PI / 180.0);


    // apply offset from second link
    auto adjustedAngle = angles.elbow + angles.shoulder;
    out.y += L2 * std::sin(adjustedAngle * M_PI / 180.0);
    out.z += L2 * std::cos(adjustedAngle * M_PI / 180.0);

    // adjust for base rotation
    auto oldY = out.y;
    out.y = std::cos(angles.base * M_PI / 180.0) * oldY;
    out.x = std::sin(angles.base * M_PI / 180.0) * oldY;

    return out;
}