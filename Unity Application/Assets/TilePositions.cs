using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TilePositions : MonoBehaviour
{
    [SerializeField] Transform tilesParent;


    public Vector3 GetTilePosition(int col, int row)
    {
        // Validate input
        if (col < 1 || col > 8 || row < 1 || row > 8)
            throw new ArgumentOutOfRangeException("Column and row must be between 1 and 8");

        int tileNumber = (row - 1) * 8 + (8 - col + 1);

        return tilesParent.GetChild(tileNumber - 1).position;
    }
}
