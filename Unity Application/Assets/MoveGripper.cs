using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

public class MoveGripper : MonoBehaviour
{
    [SerializeField] Transform shoulderpivot;
    [SerializeField] Transform elbowpivot;


    [SerializeField] CurrentAngles anglesScr;
    [SerializeField] float targetShoulderAngle;
    [SerializeField] float targetElbowAngle;


    // Update is called once per frame
    void Update()
    {
        shoulderpivot.eulerAngles += new Vector3(0, 0, 1) * Time.deltaTime;

    }

}
