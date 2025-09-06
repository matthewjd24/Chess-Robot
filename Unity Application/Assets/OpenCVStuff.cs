using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using OpenCvSharp;
using System.IO;
using System.Linq;

[ExecuteInEditMode]
public class OpenCVStuff : MonoBehaviour
{
    public static OpenCVStuff inst;
    public RawImage rawImage;
    [SerializeField] SpriteRenderer rend;
    [SerializeField] List<SpriteRenderer> tileSprites = new();
    [SerializeField] List<SpriteRenderer> grayTileSprites = new();
    [SerializeField] List<SpriteRenderer> solidTileSprites = new();
    [SerializeField] GameObject spriteObj;
    [SerializeField] SpriteRenderer originalPic;
    [SerializeField] SpriteRenderer undistortedPic;
    [SerializeField] SpriteRenderer transformedBoard;
    [SerializeField] SpriteRenderer greyTilesParent;
    [SerializeField] Transform spritesParent;
    [SerializeField] float distortionCoeff = .15f;
    [SerializeField] float distortionCoeff2 = 0;
    [SerializeField] float zoom = 1.0f;
    [SerializeField] Vector3 whiteLowerBound;
    [SerializeField] Vector3 whiteUpperBound;
    [SerializeField] Vector3 blackLowerBound;
    [SerializeField] Vector3 blackUpperBound;

    private void Awake()
    {
        inst = this;
    }

    public List<MatAndColors> AnalyzeImage()
    {
        var original = GetOriginalImage();
        originalPic.sprite = MatToSprite(original);
        var undistorted = Undistort(original);
        undistortedPic.sprite = MatToSprite(undistorted);
        var transformed = DoCornerThing(undistorted);
        transformedBoard.sprite = MatToSprite(transformed);
        var tiles = SplitTo64(transformed);
        for (int i = 0; i < 64; i++)
        {
            tileSprites[i].sprite = MatToSprite(tiles[i]);
        }

        List<MatAndColors> tileAnalyses = DoTileAnalyses(tiles);
        List<MatAndColors> DoTileAnalyses(List<Mat> tiles)
        {
            List<MatAndColors> ret = new();
            for (int i = 0; i < tiles.Count; i++)
            {
                MatAndColors analysis = AnalyzeOneTile(tiles[i], i);
                MatAndColors AnalyzeOneTile(Mat img, int index)
                {
                    bool tileIsLight = GetIsLightTile(index);

                    MatAndColors result = new();

                    var (blackMat, blackness) = AnalyzeBlackRegions(img);
                    result.blackMat = blackMat;
                    result.blackness = (float)blackness;
                    bool hasBlackPiece = result.blackness > blackPixelPercentCutoff;

                    var (whiteMat, whiteness) = AnalyzeWhiteRegions(img, tileIsLight, hasBlackPiece);
                    result.whiteMat = whiteMat;
                    result.whiteness = (float)whiteness;
                    bool hasWhitePiece = result.whiteness > whitePixelpercentCutoff;

                    if (hasWhitePiece && !hasBlackPiece)
                    {
                        result.bestMat = whiteMat;
                        result.bestPercentage = (float)whiteness;
                        result.pieceOnTile = PieceColor.White;
                    }
                    else if (hasBlackPiece)
                    {
                        result.bestMat = blackMat;
                        result.bestPercentage = (float)blackness;
                        result.pieceOnTile = PieceColor.Black;
                    }
                    else
                    {
                        result.bestMat = whiteMat;
                        if (result.whiteness > result.blackness) result.bestPercentage = result.whiteness;
                        else result.bestPercentage = result.blackness;
                        result.pieceOnTile = PieceColor.None;
                    }


                    //else
                    //{
                    //    result.bestMat = blackMat;
                    //    result.bestPercentage = (float)blackness;
                    //    if (result.bestPercentage > .05f)
                    //    {
                    //        result.pieceOnTile = PieceColor.Black;
                    //    }
                    //}

                    return result;
                }
                ret.Add(analysis);
            }
            return ret;
        }
        for (int i = 0; i < 64; i++)
        {
            grayTileSprites[i].sprite = MatToSprite(tileAnalyses[i].bestMat);
            //if (tileAnalyses[i].blackness < blackPixelPercentCutoff) grayTileSprites[i].sprite = null;
            var sr = solidTileSprites[i];
            if (tileAnalyses[i].pieceOnTile == PieceColor.None) sr.color = new Color(.45f, .45f, .45f);
            else if (tileAnalyses[i].pieceOnTile == PieceColor.White) sr.color = new Color(.8f, .8f, .8f);
            else sr.color = new Color(.1f, .1f, .1f);
        }
        return tileAnalyses;
    }

