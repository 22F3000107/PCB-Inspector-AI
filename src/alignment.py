
import cv2
import numpy as np

from src.preprocessing import preprocess_for_alignment, validate_image


def align_test_to_reference(
    reference_image,
    test_image,
    max_features=5000,
    ratio_threshold=0.75,
    min_matches=20,
    min_inliers=12,
    min_inlier_ratio=0.35,
    reprojection_threshold=5.0,
):
    """
    Align a test PCB image to a reference PCB image.

    Uses:
        1. ORB feature detection
        2. BFMatcher with Hamming distance
        3. Lowe's ratio test
        4. RANSAC homography estimation
        5. Perspective warping

    Both input images must be NumPy arrays in BGR format.

    Returns:
        aligned_image: aligned BGR image, or None on failure
        diagnostics: dictionary containing alignment metrics
    """

    diagnostics = {
        "success": False,
        "reason": "",
        "keypoints_reference": 0,
        "keypoints_test": 0,
        "good_matches": 0,
        "inliers": 0,
        "inlier_ratio": 0.0,
        "mean_reprojection_error": None,
    }

    try:
        validate_image(reference_image)
        validate_image(test_image)

        reference_height, reference_width = reference_image.shape[:2]

        # Preprocess both images
        reference_gray = preprocess_for_alignment(reference_image)
        test_gray = preprocess_for_alignment(test_image)

        # ORB feature detector
        orb = cv2.ORB_create(
            nfeatures=max_features,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=15,
            fastThreshold=10,
        )

        kp_reference, des_reference = orb.detectAndCompute(
            reference_gray,
            None,
        )

        kp_test, des_test = orb.detectAndCompute(
            test_gray,
            None,
        )

        diagnostics["keypoints_reference"] = len(kp_reference)
        diagnostics["keypoints_test"] = len(kp_test)

        if des_reference is None or des_test is None:
            diagnostics["reason"] = (
                "Could not detect enough visual features."
            )
            return None, diagnostics

        # Match descriptors using Hamming distance
        matcher = cv2.BFMatcher(
            cv2.NORM_HAMMING,
            crossCheck=False,
        )

        matches = matcher.knnMatch(
            des_test,
            des_reference,
            k=2,
        )

        # Lowe's ratio test
        good_matches = []

        for pair in matches:
            if len(pair) < 2:
                continue

            first, second = pair

            if first.distance < ratio_threshold * second.distance:
                good_matches.append(first)

        diagnostics["good_matches"] = len(good_matches)

        if len(good_matches) < min_matches:
            diagnostics["reason"] = (
                f"Insufficient feature matches: "
                f"{len(good_matches)} found, "
                f"{min_matches} required."
            )
            return None, diagnostics

        # Coordinates: test image -> reference image
        source_points = np.float32([
            kp_test[m.queryIdx].pt
            for m in good_matches
        ]).reshape(-1, 1, 2)

        destination_points = np.float32([
            kp_reference[m.trainIdx].pt
            for m in good_matches
        ]).reshape(-1, 1, 2)

        # Estimate homography using RANSAC
        homography, mask = cv2.findHomography(
            source_points,
            destination_points,
            cv2.RANSAC,
            reprojection_threshold,
        )

        if homography is None or mask is None:
            diagnostics["reason"] = (
                "Homography estimation failed."
            )
            return None, diagnostics

        if not np.isfinite(homography).all():
            diagnostics["reason"] = (
                "Homography contains invalid values."
            )
            return None, diagnostics

        inlier_mask = mask.ravel().astype(bool)
        inlier_count = int(np.sum(inlier_mask))

        inlier_ratio = inlier_count / len(good_matches)

        diagnostics["inliers"] = inlier_count
        diagnostics["inlier_ratio"] = float(inlier_ratio)

        if inlier_count < min_inliers:
            diagnostics["reason"] = (
                f"Insufficient RANSAC inliers: "
                f"{inlier_count} found, "
                f"{min_inliers} required."
            )
            return None, diagnostics

        if inlier_ratio < min_inlier_ratio:
            diagnostics["reason"] = (
                f"Low inlier ratio: {inlier_ratio:.2f}."
            )
            return None, diagnostics

        # Measure average reprojection error on inliers
        projected_points = cv2.perspectiveTransform(
            source_points,
            homography,
        )

        errors = np.linalg.norm(
            projected_points[inlier_mask].reshape(-1, 2)
            - destination_points[inlier_mask].reshape(-1, 2),
            axis=1,
        )

        mean_error = float(np.mean(errors))

        diagnostics["mean_reprojection_error"] = mean_error

        if not np.isfinite(mean_error) or mean_error > reprojection_threshold:
            diagnostics["reason"] = (
                "Alignment reprojection error is too high."
            )
            return None, diagnostics

        # Warp test image into reference image dimensions
        aligned_image = cv2.warpPerspective(
            test_image,
            homography,
            (reference_width, reference_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

        diagnostics["success"] = True
        diagnostics["reason"] = "Alignment successful."

        return aligned_image, diagnostics

    except (TypeError, ValueError, cv2.error) as error:
        diagnostics["reason"] = str(error)
        return None, diagnostics
