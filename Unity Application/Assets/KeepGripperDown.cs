using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class KeepGripperDown : MonoBehaviour
{
    MqttPublisher mqtt;
    [SerializeField] Transform gripperPivot;
    [SerializeField] Transform gripperCenter;
    [SerializeField] float angle;
    [SerializeField] bool drawRay;
    [SerializeField] float gripperSpeed;
    float b;
    // [SerializeField] float b;
    CurrentAngles anglesScr;

    private void Start()
    {
        anglesScr = GetComponent<CurrentAngles>();
        mqtt = GetComponent<MqttPublisher>();
    }

    private void LateUpdate()
    {
        if (drawRay)
        {
            Vector3 origin = gripperCenter.position; // Your start point
            origin.y -= 3f;
            Vector3 direction = Vector3.down;
            float maxDistance = 8f;
            Debug.DrawRay(origin, direction * maxDistance, Color.red);
        }
        return;
        b = 90 - anglesScr.shoulderAngle;
        angle = 90 + b - anglesScr.elbowAngle;
        gripperPivot.localEulerAngles = new Vector3(0, 0, -angle);
        //anglesScr.gripperAngle = angle;
        mqtt.Send("target/wrist", angle.ToString() + ";" + gripperSpeed.ToString());

        // Draw the ray in the Scene view
        
    }

    public void OpenGripper()
    {
        mqtt.Send("gripper", "open");
    }

    public void CloseGripper()
    {
        mqtt.Send("gripper", "closed");
    }

}
