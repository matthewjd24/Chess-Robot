using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BoardStateTracker : MonoBehaviour
{
    public string[,] board = new string[9, 9];
    [SerializeField] Transform tilesParent;
    [SerializeField] GameObject tileObject;
    [SerializeField] List<GameObject> tiles = new();
    [SerializeField] List<GameObject> tiles2 = new();

    public string responseMove = "";

    void Start()
    {
        for (int i = 1; i <= 8; i++)
        {
            for (int j = 1; j <= 8; j++)
            {
                board[i, j] = "";
            }
        }

        // White pieces (uppercase for FEN)
        board[1, 1] = "R";
        board[1, 2] = "N";
        board[1, 3] = "B";
        board[1, 4] = "Q";
        board[1, 5] = "K";
        board[1, 6] = "B";
        board[1, 7] = "N";
        board[1, 8] = "R";
        for (int j = 1; j <= 8; j++) board[2, j] = "P";

        // Black pieces (lowercase for FEN)
        board[8, 1] = "r";
        board[8, 2] = "n";
        board[8, 3] = "b";
        board[8, 4] = "q";
        board[8, 5] = "k";
        board[8, 6] = "b";
        board[8, 7] = "n";
        board[8, 8] = "r";
        for (int j = 1; j <= 8; j++) board[7, j] = "p";

        //Debug.Log(fen);
        //
    }

    string ConvertToFEN(string[,] board)
    {
        string fen = "position fen ";

        // Start from rank 8 (top, which is board[8, *]) down to rank 1 (board[1, *])
        for (int row = 8; row >= 1; row--)
        {
            int emptyCount = 0;

            for (int col = 1; col <= 8; col++)
            {
                string piece = board[row, col];

                if (string.IsNullOrEmpty(piece))
                {
                    emptyCount++;
                }
                else
                {
                    if (emptyCount > 0)
                    {
                        fen += emptyCount.ToString();
                        emptyCount = 0;
                    }

                    fen += piece;
                }
            }

            if (emptyCount > 0)
            {
                fen += emptyCount.ToString();
            }

            if (row > 1) fen += "/";
        }

        // Append rest of FEN fields: active color, castling rights, en passant target, halfmove clock, fullmove number
        fen += " b KQkq - 0 1";

        return fen;
    }

    public void RunAnalysisOfBoard()
    {
        Start();
        responseMove = "";
        OpenCVStuff cvStuff = GetComponent<OpenCVStuff>();
        var analyses = cvStuff.AnalyzeImage();
        

        string pieceThatMoved = GetPieceThatMoved();

        string GetPieceThatMoved()
        {
            for (int row = 1; row <= 8; row++) {
                for (int col = 1; col <= 8; col++) {
                    int index = (row - 1) * 8 + (8 - col);
                    var tile = analyses[index];
                    var prevLetter = board[row, col];
                    //Debug.Log($"Prev letter: {prevLetter}, current piece color: {tile.pieceOnTile}");

                    var sr = tiles2[index].GetComponent<SpriteRenderer>();
                    if (tile.pieceOnTile == PieceColor.None && prevLetter != "")
                    {
                        board[row, col] = "";
                        sr.color = new Color(84f / 255f, 96f / 255f, 128f / 255f);
                        return prevLetter;
                    }
                    else sr.color = new Color(.5f, .5f, .5f);
                }
            }
            return "";
        }

        for (int row = 1; row <= 8; row++)
        {
            for (int col = 1; col <= 8; col++)
            {
                int index = (row - 1) * 8 + (8 - col);

                var tile = analyses[index];

                var prevLetter = board[row, col];
                //Debug.Log($"Prev letter: {prevLetter}, current piece color: {tile.pieceOnTile}");

                var sr = tiles2[index].GetComponent<SpriteRenderer>();
                if (tile.pieceOnTile == PieceColor.White && prevLetter == "")
                {
                    // gained a piece
                    sr.color = new Color(67f / 255f, 128f / 255f, 67f / 255f);
                    board[row, col] = pieceThatMoved;

                }
                var textMesh = tiles2[index].GetComponentInChildren<TextMesh>();
                textMesh.text = board[row, col];
            }
        }


        //for (int i = 0; i < 64; i++)
        //{
        //    var sr = tiles2[i].GetComponent<SpriteRenderer>();
        //    sr.color = new Color(.5f, .5f, .5f);

        //    var textMesh = tiles2[i].GetComponentInChildren<TextMesh>();
        //    textMesh.text = ((analyses[i].pieceOnTile.ToString())[0]).ToString();
        //    if (analyses[i].pieceOnTile == PieceColor.None) textMesh.text = "";
        //}

        string fen = ConvertToFEN(board);
        Stockfish.inst.GetBestMove(fen);
        StartCoroutine(WaitForStockfishResponse());
    }

    IEnumerator WaitForStockfishResponse()
    {
        yield return new WaitUntil(() => Stockfish.inst.recommendedMove != "");
        responseMove = Stockfish.inst.recommendedMove;
        //Debug.Log("response move is " + responseMove);
        Stockfish.inst.recommendedMove = "";
    }

    void CreateSprites()
    {
        float step = 0.62f * 1.1f;
        Vector3 pos = tilesParent.position;
        for (int i = 0; i < 8; i++)
        {
            for (int x = 0; x < 8; x++)
            {
                var obj = Instantiate(tileObject, pos, Quaternion.identity, tilesParent);
                tiles2.Add(obj);
                pos.x -= step;
            }
            pos.x += step * 8;
            pos.y += step;
        }
    }
}
