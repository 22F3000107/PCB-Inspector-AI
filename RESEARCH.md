# Research and Technology Decisions — PCB Inspector AI

## 1. Research Objective

The objective of this project is to develop an offline, reference-based PCB component inspection system.

The system should:

1. Accept an image of a complete reference PCB.
2. Allow users to register and name components manually.
3. Align test PCB images with the reference.
4. Compare the registered component regions.
5. Identify potentially missing components.
6. Display inspection results locally without depending on hosted AI services.

The research focused on classical computer vision techniques that could support this workflow on a local computer.

## 2. Research Areas

The main areas investigated were:

- Image preprocessing and grayscale conversion.
- Feature detection and description.
- Feature matching.
- Geometric image registration.
- Structural similarity measurement.
- Pixel difference measurement.
- Rule-based classification.
- Local application development.

## 3. Technology Selection

### 3.1 Image Alignment — ORB

**Selected technique:** ORB (Oriented FAST and Rotated BRIEF).

ORB detects local image features and computes binary descriptors that can be matched between images.

The implementation uses:

- ORB feature detection.
- Hamming-distance feature matching.
- Lowe's ratio test to filter ambiguous matches.
- Homography estimation using RANSAC.
- Perspective warping to align the test image with the reference.

**Why it was selected:**

- It is suitable for local computer-vision processing.
- It uses binary descriptors and efficient matching.
- It does not require a trained neural network.
- It is available through OpenCV.

The ORB research paper describes it as a computationally efficient alternative to SIFT and SURF.

**Reference:**

Rublee, E., Rabaud, V., Konolige, K., and Bradski, G. (2011). *ORB: An efficient alternative to SIFT or SURF.* IEEE International Conference on Computer Vision.

https://doi.org/10.1109/ICCV.2011.6126544

### 3.2 Geometric Registration — Homography and RANSAC

**Selected technique:** Homography estimation with RANSAC.

A homography maps corresponding points between two images under a projective transformation.

RANSAC helps estimate the transformation while rejecting inconsistent feature matches.

The implementation checks alignment quality using:

- Number of good matches.
- Number of inliers.
- Inlier ratio.
- Mean reprojection error.

The estimated homography is used to warp the test image into the reference image dimensions.

**Why it was selected:**

- It supports perspective changes between images of the same planar PCB.
- RANSAC provides robustness against incorrect feature matches.
- OpenCV provides the required functionality locally.

**Reference:**

OpenCV documentation — Camera calibration and 3D reconstruction, including homography estimation and robust methods.

https://docs.opencv.org/doc/doxygen/html/d2/d48/group__d__projection.html

### 3.3 Structural Similarity — SSIM

**Selected technique:** Structural Similarity Index (SSIM).

SSIM compares image structure rather than relying only on raw pixel-level error.

It is used to compare the reference component region with the corresponding aligned test region.

**Why it was selected:**

- It provides a structural similarity measurement.
- It complements direct pixel-difference measurements.
- It is available through scikit-image.
- It can be used without training a machine-learning model.

**Reference:**

Wang, Z., Bovik, A. C., Sheikh, H. R., and Simoncelli, E. P. (2004). *Image quality assessment: From error visibility to structural similarity.* IEEE Transactions on Image Processing, 13(4), 600–612.

https://doi.org/10.1109/TIP.2003.819861

scikit-image documentation:

https://scikit-image.org/docs/stable/api/skimage.metrics.html

### 3.4 Pixel Difference

**Selected technique:** Normalized mean absolute pixel difference.

The implementation calculates a normalized difference between the reference and test component regions.

This measurement complements SSIM because structural similarity and pixel intensity difference provide different information.

A component may have a low structural similarity score and a high pixel difference when its appearance changes significantly.

Using both measurements provides a simple basis for three-state classification.

### 3.5 Rule-Based Classification

**Selected technique:** Threshold-based classification.

Each registered component is assigned one of three statuses:

- `PRESENT`
- `MISSING`
- `UNCERTAIN`

The current provisional thresholds are:

| Parameter | Value |
|---|---:|
| Present SSIM threshold | 0.60 |
| Present difference threshold | 0.12 |
| Missing SSIM threshold | 0.45 |
| Missing difference threshold | 0.10 |

The classification logic uses both SSIM and normalized pixel difference.

If the measurements do not satisfy either the presence or missing criteria, the component is classified as UNCERTAIN.

**Why it was selected:**

