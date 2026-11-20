# PCB Inspector AI — Reference-Based Component Inspection

An offline computer-vision application that detects potentially missing components on a printed circuit board (PCB) by comparing a test image against a manually annotated reference image.

## 1. Project Overview

PCB Inspector AI helps identify missing electronic components by comparing the locations of registered components in a reference PCB image with their appearance in uploaded test images.

The application uses classical computer vision techniques to:

- Register a reference PCB image.
- Allow users to manually annotate and name components.
- Align test images with the reference image.
- Compare corresponding component regions.
- Classify components as `PRESENT`, `MISSING`, or `UNCERTAIN`.
- Display inspection results with visual bounding boxes.

The application is designed to operate locally without requiring hosted AI services or online inference APIs.

## 2. Key Features

- **Reference image registration:** Upload a PCB reference image.
- **Manual component annotation:** Draw bounding boxes and assign component names.
- **Persistent annotations:** Save and reload component coordinates.
- **Image alignment:** Use ORB feature detection and homography estimation to align test images.
- **Component comparison:** Use Structural Similarity Index (SSIM) and normalized pixel difference.
- **Three-state classification:** Identify components as PRESENT, MISSING, or UNCERTAIN.
- **Visual inspection:** Display color-coded component bounding boxes.
- **Multiple test images:** Upload up to three test PCB images per inspection session.
- **Offline processing:** Perform image processing locally.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | User interface |
| OpenCV | Image processing, feature detection and alignment |
| NumPy | Numerical operations |
| Pillow | Image handling |
| scikit-image | SSIM-based similarity measurement |
| pytest | Automated testing |

## 4. Project Structure

```text
PCB-Inspector-AI/
│
├── app.py
├── requirements.txt
├── pytest.ini
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── alignment.py
│   ├── annotation.py
│   ├── detection.py
│   ├── inspection.py
│   └── visualization.py
│
├── data/
│   ├── reference/
│   │   ├── reference.png
│   │   └── metadata.json
│   │
│   ├── annotations/
│   │   └── reference_annotations.json
│   │
│   └── test_images/
│
├── tests/
│   └── test_detection.py
│
├── README.md
├── RESEARCH.md
├── AI_COLLAB.md
└── ARCHITECTURE.md
```

## 5. Installation

### Prerequisites

- Python 3.10 or later (developed and tested with Python 3.13.1).
- pip.
- Git.

### Clone the repository

```bash
git clone https://github.com/22F3000107/PCB-Inspector-AI.git

cd PCB-Inspector-AI
```

### Create a virtual environment

macOS / Linux:

```bash
python3 -m venv venv

source venv/bin/activate
```

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 7. How to Use

### Step 1 — Upload a reference PCB image

Upload a clear image of a complete PCB.

The reference image serves as the baseline for subsequent inspections.

### Step 2 — Annotate components

Draw bounding boxes around the components that need to be inspected.

Assign a unique component name to each annotation, such as:

- U1
- C1
- R1

Save the annotations.

The application stores the component locations as normalized coordinates.

### Step 3 — Upload test images

Upload up to three test images of the same PCB.

The images should show the same board and, where possible, similar camera angles and image quality.

### Step 4 — Automatic alignment

The application detects ORB features and estimates a homography using matched features and RANSAC.

The test image is warped into the reference image coordinate system.

### Step 5 — Component inspection

For every registered component, the application extracts the corresponding reference and test regions.

It calculates:

- Structural Similarity Index (SSIM).
- Normalized pixel difference.

The classification logic produces one of three outcomes:

| Status | Meaning |
|---|---|
| PRESENT | The region sufficiently resembles the reference component |
| MISSING | The region meets the configured missing-component criteria |
| UNCERTAIN | The comparison does not provide sufficient evidence for a confident classification |

### Step 6 — View inspection results

The application displays:

- Alignment diagnostics.
- Component-level similarity measurements.
- Overall inspection status.
- Color-coded bounding boxes.

Color convention:

- Green — PRESENT
- Red — MISSING
- Orange — UNCERTAIN

## 8. Image Alignment and Detection

### Image alignment

ORB (Oriented FAST and Rotated BRIEF) is used to detect and describe local image features.

Feature matching is performed using a Hamming-distance matcher and Lowe's ratio test.

A homography is estimated using RANSAC to align the test image with the reference image.

Alignment diagnostics include:

- Number of good matches.
- Inlier ratio.
- Mean reprojection error.

### Component comparison

The detector compares the reference and aligned test regions.

SSIM measures structural similarity, while normalized pixel difference measures intensity differences.

The initial classification thresholds are:

| Parameter | Value |
|---|---:|
| Present SSIM threshold | 0.60 |
| Present difference threshold | 0.12 |
| Missing SSIM threshold | 0.45 |
| Missing difference threshold | 0.10 |

These are provisional thresholds based on initial synthetic experiments. They are not production-calibrated values.

## 9. Testing

Run the automated test suite:

```bash
pytest -v
```

The tests cover:

- Component region extraction.
- Similarity calculation.
- Classification behavior.
- Inspection of identical component regions.
- Empty annotation validation.

The current automated test suite contains eight tests.

## 10. Current Validation

Initial experiments were conducted using a reference PCB image and synthetically generated test images.

| Scenario | Expected result | Observed result |
|---|---|---|
| Complete transformed PCB | All registered components PRESENT | Passed |
| U1 synthetically removed | U1 MISSING | Passed |
| C1 synthetically removed | C1 MISSING | Passed |
| R1 synthetically removed | R1 MISSING | Passed |

The missing-component images were generated using image inpainting to simulate component removal.

These experiments demonstrate initial pipeline behavior under controlled conditions. They do not establish real-world inspection accuracy.

## 11. Limitations

- Current classification thresholds are based on a small synthetic validation set.
- Physical component removal has not yet been comprehensively validated.
- Significant lighting, camera, perspective, and image-quality variations may affect results.
- Similar-looking PCB regions may produce misleading similarity measurements.
- Incorrect image alignment can affect component classification.
- The system currently relies on manually registered component locations.
- `UNCERTAIN` results require human review.

The application should be treated as an experimental inspection prototype rather than a production-ready quality-control system.

## 12. Offline Operation

The application performs its inspection workflow locally using installed Python libraries and local image files.

It does not require hosted inference APIs or cloud-based computer-vision services during normal operation.

Initial dependency installation may require internet access unless the required packages are already available locally.

## 13. Future Improvements

- Validate using physically removed components.
- Evaluate robustness across different lighting and camera conditions.
- Improve alignment failure handling.
- Develop adaptive or region-specific classification thresholds.
- Add more inspection metrics and confidence indicators.
- Support larger component annotation sets.
- Expand automated testing with more representative PCB images.

## 14. Author

**Deepak Kumar**

IIT Madras — BS in Data Science and Applications

GitHub: https://github.com/22F3000107

---

**Project:** PCB Inspector AI
**Category:** Computer Vision / Offline PCB Inspection
**Interface:** Streamlit
