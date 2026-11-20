# AI Collaboration Report — PCB Inspector AI

## 1. Overview

AI assistance was used during the development of PCB Inspector AI as a technical support and problem-solving resource.

The development process involved iterative discussions about project architecture, computer-vision techniques, implementation issues, testing, debugging and documentation.

AI suggestions were reviewed against the assignment requirements, the existing implementation and observed experimental results.

The developer retained responsibility for implementation choices, testing, validation and final decisions.

**AI assistant:** ChatGPT

**Project:** PCB Inspector AI — Reference-Based Component Inspection

**Repository:** https://github.com/22F3000107/PCB-Inspector-AI

## 2. Key Technical Decisions

The following decisions summarize important development discussions and implementation outcomes.

### Decision 1 — Selecting a reference-based inspection approach

- **AI suggestion:** Consider a computer-vision workflow that compares test PCB images against a known-good reference.
- **Developer decision:** Use reference-based inspection with manually registered component locations.
- **Reason:** The assignment did not provide a labelled training dataset. A reference-based approach could be developed without training a deep-learning model.
- **Evidence:** The application stores named component annotations and compares their corresponding regions in uploaded test images.

### Decision 2 — Selecting ORB for image alignment

- **AI suggestion:** Use local feature detection and matching to align test images before component comparison.
- **Developer decision:** Implement ORB feature detection and binary descriptor matching.
- **Reason:** ORB is suitable for local computer-vision processing and does not require a trained model.
- **Evidence:** `src/alignment.py` implements ORB and Hamming-distance matching.

### Decision 3 — Using homography estimation with RANSAC

- **AI suggestion:** Estimate a geometric transformation using matched image features and reject incorrect matches.
- **Developer decision:** Use homography estimation with RANSAC.
- **Reason:** Test images may have perspective and positional differences relative to the reference image.
- **Evidence:** The alignment implementation reports good matches, inlier ratio and mean reprojection error.

### Decision 4 — Combining SSIM and pixel difference

- **AI suggestion:** Compare corresponding component regions using structural similarity and pixel-level differences.
- **Developer decision:** Implement both SSIM and normalized mean absolute pixel difference.
- **Reason:** The two measurements provide complementary information about changes in component regions.
- **Evidence:** `src/detection.py` implements `structural_similarity()`, `cv2.absdiff()` and normalization by 255.

### Decision 5 — Introducing an UNCERTAIN classification

- **AI suggestion:** Avoid forcing every component into a binary present-or-missing decision.
- **Developer decision:** Implement three statuses: PRESENT, MISSING and UNCERTAIN.
- **Reason:** Ambiguous comparisons should be flagged for manual review instead of being treated as confident decisions.
- **Evidence:** `classify_component()` returns UNCERTAIN when neither the presence nor missing criteria are satisfied.

### Decision 6 — Adjusting classification thresholds

- **AI suggestion:** Investigate classification thresholds when aligned, complete PCB images were incorrectly classified as uncertain.
- **Developer decision:** Adjust the initial presence SSIM threshold from 0.85 to 0.60 and introduce a separate presence difference threshold of 0.12.
- **Reason:** Initial Streamlit experiments showed that known-present components had SSIM values substantially below 0.85.
- **Evidence:** Subsequent experiments correctly classified all three registered components as present in the complete synthetic test and identified U1, C1 and R1 independently in the corresponding synthetic missing-component tests.
- **Qualification:** These thresholds remain provisional and have not been calibrated on a representative real-world PCB dataset.

### Decision 7 — Using synthetic missing-component experiments

- **AI suggestion:** Create controlled test images to evaluate the missing-component detection pipeline in the absence of a labelled dataset.
- **Developer decision:** Generate synthetic missing-component examples using OpenCV inpainting.
- **Reason:** This allowed the initial detector to be tested against controlled changes to registered component regions.
- **Evidence:** Four initial scenarios were evaluated: a complete transformed PCB and separate synthetic removal of U1, C1 and R1.
- **Qualification:** Inpainting is a simulation and does not reproduce all characteristics of physically removed components.

