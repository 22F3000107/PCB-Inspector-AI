
from src.alignment import align_test_to_reference
from src.detection import inspect_all_components


def inspect_pcb(
    reference_image,
    test_image,
    annotations,
):
    """
    Complete PCB inspection pipeline.

    1. Align test PCB to reference PCB.
    2. Stop if alignment is unreliable.
    3. Compare all annotated component regions.
    4. Return inspection results and diagnostics.
    """

    if not annotations:
        raise ValueError("No component annotations available.")

    aligned_image, alignment_diagnostics = align_test_to_reference(
        reference_image,
        test_image,
    )

    if not alignment_diagnostics["success"] or aligned_image is None:
        return {
            "success": False,
            "message": "PCB alignment failed. Inspection cannot continue.",
            "alignment": alignment_diagnostics,
            "components": [],
            "aligned_image": None,
        }

    component_results = inspect_all_components(
        reference_image,
        aligned_image,
        annotations,
    )

    missing_components = [
        item["name"]
        for item in component_results
        if item["status"] == "MISSING"
    ]

    uncertain_components = [
        item["name"]
        for item in component_results
        if item["status"] == "UNCERTAIN"
    ]

    present_components = [
        item["name"]
        for item in component_results
        if item["status"] == "PRESENT"
    ]

    if missing_components:
        message = (
            "Potential missing components detected: "
            + ", ".join(missing_components)
        )
    elif uncertain_components:
        message = (
            "Inspection requires manual review. Uncertain components: "
            + ", ".join(uncertain_components)
        )
    else:
        message = "All registered components appear present."

    return {
        "success": True,
        "message": message,
        "alignment": alignment_diagnostics,
        "components": component_results,
        "present": present_components,
        "missing": missing_components,
        "uncertain": uncertain_components,
        "aligned_image": aligned_image,
    }
