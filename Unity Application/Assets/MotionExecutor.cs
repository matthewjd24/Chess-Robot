using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using TMPro;

public class MotionExecutor : MonoBehaviour
{
    MotionPlanner plannerScr;
    MqttPublisher mqtt;
    InverseKinematics ikScr;
    CurrentAngles anglesScr;
    public bool isMoving = false;
    [SerializeField] Transform elbow;
    [SerializeField] Transform basePivot;
    [SerializeField] bool moveArm;
    float timeBetweenSend = .048f;



    private void Awake()
    {
        plannerScr = GetComponent<MotionPlanner>();
        mqtt = GetComponent<MqttPublisher>();
        ikScr = GetComponent<InverseKinematics>();
        anglesScr = GetComponent<CurrentAngles>();
    }

    public void StartMovement(Vector4 startingAngles, Vector4 targetAngles)
    {
        isMoving = true;
        //if (plannerScr.currentAnglesAlongPath.Count == 0) plannerScr.Plan();
        //StartCoroutine(RecordLoop(targetAngles));
        StartCoroutine(PublishLoop(startingAngles, targetAngles));
        //if (moveArm)
        //{
        //    ikScr.AnimatePath(targetAngles);
        //}
    }

    IEnumerator RecordLoop(List<Vector4> anglesAlongPath)
    {
        //yield return new WaitForSeconds(0.58f);
        string elbowTargetLog = "";
        string elbowActualLog = "";
        string baseTargetLog = "";
        string baseActualLog = "";

        for (int i = 0; i < 13; i++)
        {
            yield return new WaitForSeconds(timeBetweenSend);
            RecordServoPositions(-1);
        }


        for (int i = 0; i < anglesAlongPath.Count; i++)
        {
            yield return new WaitForSeconds(timeBetweenSend);
            RecordServoPositions(i);
        }

        for (int i = 0; i < 20; i++) // record data for an extra second because the servo lags behind
        {
            yield return new WaitForSeconds(timeBetweenSend);
            RecordServoPositions(1000);
        }

        void RecordServoPositions(int i)
        {
            float baseTarget;
            if (i == 1000) baseTarget = anglesAlongPath[^1].x;
            else if (i == -1) baseTarget = anglesAlongPath[0].x;
            else baseTarget = anglesAlongPath[i].x;
            baseTargetLog += baseTarget + "\n";

            float baseAngle = basePivot.localEulerAngles.y;
            if (baseAngle > 180f) baseAngle -= 360f;
            baseActualLog += baseAngle + "\n";


            float elbowTarget;
            if (i == 1000) elbowTarget = anglesAlongPath[^1].z;
            else if (i == -1) elbowTarget = anglesAlongPath[0].z;
            else elbowTarget = anglesAlongPath[i].z;
            elbowTargetLog += elbowTarget + "\n";

            float elbowAngle = elbow.localEulerAngles.z - 90;
            if (elbowAngle > 180) elbowAngle -= 360;
            elbowAngle *= -1;
            elbowActualLog += elbowAngle + "\n";
        }

        File.WriteAllText("motion\\elbow_target_angles.txt", elbowTargetLog);
        File.WriteAllText("motion\\elbow_actual_angles.txt", elbowActualLog);
        File.WriteAllText("motion\\base_target_angles.txt", baseTargetLog);
        File.WriteAllText("motion\\base_actual_angles.txt", baseActualLog);


        //List<float> velocities = new();
        //for (int i = 0; i < angles.Count; i++)
        //{
        //    if (i < angles.Count - 1 && i > 0)
        //    {
        //        var next = angles[i + 1];
        //        var prev = angles[i - 1];
        //        velocities.Add((next - prev) / (2 * .01f));
        //    }
        //    else
        //    {
        //        velocities.Add(0);
        //    }
        //}
        //string velData = "";
        //foreach (var x in velocities) velData += x + "\n";
        //File.WriteAllText("motion\\actual_velocities.txt", velData);


        //List<float> accels = new();
        //for (int i = 0; i < velocities.Count; i++)
        //{
        //    if (i < velocities.Count - 1 && i > 0)
        //    {
        //        var next = velocities[i + 1];
        //        var prev = velocities[i - 1];
        //        accels.Add((next - prev) / (2 * .01f));
        //    }
        //    else
        //    {
        //        accels.Add(0);
        //    }
        //}
        //string accelData = "";
        //foreach (var x in accels) accelData += x + "\n";
        //File.WriteAllText("motion\\actual_accels.txt", accelData);
    }

    IEnumerator PublishLoop(Vector4 startingAngles, Vector4 targetJointAngles)
    {
        float timePerMovement = 0.9f;
        //float shoulderDelta = Mathf.Abs(startingAngles.y - targetJointAngles.y);
        //if (shoulderDelta > 20f)
        //{
        //    float addedTime = shoulderDelta / 45f;
        //    if (addedTime > 2f) addedTime = 2f;
        //    timePerMovement += addedTime;
        //}

        PublishBase();
        yield return new WaitForSeconds(.43f);
        PublishElbow();
        PublishShoulder();
        PublishWrist();


        void PublishElbow()
        {
            float target = targetJointAngles.z;
            float deltaDeg = Mathf.Abs(startingAngles.z - targetJointAngles.z);
            float degPerSec = deltaDeg / timePerMovement;
            float rpm = degPerSec * 60f / 360f;
            float profileVelocity = rpm * 4.3f;
            profileVelocity = Mathf.Clamp(profileVelocity, 15, 60);
            mqtt.Send("target/elbow", $"{target};{profileVelocity}");
        }
        void PublishBase()
        {
            float target = targetJointAngles.x;
            float deltaDeg = Mathf.Abs(startingAngles.x - targetJointAngles.x);
            float degPerSec = deltaDeg / timePerMovement;
            float rpm = degPerSec * 60f / 360f;
            float profileVelocity = rpm * 4.3f;
            profileVelocity = Mathf.Clamp(profileVelocity, 15, 60);
            mqtt.Send("target/base", $"{target};{profileVelocity}");
        }
        void PublishShoulder()
        {
            float target = targetJointAngles.y;
            float deltaDeg = Mathf.Abs(startingAngles.y - targetJointAngles.y);
            float degPerSec = deltaDeg / timePerMovement;
            float rpm = degPerSec * 60f / 360f;
            float profileVelocity = rpm * 4.3f;
            profileVelocity = Mathf.Clamp(profileVelocity, 15, 60);
            mqtt.Send("target/shoulder", $"{target};{profileVelocity}");
        }
        void PublishWrist()
        {
            float target = 180 - targetJointAngles.w;
            float deltaDeg = Mathf.Abs(startingAngles.w - targetJointAngles.w);
            float degPerSec = deltaDeg / timePerMovement;
            float rpm = degPerSec * 60f / 360f;
            float profileVelocity = rpm * 4.8f;
            Debug.Log("Wrist profile vel: " + profileVelocity);
            profileVelocity = Mathf.Clamp(profileVelocity, 5, 60);
            mqtt.Send("target/wrist", $"{target};{profileVelocity}");
        }

        //float waitTime = targetJointAngles.Count * timeBetweenSend;
        //yield return new WaitForSeconds(waitTime);
        //isMoving = false;
    }


}
