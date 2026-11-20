# Architecture — PCB Inspector AI

## 1. System Overview

PCB Inspector AI is a locally executed, reference-based PCB component inspection application.

The system uses a Streamlit interface and a modular Python computer-vision pipeline. A reference PCB image is annotated with component names and bounding boxes. Uploaded test images are aligned with the reference and inspected at the registered component locations.

The application produces three possible component statuses:

- PRESENT
- MISSING
- UNCERTAIN

All inspection processing is performed locally using installed Python libraries.

## 2. Architecture Diagram

The system architecture diagram is generated using Archify.

**Diagram export:** `docs/architecture.png`

**Interactive diagram:** `docs/architecture.html`

The exported diagram illustrates the user interface, annotation management, local file storage, preprocessing, image alignment, inspection orchestration and component inspection flow.

The interactive HTML diagram is the standalone architecture artifact. The PNG export is provided for convenient review and submission. The diagram passed Archify's automated validation and browser checks, followed by a visual review of the 2048 × 1320 light-theme capture.

## 3. Architectural Components

### 3.1 User Interface — `app.py`

Streamlit provides the application's interaction layer.

Responsibilities:

- Reference image upload.
- Component annotation interface.
- Annotation management.
- Test image upload.
- Inspection execution.
- Alignment diagnostics.
- Component classification display.
- Color-coded inspection visualization.

### 3.2 Annotation Module — `src/annotation.py`

Manages component annotations and their persistence.

Responsibilities:

- Saving component annotations.
- Loading saved annotations.
- Adding component annotations.
- Deleting annotations.

Annotations contain normalized component coordinates and component names.

### 3.3 Preprocessing Module — `src/preprocessing.py`

Handles image loading and preparation.

Responsibilities:

- Loading images.
- Validating image arrays.
- Grayscale conversion.
- Image preprocessing for alignment.

### 3.4 Alignment Module — `src/alignment.py`

Aligns test images with the reference PCB image.

Processing stages:

1. Detect ORB keypoints and descriptors.
2. Match binary descriptors using Hamming distance.
3. Apply Lowe's ratio test.
4. Estimate homography using RANSAC.
5. Evaluate alignment diagnostics.
6. Warp the test image into reference coordinates.

### 3.5 Detection Module — `src/detection.py`

Compares registered component regions.

Responsibilities:

- Extracting reference and test component regions.
- Calculating SSIM.
- Calculating normalized mean absolute pixel difference.
- Applying threshold-based classification.
- Returning component-level inspection measurements.

Classification outputs:

| Status | Interpretation |
|---|---|
| PRESENT | Similarity criteria indicate the component is present |
| MISSING | Difference criteria indicate a potentially missing component |
| UNCERTAIN | Evidence is insufficient for a confident decision |

### 3.6 Inspection Module — `src/inspection.py`

Coordinates the inspection workflow.

Responsibilities:

- Aligning test images with the reference.
- Handling alignment failures.
- Invoking component inspection.
- Aggregating present, missing and uncertain component results.
- Returning inspection summaries.

### Visualization Implementation

Inspection result visualization is currently implemented directly in `app.py` using OpenCV and Streamlit. `src/visualization.py` exists as an empty placeholder and is not currently part of the functional pipeline.

### 3.7 Testing Layer — `tests/`

Contains automated tests for component region extraction, similarity calculations, classification behavior and input validation.

The current test suite contains eight passing tests.

## 4. Data Storage

The application uses local files rather than a remote database.

| Data | Location | Purpose |
|---|---|---|
| Reference PCB image | `data/reference/` | Baseline image |
| Reference metadata | `data/reference/metadata.json` | Reference image information |
| Component annotations | `data/annotations/` | Named component coordinates |
| Test images | `data/test_images/` | Local inspection examples |

## 5. End-to-End Inspection Flow

1. The user uploads a complete reference PCB image.
2. The user annotates and names components.
3. The application stores the annotations in JSON.
4. The user uploads one or more test images.
5. Preprocessing prepares the images.
6. ORB feature matching and homography estimation align each test image.
7. The detection module extracts registered component regions.
8. SSIM and normalized pixel difference are calculated.
9. Threshold-based classification assigns a component status.
10. The inspection module aggregates the results.
11. Streamlit displays the results and visual bounding boxes.

If alignment fails, the application reports the failure rather than proceeding with an unreliable comparison.

## 6. Architectural Decisions and Trade-offs

### Modular Python architecture

Separate modules are used for preprocessing, annotation, alignment, detection and inspection.

**Benefit:** Individual components are easier to understand, test and maintain.

**Trade-off:** More modules require clear interfaces and coordination.

### Reference-based inspection

The system compares uploaded images against a manually annotated reference.

**Benefit:** Does not require a labelled training dataset or model training.

**Trade-off:** Inspection depends on the quality of the reference image and component annotations.

### Classical computer vision

ORB, homography, SSIM and pixel difference are used instead of a trained deep-learning model.

**Benefit:** Lightweight local processing and interpretable intermediate measurements.

**Trade-off:** Changes in imaging conditions and component appearance can affect classification.

### Three-state classification

The system supports PRESENT, MISSING and UNCERTAIN.

**Benefit:** Ambiguous cases are not automatically forced into a binary decision.

**Trade-off:** UNCERTAIN results require manual review.

### Local file storage

Images and annotations are stored locally.

**Benefit:** No remote database or hosted inference service is required.

**Trade-off:** The prototype does not provide centralized multi-user data management.

## 7. Offline and Runtime Architecture

The inspection workflow runs locally using installed Python libraries and local files.

The application does not depend on hosted computer-vision inference APIs, cloud databases or remote application servers during normal inspection.

Dependency installation may require internet access unless the required packages are already installed.

## 8. Known Limitations

- Alignment quality depends on shared visual features.
- Significant camera and lighting differences may affect matching.
- Classification thresholds are provisional.
- Synthetic validation does not establish real-world inspection accuracy.
- Manual component registration is required.
- The current interface supports up to three test images per inspection session.

## 9. Future Architectural Improvements

- Introduce a larger validation dataset.
- Add real-world physical component-removal tests.
- Support component-specific threshold calibration.
- Improve handling of alignment failures.
- Add structured inspection history and report export.
- Expand support for different PCB designs.

## 10. Conclusion

The architecture separates user interaction, image preprocessing, image alignment, component detection and inspection orchestration.

This modular design supports offline execution, transparent inspection results and incremental improvements to the computer-vision pipeline.