### Decision 8 — Adding automated tests

- **AI suggestion:** Add unit tests for image-region extraction, similarity measurements and classification behavior.
- **Developer decision:** Implement pytest-based tests.
- **Reason:** Automated tests make it easier to detect regressions when the detection logic changes.
- **Evidence:** The current test suite contains eight passing tests.

### Decision 9 — Choosing Streamlit for the interface

- **AI suggestion:** Use a lightweight local interface for image uploads, annotation and result presentation.
- **Developer decision:** Build the application using Streamlit.
- **Reason:** Streamlit supports rapid development of interactive Python applications and local execution.
- **Evidence:** `app.py` implements reference upload, annotation, test-image upload and inspection result display.

## 3. Selected Chat Excerpts

The following are selected excerpts from the development conversation. They are reproduced as short excerpts, not as a complete transcript.

### Excerpt 1 — Threshold calibration

**Developer's observed issue:**

The complete transformed PCB was producing UNCERTAIN classifications even though image alignment was successful.

**AI assistant's guidance:**

> Don't simply lower the thresholds without checking the results. We need to distinguish these cases:
>
> - A component is present but looks slightly different.
> - A component is genuinely missing.
> - The image comparison is inconclusive.

**Outcome:**

The presence threshold was adjusted based on observed similarity scores. Subsequent complete-board and missing-component experiments produced the expected classifications.

### Excerpt 2 — Synthetic validation

**AI assistant's guidance:**

> If these four cases pass, we'll have a useful initial synthetic validation set.

**Developer's action:**

Tested the complete transformed PCB and generated three separate missing-component images for U1, C1 and R1.

**Outcome:**

All four initial scenarios produced the expected classifications.

### Excerpt 3 — Final verification

**AI assistant's guidance:**

> We should avoid pushing unreviewed changes, especially the detection thresholds.

**Developer's action:**

Reviewed Git changes, ran automated tests, checked Python syntax and verified Git whitespace.

**Outcome:**

Eight automated tests passed, compilation succeeded and the latest inspection interface and classifier changes were pushed to the public GitHub repository.

## 4. AI-Assisted Development Workflow

The collaboration followed an iterative workflow:

1. Understand the assignment requirements.
2. Discuss possible technical approaches.
3. Select an implementation strategy.
4. Implement individual modules.
5. Execute code and inspect errors.
6. Share terminal output and screenshots.
7. Review observed behavior.
8. Adjust implementation where justified by evidence.
9. Run automated tests.
10. Review and publish the changes.

AI assistance was used to support reasoning and debugging. Implementation and validation were performed against the local project.

## 5. Developer Responsibilities

The developer was responsible for:

- Selecting the assignment task.
- Creating and maintaining the GitHub repository.
- Setting up the Python environment.
- Implementing and integrating project modules.
- Registering PCB components.
- Running the application locally.
- Executing synthetic experiments.
- Reviewing classification outputs.
- Running automated tests.
- Reviewing and pushing code changes.
- Preparing the final submission.

## 6. Limitations of AI Assistance

AI-generated suggestions were not treated as proof of correctness.

Code and recommendations were checked through:

- Local execution.
- Inspection of source code.
- Terminal outputs.
- Streamlit application behavior.
- Synthetic test cases.
- Automated pytest results.

The initial experimental results are limited to the available PCB image and generated test cases.


## 7. Full AI Conversation History

The complete AI-assisted development conversation is available through the following ChatGPT shared conversation link:

- **Shared conversation:** https://chatgpt.com/share/6b005949-37bc-83ee-83f5-ba3ea10855e9

This conversation documents the development discussions, implementation decisions, debugging, testing, and architecture work for the PCB Inspector AI project.


## 8. Conclusion

AI assistance contributed to technical exploration, implementation planning, debugging, threshold calibration and testing.

The final project reflects an iterative development process in which suggestions were evaluated against assignment constraints and local experimental evidence.

The developer retained responsibility for the final implementation and submission.