    Mat DoCornerThing(Mat undistorted)
    {
        SpriteRenderer sr = undistortedPic;
        Vector2 spriteSize = sr.sprite.rect.size; // in pixels
        Vector2 spriteWorldSize = sr.bounds.size; // in world units
        List<Vector2> cornerPositions = new();

        foreach (Transform corner in undistortedPic.transform)
        {
            Vector2 localPos = corner.localPosition;

            // Normalize local position to [0, 1] range based on sprite's bounds
            float percentX = (localPos.x + spriteWorldSize.x / 2f) / spriteWorldSize.x;
            float percentY = 1f - (localPos.y + spriteWorldSize.y / 2f) / spriteWorldSize.y;
            cornerPositions.Add(new Vector2(percentX, percentY));
        }
        var mat = WarpChessboard(undistorted, cornerPositions);
        return mat;
    }

    //List<MatAndColors> CreateSprites(List<Mat> tiles, Transform point)
    //{
    //    float step = 0.62f * 1.1f;
    //    Vector3 pos = point.position;
    //    //for (int i = 0; i < 8; i++)
    //    //{
    //    //    for (int x = 0; x < 8; x++)
    //    //    {
    //    //        var obj = Instantiate(spriteObj, pos, Quaternion.identity, spritesParent);
    //    //        pos.x -= step;
    //    //    }
    //    //    pos.x += step * 8;
    //    //    pos.y += step;
    //    //}

    //    //#if UNITY_EDITOR
    //    //    foreach (Transform child in point.transform)
    //    //    {
    //    //        DestroyImmediate(child.gameObject);
    //    //    }
    //    //#else

    //    //#endif

    //    bool hasChildren = false;
    //    if (point.childCount > 0) hasChildren = true;

    //    List<MatAndColors> ret = new();
    //    for (int i = 0; i < tiles.Count; i++)
    //    {

    //        var filteredTile = DoColorAnalysis(tiles[i]);
    //        Mat filtered = filteredTile.whiteMat;
    //        ret.Add(filteredTile);

    //        Mat oneToShow = filteredTile.whiteMat;
    //        if (filteredTile.blackness > filteredTile.whiteness) oneToShow = filteredTile.blackMat;

    //        if(!hasChildren)
    //        {
    //            var obj = Instantiate(spriteObj, pos, Quaternion.identity, point);
    //            obj.GetComponent<SpriteRenderer>().sprite = MatToSprite(oneToShow);
    //        }
    //        else
    //        {
    //            point.GetChild(i).GetComponent<SpriteRenderer>().sprite = MatToSprite(oneToShow);
    //        }

    //        pos.x -= step;

    //        if((i+1) % 8 == 0)
    //        {
    //            pos.y += step;
    //            pos.x += step * 8;
    //        }
    //    }

    //    return ret;
    //}

    private void Update()
    {
        //ShowImage();
    }

    Mat GetOriginalImage()
    {
        string imagePath = @"C:\Users\matt\Documents\GitHub\Chess-Robot\captured_image.jpg"; //Path.Combine(Application.streamingAssetsPath, "board3.jpg");
        if (!File.Exists(imagePath))
        {
            Debug.LogError("Image not found: " + imagePath);
            return null;
        }
        var imgFile = Cv2.ImRead(imagePath);
        if (imgFile.Empty())
        {
            Debug.LogError("Failed to load image: " + imagePath);
            return null;
        }
        return imgFile;
    }

    void showTiles()
    {
        //transformedBoard.sprite = MatToSprite(newImgFile);

        //FindCorners(newImgFile);
        //transformedBoard.sprite = MatToSprite(unwarped);

        //List<string> corners = File.ReadAllLines("corners.txt").ToList();
        //Point2f[] cornersArray = new Point2f[corners.Count];
        //for (int i = 0; i < corners.Count; i++)
        //{
        //    string[] split = corners[i].Split(";");
        //    cornersArray[i].X = float.Parse(split[0]);
        //    cornersArray[i].Y = float.Parse(split[1]);
        //}

        //// Display in UI
        //var unwarped = WarpChessboard(imgFile, cornersArray);
        //List<Mat> tiles = SplitTo64(unwarped);

        //for (int i = 0; i < 64; i++)
        //{
        //    //Debug.Log(tiles[i].Width);
        //    tileSprites[i].sprite = MatToSprite(tiles[i]);
        //}

        //transformedBoard.sprite = MatToSprite(unwarped);

        //for (int i = 0; i < 64; i++)
        //{

        //    rawImage.texture = ConvertToTex(tiles[i]);
        //    yield return new WaitForSeconds(0.25f);
        //}
    }

