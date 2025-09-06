using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class HighLevelControl : MonoBehaviour
{
    public static HighLevelControl inst;
    MotionPlanner plannerScr;
    MotionExecutor executorScr;
    KeepGripperDown gripper;
    Button btnScr;
    MqttPublisher mqtt;
    int currCol = 0;
    int currRow = 0;
    float currZHeight = 0;

    [SerializeField] float piecePickupHeight = 2f;
    [SerializeField] float gripperMovementHeight = 5.4f;

    [SerializeField] int startCol = 1;
    [SerializeField] int startRow = 1;
    [SerializeField] int endCol = 2;
    [SerializeField] int endRow = 2;

    [SerializeField] TextMeshProUGUI baseTarget;
    [SerializeField] TextMeshProUGUI baseTargetAfterAdjust;
    [SerializeField] TextMeshProUGUI shoulderTarget;
    [SerializeField] TextMeshProUGUI elbowTarget;

    private void Awake() {
        inst = this;
    }

    private void Start()
    {
        gripper = GetComponent<KeepGripperDown>();
        plannerScr = GetComponent<MotionPlanner>();
        executorScr = GetComponent<MotionExecutor>();
        btnScr = GetComponent<Button>();
        mqtt = GetComponent<MqttPublisher>();

        //StartCoroutine(OpenGripper());
        StartCoroutine(GameLoop());
    }

    IEnumerator GameLoop()
    {
        var tracker = GetComponent<BoardStateTracker>();
        int counter = 1;
        while (true)
        {
            if (counter == 1) {
                startCol = 5;
                startRow = 2;
                endCol = 5;
                endRow = 4;
            }
            else if (counter == 2) {
                startCol = 2;
                startRow = 1;
                endCol = 3;
                endRow = 3;
            }
            else if (counter == 3) {
                startCol = 6;
                startRow = 1;
                endCol = 2;
                endRow = 5;
            }
            else if (counter == 4) {
                startCol = 7;
                startRow = 2;
                endCol = 7;
                endRow = 4;
            }
            counter++;

            mqtt.Send("waiting_for_button", "true");
            yield return new WaitUntil(() => btnScr.isPressed);
            mqtt.Send("waiting_for_button", "false");

            //tracker.RunAnalysisOfBoard();
            //yield return new WaitUntil(() => tracker.responseMove != "");
            //string response = tracker.responseMove;
            //Debug.Log("Going to do " + response);
            //tracker.responseMove = null;

            //mqtt.Send("waiting_for_button", "true");
            //yield return new WaitUntil(() => btnScr.isPressed);
            //mqtt.Send("waiting_for_button", "false");

            //Debug.Log("Btn pressed");
            //yield return StartCoroutine(MovePiece(startCol, startRow, endCol, endRow));

            bool destinationTileIsAdjacent = false;
            if (Mathf.Abs(startCol - endCol) == 1 && startRow == endRow) destinationTileIsAdjacent = true;
            if (Mathf.Abs(startRow - endRow) == 1 && startCol == endCol) destinationTileIsAdjacent = true;

            if (destinationTileIsAdjacent) yield return StartCoroutine(MovePieceToAdjacentTile(startCol, startRow, endCol, endRow));
            else yield return StartCoroutine(MovePiece(startCol, startRow, endCol, endRow));
        }
    }

    IEnumerator MovePieceToAdjacentTile(int sourceCol, int sourceRow, int destCol, int destRow)
    {
        yield return StartCoroutine(ExecuteMovement(0, 0, GripperHeight.PieceMovement, 21f));
        yield return StartCoroutine(ExecuteMovement(sourceCol, sourceRow, GripperHeight.PieceMovement, 21f));


        gripper.OpenGripper();
        yield return StartCoroutine(ExecuteMovement(sourceCol, sourceRow, GripperHeight.PiecePickup));
        gripper.CloseGripper();
        yield return new WaitForSeconds(.5f);

        yield return StartCoroutine(ExecuteMovement(sourceCol, sourceRow, GripperHeight.LowPieceMovement));
        yield return StartCoroutine(ExecuteMovement(destCol, destRow, GripperHeight.LowPieceMovement, 15f));

        yield return StartCoroutine(ExecuteMovement(destCol, destRow, GripperHeight.PiecePickup));

        StartCoroutine(OpenAndCloseGripper(2f));
        yield return StartCoroutine(ExecuteMovement(destCol, destRow, GripperHeight.PieceMovement, 23f));

        yield return StartCoroutine(ExecuteMovement(0, 0, GripperHeight.PieceMovement, 48f));
        yield return StartCoroutine(ExecuteMovement(0, 0, GripperHeight.RestingPosition));
    }

    enum GripperHeight
    {
        PiecePickup,
        LowPieceMovement,
        PieceMovement,
        RestingPosition
    }

    IEnumerator MovePiece(int sourceCol, int sourceRow, int destCol, int destRow)
    {
        yield return new WaitForSeconds(.01f);

        // move gripper to be above source tile
        yield return StartCoroutine(ExecuteMovement(0, 0, GripperHeight.PieceMovement, 21f));
        yield return StartCoroutine(ExecuteMovement(sourceCol, sourceRow, GripperHeight.PieceMovement, 21f));
        //yield return new WaitUntil(() => btnScr.isPressed);

        // pick up piece from tile
        StartCoroutine(OpenAndCloseGripper(1.5f));
        yield return StartCoroutine(ExecuteMovement(sourceCol, sourceRow, GripperHeight.PiecePickup));
        yield return new WaitForSeconds(0.4f);
        yield return StartCoroutine(ExecuteMovement(sourceCol, sourceRow, GripperHeight.PieceMovement, 10f));

        // go to destination tile
        yield return StartCoroutine(ExecuteMovement(destCol, destRow, GripperHeight.PieceMovement, 14f));

        // place piece on tile
        yield return StartCoroutine(ExecuteMovement(destCol, destRow, GripperHeight.PiecePickup));
        StartCoroutine(OpenAndCloseGripper(1.5f));
        yield return new WaitForSeconds(0.4f);
        yield return StartCoroutine(ExecuteMovement(destCol, destRow, GripperHeight.PieceMovement, 15f));

        // return to origin
        yield return StartCoroutine(ExecuteMovement(0, 0, GripperHeight.PieceMovement, 33f));
        yield return StartCoroutine(ExecuteMovement(0, 0, GripperHeight.RestingPosition));
    }

    [SerializeField] float baseAngleMultiplier = 1.07f;
    [SerializeField] Vector4 targetAngles;
    public Vector4 currentAngles;
    IEnumerator ExecuteMovement(int destCol, int destRow, GripperHeight height, float cutoffDist = 7f)
    {
        float destZ = gripperMovementHeight;
        if (height == GripperHeight.PiecePickup) destZ = piecePickupHeight;
        else if (height == GripperHeight.RestingPosition) destZ = plannerScr.restingPosition.position.y;
        else if (height == GripperHeight.LowPieceMovement) destZ = piecePickupHeight + 1f;

        Vector3 startPos = MotionPlanner.inst.GetSpotPosition(currCol, currRow, currZHeight);
        Vector4 startAngles = InverseKinematics.inst.Solve(startPos);
        Vector3 targetPos = MotionPlanner.inst.GetSpotPosition(destCol, destRow, destZ);

        Vector4 targetJointAngles = InverseKinematics.inst.Solve(targetPos);
        MotionPlanner.inst.ShowPointsAlongPath(startPos, targetPos);

        if (height == GripperHeight.PiecePickup || height == GripperHeight.LowPieceMovement) {
            float distance = Vector3.Distance(Vector3.zero, targetPos);

            // 6.7: distance to closest tile (col 4 row 1)
            // 20: distance to farthest tile (col 1 row 8)
            float percentOfMaxDistance = Mathf.Abs((distance - 6.7f) / (20f - 6.7f));
            float shoulderAngleOffsetForBending = percentOfMaxDistance * -9.5f; // 1f is max added angle
            Debug.Log("Adding " + shoulderAngleOffsetForBending);
            targetJointAngles.y += shoulderAngleOffsetForBending;
        }

        targetJointAngles.x *= baseAngleMultiplier;

        baseTarget.text = "Target (b4 adjust): " + targetJointAngles.x;
        shoulderTarget.text = "Target: " + targetJointAngles.y;
        elbowTarget.text = "Target: " + targetJointAngles.z;

        //baseTargetAfterAdjust.text = "Target (after adjust):" + newX.ToString();
        targetAngles = new Vector4(targetJointAngles.x, targetJointAngles.y, targetJointAngles.z, 180f - targetJointAngles.w);

        executorScr.StartMovement(startAngles, targetJointAngles);
        yield return StartCoroutine(WaitUntilCurrentAnglesReachTarget(cutoffDist));
        //yield return new WaitForSeconds(3f);

        currCol = destCol;
        currRow = destRow;
        currZHeight = destZ;
    }

    IEnumerator WaitUntilCurrentAnglesReachTarget(float cutoff) {
        while (true) {
            yield return new WaitForEndOfFrame();
            bool isClose = false;

            var dist = Vector4.Distance(targetAngles, currentAngles);
            //Debug.Log("Distance is " + dist);
            if (dist < cutoff) isClose = true;

            if (isClose) break;
        }
    }

    IEnumerator OpenAndCloseGripper(float duration) {
        gripper.OpenGripper();
        yield return new WaitForSeconds(duration);
        gripper.CloseGripper();
    }
}
