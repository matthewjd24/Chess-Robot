using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.IO;
using UnityEngine;

public class MotionPlanner : MonoBehaviour
{
    public static MotionPlanner inst;
    CurrentAngles anglesScr;
    TilePositions tilesScr;
    InverseKinematics IKScr;
    public List<JointState> motionProfile = new List<JointState>();
    [SerializeField] Transform pathVisualParent;
    public Transform restingPosition;
    [SerializeField] float accel = 3f; // rad/s^2

    //[SerializeField] int startCol = 1;
    //[SerializeField] int startRow = 1;
    //[SerializeField] int endCol = 2;
    //[SerializeField] int endRow = 2;

    //[SerializeField] List<float> I = new(); // moment of inertia (kg*m^2)
    //[SerializeField] List<float> b = new(); // damping coefficient (N*m*s/rad)
    //[SerializeField] List<float> m = new(); // mass (kg)
    //[SerializeField] List<float> l = new(); // distance from joint to com (m)
    //float g = -9.81f; // gravity
    //int numJoints = 1;
    //float timePerStep = .01f;
    //float startingAngle = 90 * Mathf.Deg2Rad;
    [SerializeField] GameObject dot;
    //public List<Vector4> currentAnglesAlongPath;

    private void Awake()
    {
        inst = this;
    }

    private void Start()
    {
        anglesScr = GetComponent<CurrentAngles>();
        tilesScr = GetComponent<TilePositions>();
        IKScr = GetComponent<InverseKinematics>();
        //PlanMovement();
    }

    public void ShowPointsAlongPath(Vector3 startPos, Vector3 targetPos)
    {
        foreach (Transform child in pathVisualParent)
        {
            Destroy(child.gameObject);
        }
        List<Vector3> path = GetPointsFromAToB(startPos, targetPos, .16f);

        foreach (var x in path)
        {
            Instantiate(dot, x, Quaternion.identity, pathVisualParent);
        }
    }

    public Vector4 GetTargetAngles(int startCol, int startRow, float startZHeight, int endCol, int endRow, float endZHeight)
    {
        foreach(Transform child in pathVisualParent)
        {
            Destroy(child.gameObject);
        }

        Vector3 a = GetSpotPosition(startCol, startRow, startZHeight);
        Vector3 b = GetSpotPosition(endCol, endRow, endZHeight);
        List<Vector3> path = GetPointsFromAToB(a, b, .16f);

        foreach(var x in path)
        {
            Instantiate(dot, x, Quaternion.identity, pathVisualParent);
        }

        Instantiate(dot, b, Quaternion.identity, pathVisualParent);

        return IKScr.Solve(b);
    }

    public Vector3 GetSpotPosition(int col, int row, float zHeight)
    {
        if (col == 0) {
            return new Vector3(restingPosition.position.x, zHeight, restingPosition.position.z);
        }

        Vector3 targetPos = tilesScr.GetTilePosition(col, row);
        targetPos.y = zHeight;
        return targetPos;
    }

    List<Vector3> GetPointsFromAToB(Vector3 a, Vector3 b, float stepLength)
    {
        List<Vector3> path = new() { a };
        float dist = Vector3.Distance(a, b);
        int steps = Mathf.RoundToInt(dist / stepLength);
        var dir = (b - a).normalized;
        Vector3 currPos = a;
        for (int i = 1; i <= steps; i++)
        {
            currPos += dir * stepLength;
            path.Add(currPos);
        }
        path.Add(b);

        return path;
    }

    void PlanMovement(List<Vector3> path)
    {
        float currVel = 0f;
        float currPos = 0f;


        int totalSteps = 300;
        int accelSteps = 30; // accelerate for 20 steps

        // Compute max velocity reached
        float currAccel;

        for (int i = 0; i < totalSteps; i++)
        {
            currAccel = 0;
            //if (i < accelSteps)
            //{
            //    currAccel = -accel;
            //}
            //else if (i < totalSteps - accelSteps)
            //{
            //    currAccel = 0;
            //}
            //else
            //{
            //    currAccel = accel;
            //}

            //currVel += currAccel * timePerStep;
            //currPos += currVel * timePerStep;

            //var newJointState = new JointState();
            //newJointState.time = i * timePerStep;
            //newJointState.angles = new float[numJoints];
            //newJointState.velocities = new float[numJoints];
            //newJointState.accelerations = new float[numJoints];
            //newJointState.torques = new float[numJoints];

            //newJointState.angles[0] = startingAngle + currPos;
            //motionProfile.Add(newJointState);
        }

        //AddVelocity();
        //AddAccel();
        //AddTorques();

        string angleData = "";
        foreach(var x in motionProfile)
        {
            angleData += x.angles[0] + "\n";
        }
        File.WriteAllText("motion\\angles.txt", angleData);

        angleData = "";
        foreach (var x in motionProfile)
        {
            angleData += x.velocities[0] + "\n";
        }
        File.WriteAllText("motion\\velocities.txt", angleData);

        angleData = "";
        foreach (var x in motionProfile)
        {
            angleData += x.accelerations[0] + "\n";
        }
        File.WriteAllText("motion\\accelerations.txt", angleData);

        angleData = "";
        foreach (var x in motionProfile)
        {
            angleData += x.torques[0] + "\n";
        }
        File.WriteAllText("motion\\torques.txt", angleData);
    }
    
    //void AddVelocity()
    //{
    //    for (int i = 0; i < motionProfile.Count; i++)
    //    {
    //        if (i < motionProfile.Count - 1 && i > 0)
    //        {
    //            var x = motionProfile[i];
    //            var next = motionProfile[i + 1];
    //            var prev = motionProfile[i - 1];
    //            x.velocities[0] = (next.angles[0] - prev.angles[0]) / (2 * timePerStep);
    //        }
    //        else
    //        {
    //            motionProfile[i].velocities[0] = 0;
    //        }
    //    }
    //}

    //void AddAccel()
    //{
    //    for (int i = 0; i < motionProfile.Count; i++)
    //    {
    //        if (i < motionProfile.Count - 1 && i > 0)
    //        {
    //            var x = motionProfile[i];
    //            var next = motionProfile[i + 1];
    //            var prev = motionProfile[i - 1];
    //            x.accelerations[0] = (next.velocities[0] - prev.velocities[0]) / (2 * timePerStep);
    //        }
    //        else
    //        {
    //            motionProfile[i].accelerations[0] = 0;
    //        }
    //    }
    //}

    //void AddTorques()
    //{
    //    for (int i = 0; i < motionProfile.Count; i++)
    //    {
    //        var state = motionProfile[i];
    //        for (int j = 0; j < numJoints; j++)
    //        {
    //            float position = state.angles[j];
    //            float velocity = state.velocities[j];
    //            float accel = state.accelerations[j];

    //            float inertia = I[j];
    //            float damping = b[j];
    //            float mass = m[j];
    //            float length = l[j];

    //            float inertiaTerm = inertia * accel;
    //            float dampingTerm = damping * velocity;
    //            float gravityTerm = mass * g * length * Mathf.Sin(position);

    //            state.torques[j] = inertiaTerm + dampingTerm + gravityTerm;

    //            //Debug.Log($"i: {i}, pos: {position}, accel: {accel}, inertiaTerm: {inertiaTerm}, damping: {dampingTerm}, " +
    //                //$"gravity: {gravityTerm}, totalTorque: {state.torques[j]}");

    //        }
    //    }
    //}
}

public class JointState
{
    public float time;

    public float[] angles;       // q(t)
    public float[] velocities;   // q'(t)
    public float[] accelerations;// q''(t)
    public float[] torques;      // tau(t)
}