- It is interpretable.
- It does not require labelled training data.
- It is computationally inexpensive.
- It supports a manual-review outcome when evidence is inconclusive.

The thresholds were adjusted using initial synthetic experiments. They have not been calibrated against a representative real-world PCB dataset.

## 4. Alternatives Considered

The following table describes the design alternatives considered at the technology-selection stage. These alternatives were not all implemented or experimentally benchmarked in this project.

| Area | Selected approach | Alternatives considered | Reason for selection |
|---|---|---|---|
| Feature detection | ORB | SIFT, SURF | Efficient binary descriptors and local processing |
| Feature matching | BFMatcher with Hamming distance | FLANN-based matching | Compatible with binary ORB descriptors |
| Image registration | Homography with RANSAC | Affine transformation | Supports projective alignment and rejects outliers |
| Image similarity | SSIM | MSE, PSNR | Structural comparison complements pixel difference |
| Classification | Rule-based thresholds | Supervised ML classifier | No labelled training dataset was provided |
| Interface | Streamlit | Custom web application | Rapid local application development |

### 4.1 Why not use a deep-learning detector?

A deep-learning object detector could identify component categories and locations, but this project did not include a labelled PCB training dataset.

Training and validating such a detector would require additional data collection and annotation.

A reference-based comparison workflow was therefore selected for the initial prototype.

### 4.2 Why not use cloud-based vision APIs?

The assignment requires offline operation.

Cloud-based inference APIs would introduce network dependencies and would not satisfy the intended local inspection workflow.

The implementation therefore uses locally installed computer-vision libraries.

## 5. Data and Experimental Approach

No labelled PCB dataset was supplied with the assignment.

The initial experiments used a reference PCB image and manually registered component regions.

Three components were registered:

- U1
- C1
- R1

Synthetic test images were created to examine the detector's behavior.

The experiments included:

1. A transformed copy of the reference PCB.
2. A synthetic image with U1 removed.
3. A synthetic image with C1 removed.
4. A synthetic image with R1 removed.

The missing-component images were generated using OpenCV inpainting within the annotated component regions.

This provides controlled examples for testing the initial comparison pipeline.

These are synthetic experiments, not photographs of physically removed components.

## 6. Experimental Results

The initial validation produced the following results:

| Scenario | Expected result | Observed result |
|---|---|---|
| Complete transformed PCB | U1, C1 and R1 PRESENT | Passed |
| U1 synthetically removed | U1 MISSING; C1 and R1 PRESENT | Passed |
| C1 synthetically removed | C1 MISSING; U1 and R1 PRESENT | Passed |
| R1 synthetically removed | R1 MISSING; U1 and C1 PRESENT | Passed |

The automated test suite contains eight tests covering region extraction, similarity calculation, classification behavior, component inspection and empty annotation validation.

Latest test result: **8 tests passed.**

These results demonstrate that the initial implementation behaves as expected on the selected controlled examples. They should not be interpreted as a measured production accuracy or a generalization guarantee.

## 7. Limitations and Risks

### Image alignment

- ORB matching may fail when images have insufficient shared visual features.
- Significant changes in lighting or image quality may affect feature matching.
- A homography cannot correct arbitrary three-dimensional changes or severe non-planar distortions.

### Component comparison

- SSIM and pixel difference are sensitive to image quality and local appearance changes.
- Thresholds may need adjustment for different component types and imaging conditions.
- Components with similar surrounding patterns may be difficult to distinguish.

### Experimental validation

- The initial validation set is small.
- Synthetic inpainting does not reproduce every visual characteristic of physical component removal.
- The system has not been evaluated across a representative collection of PCBs, cameras and lighting conditions.

### Operational limitations

- Components must be registered manually.
- The application currently supports up to three test images per inspection session.
- UNCERTAIN classifications require human review.

## 8. Future Research

Potential future improvements include:

1. Testing with real PCB photographs containing physically removed components.
2. Building a larger and more representative validation dataset.
3. Measuring false-positive and false-negative rates.
4. Evaluating different alignment and similarity techniques.
5. Exploring adaptive thresholds for different component types.
6. Investigating feature-based or learned component representations if labelled data becomes available.

## 9. Summary

The project uses a classical computer-vision pipeline combining ORB feature matching, homography-based image alignment, SSIM, normalized pixel difference and rule-based classification.

This approach was selected because it is interpretable, computationally practical and compatible with offline execution.

Initial synthetic experiments demonstrate the intended behavior for the registered components. Further testing with real PCB inspection images is necessary before the system can be considered suitable for production use.
