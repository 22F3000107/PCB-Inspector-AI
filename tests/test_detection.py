
import numpy as np
import pytest

from src.detection import (
    extract_component_region,
    calculate_region_similarity,
    classify_component,
    inspect_all_components,
)


@pytest.fixture
def sample_image():
    """Create a deterministic sample PCB-like image."""
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    image[40:100, 50:110] = (180, 180, 180)
    image[50:90, 60:100] = (80, 80, 80)

    return image


@pytest.fixture
def sample_annotation():
    return {
        "name": "U1",
        "x": 0.25,
        "y": 0.20,
        "width": 0.30,
        "height": 0.30,
    }


def test_extract_component_region(sample_image, sample_annotation):
    region = extract_component_region(
        sample_image,
        sample_annotation,
        padding=0,
    )

    assert region.shape[:2] == (60, 60)
    assert region.size > 0


def test_identical_regions_have_high_similarity(sample_image):
    ssim, difference = calculate_region_similarity(
        sample_image,
        sample_image.copy(),
    )

    assert ssim == pytest.approx(1.0)
    assert difference == pytest.approx(0.0)


def test_different_regions_have_lower_similarity(sample_image):
    modified = np.full_like(sample_image, 255)

    ssim, difference = calculate_region_similarity(
        sample_image,
        modified,
    )

    assert ssim < 0.45
    assert difference > 0.10


@pytest.mark.parametrize(
    "ssim,difference,expected",
    [
        (0.95, 0.03, "PRESENT"),
        (0.20, 0.45, "MISSING"),
        (0.65, 0.12, "UNCERTAIN"),
    ],
)
def test_component_classification(ssim, difference, expected):
    result = classify_component(ssim, difference)

    assert result == expected


def test_inspect_identical_component_regions(
    sample_image,
    sample_annotation,
):
    results = inspect_all_components(
        sample_image,
        sample_image.copy(),
        [sample_annotation],
    )

    assert len(results) == 1
    assert results[0]["name"] == "U1"
    assert results[0]["status"] == "PRESENT"


def test_empty_annotations_raise_error(sample_image):
    with pytest.raises(ValueError):
        inspect_all_components(
            sample_image,
            sample_image.copy(),
            [],
        )
