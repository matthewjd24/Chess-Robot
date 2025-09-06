using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CurrentAngles : MonoBehaviour
{
    [SerializeField] Transform shoulderpivot;
    [SerializeField] Transform elbowpivot;

    public float baseAngle;
    public float shoulderAngle;
    public float elbowAngle;
    public float gripperAngle;

    public float elbowGlobalAngleFromVertical;

    private void Start()
    {
        Update();
    }


    // Update is called once per frame
    void Update()
    {
        shoulderAngle = shoulderpivot.localEulerAngles.z;
        if (shoulderAngle > 180f) shoulderAngle -= 360f;
        shoulderAngle *= -1;
        elbowAngle = elbowpivot.localEulerAngles.z;
        if (elbowAngle > 180f) elbowAngle -= 360f;
        elbowAngle *= -1;
        elbowAngle += 90f;

        elbowGlobalAngleFromVertical = shoulderAngle + elbowAngle;
    }
}
