from dataclasses import dataclass
import math


@dataclass
class tile:
    x: float
    y: float


def get_tile_positions():
    tileWidth = 1.768
    inchesFromBaseToFirstTile = 6.0
    tiles = [[None for _ in range(9)] for _ in range(9)]
    startingXPos = tileWidth * -4.5

    for a in range(9):
        if a == 0:
            continue

        xPos = round(startingXPos + a * tileWidth, 3)

        for b in range(9):
            if b == 0:
                continue

            y = inchesFromBaseToFirstTile + (b-1) * tileWidth
            myTile = tile(xPos, y)
            tiles[a][b] = myTile
        #print(tiles[a])

    return tiles

def get_base_angle(tile):
    # angle = arctan(x/y)
    angle = math.degrees(math.atan(tile.x / tile.y))
    return round(angle, 3)

def get_distance_to_tile(tile):
    return math.sqrt(tile.x * tile.x + tile.y * tile.y)

def get_elbow_shoulder_angles(distance, vert_height):
    l1 = 9.75
    l2 = 9.75
    x = distance
    y = vert_height
    # Calculate the cosine of theta2 using the cosine law
    cos_val = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    
    # Calculate the sine of theta2; note the negative sign as in the original snippet
    sin_val = -math.sqrt(1 - cos_val * cos_val)
    
    # Compute theta2 in degrees
    theta2 = math.degrees(math.atan2(sin_val, cos_val))
    
    # Calculate intermediate values for theta1 calculation
    k1 = l1 + l2 * cos_val
    k2 = l2 * sin_val
    
    # Compute theta1 in degrees
    theta1 = math.degrees(math.atan2(y, x) - math.atan2(k2, k1))
    theta1 = theta1 - 90.0
    theta2 = theta2 * -1
    print(f"Shoulder and elbow targets: {theta1:.2f}, {theta2:.2f}")
    
    return theta1, theta2