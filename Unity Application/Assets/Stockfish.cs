using System.Diagnostics;
using System.IO;
using UnityEngine;
using System.Threading;
using System.Collections.Concurrent;

public class Stockfish : MonoBehaviour
{
    public static Stockfish inst;
    private Process stockfishProcess;
    private StreamWriter inputStream;
    private StreamReader outputStream;
    private Thread outputThread;
    private bool running = false;
    public string recommendedMove = "";

    public ConcurrentQueue<string> OutputQueue = new ConcurrentQueue<string>();

    private void Awake()
    {
        inst = this;
        StartStockfish();
        SendCommand("uci");
        SendCommand("isready");
        //SendCommand("position fen rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 - 0 1");
        //SendCommand("go depth 10");

        //SendCommand("position startpos moves e2e4 e7e5");
    }

    void OnDestroy()
    {
        StopStockfish();
    }

    void Update()
    {
        while (OutputQueue.TryDequeue(out string line))
        {
            //UnityEngine.Debug.Log("Parsed Stockfish: " + line);

            if (line.StartsWith("bestmove"))
            {
                string move = line.Split(' ')[1];
                //UnityEngine.Debug.Log("Stockfish recommends: " + move);
                recommendedMove = move;
                // Do something with the move here
            }
        }
    }

    void StartStockfish()
    {
        string stockfishPath = "C:\\stockfish.exe";

        stockfishProcess = new Process();
        stockfishProcess.StartInfo.FileName = stockfishPath;
        stockfishProcess.StartInfo.UseShellExecute = false;
        stockfishProcess.StartInfo.RedirectStandardInput = true;
        stockfishProcess.StartInfo.RedirectStandardOutput = true;
        stockfishProcess.StartInfo.CreateNoWindow = true;

        try
        {
            stockfishProcess.Start();
            //UnityEngine.Debug.Log("Stockfish process started");
        }
        catch (System.Exception ex)
        {
            UnityEngine.Debug.LogError("Failed to start Stockfish: " + ex.Message);
        }
        inputStream = stockfishProcess.StandardInput;
        inputStream.AutoFlush = true;
        outputStream = stockfishProcess.StandardOutput;

        running = true;
        outputThread = new Thread(ReadOutputLoop);
        outputThread.Start();
    }

    void ReadOutputLoop()
    {
        //UnityEngine.Debug.Log("ReadOutputLoop started");

        while (running && !outputStream.EndOfStream)
        {
            string line = outputStream.ReadLine();
            if (line != null)
            {
                //UnityEngine.Debug.Log("Stockfish: " + line);
                OutputQueue.Enqueue(line);
            }
            else
            {
                //UnityEngine.Debug.Log("ReadLine() returned null");
            }
        }

        //UnityEngine.Debug.Log("ReadOutputLoop exited");
    }

    public void GetBestMove(string fen)
    {
        SendCommand(fen);
        SendCommand("go depth 10");
    }

    void SendCommand(string command)
    {
        if (stockfishProcess != null && !stockfishProcess.HasExited)
        {
            inputStream.WriteLine(command);
            inputStream.Flush();
        }
    }

    void StopStockfish()
    {
        running = false;

        if (stockfishProcess != null && !stockfishProcess.HasExited)
        {
            SendCommand("quit");
            stockfishProcess.Kill();
            stockfishProcess.Dispose();
        }

        outputThread?.Join();
    }
}
