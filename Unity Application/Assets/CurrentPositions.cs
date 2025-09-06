using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CurrentPositions : MonoBehaviour
{
    [SerializeField] CurrentAngles anglesScr;
    public Vector3 elbowPosition;
    public Vector3 gripperPosition;
    public float localAngle;
    public float edgeLength;
    public float hypotLength;
    public float overallAngle;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        float shouldAngle = anglesScr.shoulderAngle * Mathf.Deg2Rad;
        float x = Mathf.Sin(shouldAngle) * 9.8f;
        float y = Mathf.Cos(shouldAngle) * 9.8f;
        elbowPosition = new Vector3(x, y, 0);

        float elbowAngle = anglesScr.elbowAngle * Mathf.Deg2Rad;
        float localX = Mathf.Sin(elbowAngle) * 10f;
        float localY = Mathf.Cos(elbowAngle) * 10f;
        edgeLength = 9.8f + localY;
        hypotLength = Mathf.Sqrt(edgeLength * edgeLength + localX * localX);
        localAngle = Mathf.Acos(edgeLength / hypotLength) * Mathf.Rad2Deg;
        overallAngle = (shouldAngle + Mathf.Acos(edgeLength / hypotLength)) * Mathf.Rad2Deg;
        float overallAngleRad = (shouldAngle + Mathf.Acos(edgeLength / hypotLength));
        float gripperX = Mathf.Sin(overallAngleRad) * hypotLength;
        float gripperY = Mathf.Cos(overallAngleRad) * hypotLength;
        gripperPosition = new Vector3(gripperX, gripperY, 0);
    }
}
