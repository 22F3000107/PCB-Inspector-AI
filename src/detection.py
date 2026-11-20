
import cv2
import numpy as np

from skimage.metrics import structural_similarity

from src.preprocessing import validate_image


def extract_component_region(image, annotation, padding=0.10):
    """
    Extract a component's annotated region.

    Annotation coordinates are normalized between 0 and 1.
    Padding expands the crop slightly around the component.
    """

    validate_image(image)

    image_height, image_width = image.shape[:2]

    x = float(annotation["x"]) * image_width
    y = float(annotation["y"]) * image_height
    width = float(annotation["width"]) * image_width
    height = float(annotation["height"]) * image_height

    pad_x = width * padding
    pad_y = height * padding

    x1 = max(0, int(round(x - pad_x)))
    y1 = max(0, int(round(y - pad_y)))
    x2 = min(image_width, int(round(x + width + pad_x)))
    y2 = min(image_height, int(round(y + height + pad_y)))

    if x2 <= x1 or y2 <= y1:
        raise ValueError(
            f"Invalid component region: {annotation.get('name', 'Unknown')}"
        )

    return image[y1:y2, x1:x2].copy()


def calculate_region_similarity(reference_region, test_region):
    """
    Calculate structural similarity and normalized pixel difference.

    Returns:
        ssim_score: Structural similarity, between -1 and 1.
        difference_score: Mean absolute pixel difference, normalized 0-1.
    """

    if reference_region is None or test_region is None:
        raise ValueError("Both image regions are required.")

    if reference_region.size == 0 or test_region.size == 0:
        raise ValueError("Image region is empty.")

    if reference_region.shape != test_region.shape:
        test_region = cv2.resize(
            test_region,
            (reference_region.shape[1], reference_region.shape[0]),
            interpolation=cv2.INTER_AREA,
        )

    reference_gray = cv2.cvtColor(
        reference_region,
        cv2.COLOR_BGR2GRAY,
    )

    test_gray = cv2.cvtColor(
        test_region,
        cv2.COLOR_BGR2GRAY,
    )

    # SSIM measures structural similarity.
    min_dimension = min(reference_gray.shape)

    if min_dimension < 3:
        raise ValueError("Component region is too small for SSIM.")

    win_size = min(7, min_dimension)

    if win_size % 2 == 0:
        win_size -= 1

    ssim_score = structural_similarity(
        reference_gray,
        test_gray,
        data_range=255,
        win_size=win_size,
    )

    # Mean absolute pixel difference.
    difference = cv2.absdiff(
        reference_gray,
        test_gray,
    )

    difference_score = float(np.mean(difference) / 255.0)

    return float(ssim_score), difference_score



def classify_component(
    ssim_score,
    difference_score,
    present_ssim_threshold=0.60,
    present_difference_threshold=0.12,
    missing_ssim_threshold=0.45,
    missing_difference_threshold=0.10,
):
    """
    Provisional classification thresholds based on initial
    synthetic PCB inspection experiments.

    These values require further validation on representative
    real-world PCB images.
    """

    # Component appears present
    if (
        ssim_score >= present_ssim_threshold
        and difference_score < present_difference_threshold
    ):
        return "PRESENT"

    # Component appears missing
    if (
        ssim_score < missing_ssim_threshold
        and difference_score >= missing_difference_threshold
    ):
        return "MISSING"

    # Insufficient evidence for a confident decision
    return "UNCERTAIN"



def inspect_component_region(
    reference_image,
    aligned_test_image,
    annotation,
    padding=0.10,
):
    """
    Compare one annotated component between reference and aligned test.
    """

    reference_region = extract_component_region(
        reference_image,
        annotation,
        padding=padding,
    )

    test_region = extract_component_region(
        aligned_test_image,
        annotation,
        padding=padding,
    )

    ssim_score, difference_score = calculate_region_similarity(
        reference_region,
        test_region,
    )

    status = classify_component(
        ssim_score,
        difference_score,
    )

    return {
        "name": annotation["name"],
        "status": status,
        "ssim": round(ssim_score, 4),
        "difference": round(difference_score, 4),
        "reference_region": reference_region,
        "test_region": test_region,
    }


def inspect_all_components(
    reference_image,
    aligned_test_image,
    annotations,
    padding=0.10,
):
    """
    Inspect all registered PCB components.

    Returns a list of component-level results.
    """

    if not annotations:
        raise ValueError("No component annotations were provided.")

    if reference_image.shape[:2] != aligned_test_image.shape[:2]:
        raise ValueError(
            "Reference and aligned test images must have identical dimensions."
        )

    results = []

    for annotation in annotations:

        result = inspect_component_region(
            reference_image,
            aligned_test_image,
            annotation,
            padding=padding,
        )

        # Keep image crops out of the summary result.
        results.append({
            "name": result["name"],
            "status": result["status"],
            "ssim": result["ssim"],
            "difference": result["difference"],
        })

    return results
