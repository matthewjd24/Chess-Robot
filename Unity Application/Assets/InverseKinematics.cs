using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class InverseKinematics : MonoBehaviour
{
    public static InverseKinematics inst;
    [SerializeField] float L1 = 6;
    [SerializeField] float L2 = 6;
    [SerializeField] Transform sphere;
    [SerializeField] float baseAngle = 0;
    [SerializeField] float shoulderAngle = 0;
    [SerializeField] float elbowAngle = 0;
    [SerializeField] float wristAngle = 0;
    [SerializeField] Transform basePivot;
    [SerializeField] Transform shoulderPivot;
    [SerializeField] Transform elbowPivot;
    [SerializeField] Transform wristPivot;
    [SerializeField] bool moveArm;

    [SerializeField] float timePerStep = .02f;
    [SerializeField] float distancePerStep = .04f;

    private void Awake()
    {
        inst = this;
    }

    public void MoveToSphere()
    {
        Solve(sphere.transform.position);
    }

    public Vector4 Solve(Vector3 target)
    {
        float x = Mathf.Sqrt(target.x * target.x + target.z * target.z);
        float y = target.y;
        float cos = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2);
        float sin = -Mathf.Sqrt(1 - cos * cos);
        elbowAngle = Mathf.Atan2(sin, cos) * Mathf.Rad2Deg;
        float k1 = L1 + L2 * cos;
        float k2 = L2 * sin;
        shoulderAngle = -((Mathf.Atan2(y, x) - Mathf.Atan2(k2, k1)) * Mathf.Rad2Deg - 90);
        elbowAngle *= -1;

        // tan theta = z / x
        // the
        baseAngle = -Mathf.Atan2(target.z, target.x) * Mathf.Rad2Deg;
        wristAngle = shoulderAngle + elbowAngle + 4;

        //translate to unity
        float actualAngle1 = -shoulderAngle;
        float actualAngle2 = -elbowAngle + 90;
        float actualAngle3 = wristAngle;
        if (moveArm)
        {
            basePivot.localEulerAngles = new Vector3(0, baseAngle, 0);
            elbowPivot.localEulerAngles = new Vector3(0, 0, actualAngle2);
            shoulderPivot.localEulerAngles = new Vector3(0, 0, actualAngle1);
            wristPivot.localEulerAngles = new Vector3(0, 0, actualAngle3);
        }

        return new Vector4(baseAngle, shoulderAngle, elbowAngle, wristAngle);
    }

    private void Update()
    {
        Solve(sphere.transform.position);
    }

    //public Vector4 SolveAnglesForPath(Vector3 targetPos)
    //{
    //    //List<Vector4> angles = new();
    //    //foreach (var x in path)
    //    //{
    //    //    var result = Solve(x);
    //    //    //Vector4 set = new Vector4(result.x, result.y, result.z, 0);
    //    //    angles.Add(result);
    //    //}

    //    return Solve(targetPos);
    //}

    public void AnimatePath(List<Vector4> angles)
    {
        //if (angles == null) angles = planner.currentAnglesAlongPath;
        StartCoroutine(Animate(angles));
    }

    IEnumerator Animate(List<Vector4> angles)
    {
        moveArm = false;
        for (int i = 0; i < angles.Count; i++)
        {
            basePivot.localEulerAngles = new Vector3(0, angles[i].x, 0);

            float shoulderAngle = -angles[i].y;
            shoulderPivot.localEulerAngles = new Vector3(0, 0, shoulderAngle);

            float elbowAngle = -angles[i].z + 90;
            elbowPivot.localEulerAngles = new Vector3(0, 0, elbowAngle);

            float wristAngle = angles[i].w + 180;
            wristPivot.localEulerAngles = new Vector3(0, 0, wristAngle);

            yield return new WaitForSeconds(timePerStep);
        }
    }
}