    Sprite MatToSprite(Mat mat)
    {
        if (mat == null) return null;

        Texture2D tex = ConvertToTex(mat);
        return Sprite.Create(tex, new UnityEngine.Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f));
    }

    Texture2D ConvertToTex(Mat mat)
    {
        // Convert BGR to RGB
        Mat rgb = new Mat();
        Cv2.CvtColor(mat, rgb, ColorConversionCodes.BGR2RGB);

        // Flip vertically to match Unity's origin
        Cv2.Flip(rgb, rgb, 0);

        int width = rgb.Width;
        int height = rgb.Height;
        Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);

        byte[] data = new byte[rgb.Total() * rgb.ElemSize()];
        System.Runtime.InteropServices.Marshal.Copy(rgb.Data, data, 0, data.Length);

        tex.LoadRawTextureData(data);
        tex.Apply();

        tex.wrapMode = TextureWrapMode.Clamp;
        return tex;
    }

    Mat Undistort(Mat image)
    {
        int h = image.Rows;
        int w = image.Cols;

        // Create camera matrix K manually
        Mat K = new Mat(3, 3, MatType.CV_32F);
        K.Set<float>(0, 0, w);
        K.Set<float>(0, 1, 0);
        K.Set<float>(0, 2, w / 2f);
        K.Set<float>(1, 0, 0);
        K.Set<float>(1, 1, h);
        K.Set<float>(1, 2, h / 2f);
        K.Set<float>(2, 0, 0);
        K.Set<float>(2, 1, 0);
        K.Set<float>(2, 2, 1);

        // Distortion coefficients
        Mat D = new Mat(1, 4, MatType.CV_32F);
        D.Set<float>(0, 0, distortionCoeff);
        D.Set<float>(0, 1, distortionCoeff);
        D.Set<float>(0, 2, distortionCoeff2);
        D.Set<float>(0, 3, distortionCoeff2);

        // Identity matrix for rectification
        Mat I = Mat.Eye(3, 3, MatType.CV_32F);

        Mat newK = new Mat();
        Cv2.FishEye.EstimateNewCameraMatrixForUndistortRectify(K, D, new Size(w, h), I, newK, zoom);

        Mat map1 = new Mat();
        Mat map2 = new Mat();
        Cv2.FishEye.InitUndistortRectifyMap(K, D, I, newK, new Size(w, h), (int)MatType.CV_16SC2, map1, map2);

        Mat undistorted = new Mat();
        Cv2.Remap(image, undistorted, map1, map2, InterpolationFlags.Linear, BorderTypes.Constant);

        return undistorted;
    }

    void FindCorners(Mat rawImage)
    {
        // Convert to grayscale
        Mat gray = new Mat();
        Cv2.CvtColor(rawImage, gray, ColorConversionCodes.BGR2GRAY);

        // Histogram equalization
        //Mat equalized = new Mat();
        //Cv2.EqualizeHist(gray, equalized);

        // Gaussian blur
        //Mat blurred = new Mat();
        //Cv2.GaussianBlur(gray, gray, new Size(9, 9), 0);

        // Find chessboard corners
        Size patternSize = new Size(7, 7);
        Point2f[] corners;
        bool found = Cv2.FindChessboardCorners(gray, patternSize, out corners);

        if (found)
        {
            // Refine corners to subpixel accuracy
            TermCriteria criteria = new TermCriteria(CriteriaTypes.Eps | CriteriaTypes.MaxIter, 30, 0.001);
            Cv2.CornerSubPix(gray, corners, new Size(11, 11), new Size(-1, -1), criteria);

            string save = "";
            foreach (var pt in corners)
            {
                save += pt.X + ";" + pt.Y + "\n";
            }
            File.WriteAllText("corners.txt", save);
            Debug.Log("Corners found");
        }
        else
        {
            Debug.LogError("No corners found");
        }
    }

    Mat WarpChessboard(Mat image, List<Vector2> normalizedCorners)
    {
        if (normalizedCorners == null || normalizedCorners.Count != 4)
            return null;

        int width = image.Width;
        int height = image.Height;

        // Convert normalized percentages to absolute pixel coordinates
        Point2f bottomRight = new Point2f(normalizedCorners[0].x * width, normalizedCorners[0].y * height);
        Point2f bottomLeft = new Point2f(normalizedCorners[1].x * width, normalizedCorners[1].y * height);
        Point2f topRight = new Point2f(normalizedCorners[2].x * width, normalizedCorners[2].y * height);
        Point2f topLeft = new Point2f(normalizedCorners[3].x * width, normalizedCorners[3].y * height);

        // Optional debug output
        //Mat debug = image.Clone();
        //Cv2.Circle(debug, 0, 0, 5, Scalar.Red, -1);
        //Cv2.Circle(debug, 0, (int)height/2, 5, Scalar.Aqua, -1);
        //Cv2.Circle(debug, (int)topLeft.X, (int)topLeft.Y, 5, Scalar.Firebrick, -1);
        //Cv2.Circle(debug, (int)topRight.X, (int)topRight.Y, 5, Scalar.Green, -1);
        //Cv2.Circle(debug, (int)bottomLeft.X, (int)bottomLeft.Y, 5, Scalar.Blue, -1);
        //Cv2.Circle(debug, (int)bottomRight.X, (int)bottomRight.Y, 5, Scalar.Yellow, -1);
        //Cv2.ImWrite("chessboard_corners_debug.jpg", debug); // optional

        // Warp image using the four corner points
        Point2f[] srcPoints = new[] { topLeft, topRight, bottomLeft, bottomRight };
        Point2f[] dstPoints = new[]
        {
            new Point2f(0, 0),
            new Point2f(499, 0),
            new Point2f(0, 499),
            new Point2f(499, 499)
        };

        Mat M = Cv2.GetPerspectiveTransform(srcPoints, dstPoints);
        Mat warped = new Mat();
        Cv2.WarpPerspective(image, warped, M, new Size(500, 500));

        // Flip to match expected orientation
        Cv2.Flip(warped, warped, FlipMode.XY);

        return warped;
    }

    [SerializeField] float zoomedPercentage = .92f;
    List<Mat> SplitTo64(Mat warpedImage)
    {
        int height = warpedImage.Rows;
        int width = warpedImage.Cols;

        float cellHeight = height / 8f;
        float cellWidth = width / 8f;
        //Debug.Log(width + ", " + cols + ", " + cellWidth);

        List<Mat> cellImages = new List<Mat>();

        for (int i = 7; i >= 0; i--)
        {
            for (int j = 7; j >= 0; j--)
            {
                float offset = (1f - zoomedPercentage) / 2f;
                int xStart = (int)(j * cellWidth + offset * cellWidth);
                int yStart = (int)(i * cellHeight + offset * cellHeight);

                int zoomedCellWidth = (int)(cellWidth * zoomedPercentage);
                int zoomedCellHeight = (int)(cellHeight * zoomedPercentage);

                // Use Rect to extract region
                OpenCvSharp.Rect roi = new OpenCvSharp.Rect(xStart, yStart, zoomedCellWidth, zoomedCellHeight);
                Mat cell = new Mat(warpedImage, roi).Clone(); // Clone to make it independent

                cellImages.Add(cell);
            }
        }

        return cellImages;
    }

    bool GetIsLightTile(int index)
    {
        int row = index / 8;
        int col = index % 8;

        // Light if row + col is even
        return (row + col) % 2 == 0;
    }


    double GetPixelColorPercentageBlack(Mat img)
    {
        // Convert to BGR if needed
        if (img.Channels() == 4)
            Cv2.CvtColor(img, img, ColorConversionCodes.BGRA2BGR);

        // Define lower and upper bounds for white in BGR
        Scalar lower = new Scalar(blackLowerBound.x, blackLowerBound.y, blackLowerBound.z);
        Scalar upper = new Scalar(blackUpperBound.x, blackUpperBound.y, blackUpperBound.z);

        Mat mask = new Mat();
        Cv2.InRange(img, lower, upper, mask);

        int whitePixels = Cv2.CountNonZero(mask);
        int totalPixels = img.Rows * img.Cols;

        return (double)whitePixels / totalPixels;
    }

    (Mat maskVisualization, double blackPercentage) AnalyzeBlackRegions(Mat img)
    {
        Mat imgBGR = img.Clone(); // Avoid modifying the original
        if (imgBGR.Channels() == 4)
            Cv2.CvtColor(imgBGR, imgBGR, ColorConversionCodes.BGRA2BGR);

        Mat imgHSV = new Mat();
        Cv2.CvtColor(imgBGR, imgHSV, ColorConversionCodes.BGR2HSV);

        Scalar lower = new Scalar(blackLowerBound.x, blackLowerBound.y, blackLowerBound.z);
        Scalar upper = new Scalar(blackUpperBound.x, blackUpperBound.y, blackUpperBound.z);

        Mat mask = new Mat();
        Cv2.InRange(imgHSV, lower, upper, mask);

        int blackPixels = Cv2.CountNonZero(mask);
        int totalPixels = img.Rows * img.Cols;
        double percentage = (double)blackPixels / totalPixels;

        Scalar grayColor = new Scalar(128, 128, 128);
        Mat result = new Mat(img.Size(), img.Type(), grayColor);
        imgBGR.CopyTo(result, mask);

        return (result, percentage);
    }

    [SerializeField] float minHue;
    [SerializeField] float maxHue;
    [SerializeField] float lowerValueThreshold;
    [SerializeField] float upperValueThreshold;

    (Mat maskVisualization, double whitePercentage) AnalyzeWhiteRegions(Mat img, bool tileIsLight, bool containsBlackPiece)
    {
        // does three things for adding pixels to the mask:
        //      for light tiles, any pixel with a hue outside the normal light-tile hue range
        //      for light tiles, any pixel with a value below the normal light-tile value range
        //      otherwise, all pixels between the color bounds

        Mat imgBGR = img.Clone(); // Avoid modifying the original
        if (imgBGR.Channels() == 4)
            Cv2.CvtColor(imgBGR, imgBGR, ColorConversionCodes.BGRA2BGR);

        Mat imgHSV = new Mat();
        Cv2.CvtColor(imgBGR, imgHSV, ColorConversionCodes.BGR2HSV);

        // Base white range mask
        Scalar lower = new Scalar(whiteLowerBound.x, whiteLowerBound.y, whiteLowerBound.z);
        Scalar upper = new Scalar(whiteUpperBound.x, whiteUpperBound.y, whiteUpperBound.z);
        Mat whiteRangeMask = new Mat();
        Cv2.InRange(imgHSV, lower, upper, whiteRangeMask);

        Mat combinedMask = whiteRangeMask;

        //if (tileIsLight)
        //{
        //    // Hue-based mask
        //    Scalar lowerHue = new Scalar(minHue * 179f, 0, 60);
        //    Scalar upperHue = new Scalar(maxHue * 179f, 255, 255);
        //    Mat hueRangeMask = new Mat();
        //    Cv2.InRange(imgHSV, lowerHue, upperHue, hueRangeMask);

        //    //// Value-based dark pixel mask

        //    //Scalar lowerVal = new Scalar(0, 0, lowerValueThreshold * 255f);
        //    //Scalar upperVal = new Scalar(255f, 255, upperValueThreshold * 255f);
        //    //Mat darkValueMask = new Mat();
        //    //Cv2.InRange(imgHSV, lowerVal, upperVal, darkValueMask);

        //    // OR all masks together
        //    Mat tempMask = new Mat();
        //    Cv2.BitwiseOr(whiteRangeMask, hueRangeMask, tempMask);
        //    //Cv2.BitwiseOr(tempMask, darkValueMask, combinedMask);
        //}

        int whitePixels = Cv2.CountNonZero(combinedMask);
        int totalPixels = img.Rows * img.Cols;
        double percentage = (double)whitePixels / totalPixels;

        Scalar grayColor = new Scalar(128, 128, 128);
        Mat result = new Mat(img.Size(), img.Type(), grayColor);
        imgBGR.CopyTo(result, combinedMask);

        if (containsBlackPiece) percentage = 0f;

        return (result, percentage);
    }


    

    [SerializeField] float blackPixelPercentCutoff = .15f;
    [SerializeField] float whitePixelpercentCutoff = .15f;
    
}
public enum PieceColor
{
    None,
    White,
    Black
}
public struct MatAndColors
{
    public PieceColor pieceOnTile;
    public Mat bestMat;
    public float bestPercentage;
    public Mat whiteMat;
    public Mat blackMat;
    public float whiteness;
    public float blackness;
}
