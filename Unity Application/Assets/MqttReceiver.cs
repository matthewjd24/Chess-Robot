using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Collections.Concurrent;
using TMPro;

public class MqttReceiver : MonoBehaviour
{
    ConcurrentQueue<KeyValuePair<string, string>> messageQueue = new ConcurrentQueue<KeyValuePair<string, string>>();
    [SerializeField] Transform basePivot;
    [SerializeField] Transform shoulder;
    [SerializeField] Transform elbow;
    [SerializeField] Transform gripper;
    Button btnScr;
    [SerializeField] TextMeshProUGUI baseActual;
    [SerializeField] TextMeshProUGUI shoulderActual;
    [SerializeField] TextMeshProUGUI elbowActual;
    [SerializeField] float baseServoZeroAngle = -1f;

    private void Start()
    {
        btnScr = GetComponent<Button>();
    }

    public void ReceiveMessage(string topic, string msg)
    {
        //Debug.Log($"[MQTT] Message received on topic '{topic}': {msg}");
        messageQueue.Enqueue(new KeyValuePair<string, string>(topic, msg));
    }

    private void Update()
    {
        while (messageQueue.TryDequeue(out var message))
        {
            string topic = message.Key;
            string payload = message.Value;

            // Handle the message safely on the main thread
            //Debug.Log($"[MQTT] Topic: {topic} | Payload: {payload}");
            if (topic == "position/base")
            {
                basePivot.localEulerAngles = new Vector3(0f, float.Parse(payload) + baseServoZeroAngle, 0f); // 
                baseActual.text = "Actual: " + payload; // + baseServoZeroAngle
                HighLevelControl.inst.currentAngles.x = float.Parse(payload);
            }
            else if (topic == "position/shoulder")
            {
                shoulder.localEulerAngles = new Vector3(0f, 0, -float.Parse(payload));
                shoulderActual.text = "Actual: " + payload;
                HighLevelControl.inst.currentAngles.y = float.Parse(payload);
            }
            else if (topic == "position/elbow")
            {
                float angle = -(float.Parse(payload) - 90f);
                elbow.localEulerAngles = new Vector3(0f, 0, angle);
                elbowActual.text = "Actual: " + payload;
                HighLevelControl.inst.currentAngles.z = float.Parse(payload);
            }
            else if (topic == "position/wrist")
            {
                gripper.localEulerAngles = new Vector3(0f, 0, -float.Parse(payload));
                HighLevelControl.inst.currentAngles.w = float.Parse(payload);
            }
            else if (topic == "button")
            {
                 btnScr.isPressed = payload == "pressed";
            }
        }

    }
}
