using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(MotionExecutor))]
public class MotionButton : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Reference to the script
        MotionExecutor myScript = (MotionExecutor)target;

        // Draw a button
        if (GUILayout.Button("Start motion"))
        {
            //myScript.StartMovement();
        }
    }
}

[CustomEditor(typeof(InverseKinematics))]
public class IKButton : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Reference to the script
        InverseKinematics myScript = (InverseKinematics)target;

        // Draw a button
        if (GUILayout.Button("Solve"))
        {
            myScript.MoveToSphere();
        }
        if (GUILayout.Button("Animate Path"))
        {
            //myScript.AnimatePath();
        }
    }
}

[CustomEditor(typeof(MotionPlanner))]
public class MotionPlannerButton : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Reference to the script
        MotionPlanner myScript = (MotionPlanner)target;

        // Draw a button
        if (GUILayout.Button("Create path"))
        {
            //myScript.Plan();
        }
    }
}

[CustomEditor(typeof(OpenCVStuff))]
public class OpenCVButton : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Reference to the script
        OpenCVStuff myScript = (OpenCVStuff)target;

        // Draw a button
        if (GUILayout.Button("Do Again"))
        {
            myScript.AnalyzeImage();
        }
    }
}

[CustomEditor(typeof(BoardStateTracker))]
public class BoardButton : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Reference to the script
        BoardStateTracker myScript = (BoardStateTracker)target;

        // Draw a button
        if (GUILayout.Button("Run"))
        {
            myScript.RunAnalysisOfBoard();
        }
    }
}

[CustomEditor(typeof(MqttPublisher))]
public class MqttPublisherBtn : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        DrawDefaultInspector();

        // Reference to the script
        MqttPublisher myScript = (MqttPublisher)target;

        // Draw a button
        if (GUILayout.Button("Send Angle"))
        {
            myScript.SendAngle();
        }
    }
}