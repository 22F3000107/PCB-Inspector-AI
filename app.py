
import json
from pathlib import Path
import cv2
import numpy as np


from src.inspection import inspect_pcb

import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

from src.annotation import (
    save_annotations,
    load_annotations,
    add_annotation,
    delete_annotation,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="PCB Inspector AI",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 PCB Inspector AI")
st.caption("Reference-Based PCB Component Inspection System")


# --------------------------------------------------
# PATHS AND CONFIGURATION
# --------------------------------------------------

ANNOTATION_DIR = Path("data/annotations")
REFERENCE_DIR = Path("data/reference")

ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_PATH = REFERENCE_DIR / "reference.png"
REFERENCE_METADATA_PATH = REFERENCE_DIR / "metadata.json"

CANVAS_VERSION = "7.4.0"
MAX_DISPLAY_WIDTH = 1000


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def create_canvas_drawing(annotations, display_width, display_height):
    """Rebuild canvas rectangles from saved normalized annotations."""

    objects = []

    for annotation in annotations:
        objects.append({
            "type": "Rect",
            "version": CANVAS_VERSION,
            "originX": "left",
            "originY": "top",
            "left": annotation["x"] * display_width,
            "top": annotation["y"] * display_height,
            "width": annotation["width"] * display_width,
            "height": annotation["height"] * display_height,
            "fill": "rgba(0, 150, 255, 0.15)",
            "stroke": "#00BFFF",
            "strokeWidth": 2,
            "scaleX": 1,
            "scaleY": 1,
            "angle": 0,
            "component_name": annotation["name"],
        })

    return {
        "version": CANVAS_VERSION,
        "objects": objects,
    }


def save_current_annotations():
    """Persist the current component annotations."""

    save_annotations(st.session_state.annotations)


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "annotations" not in st.session_state:
    st.session_state.annotations = load_annotations()

if "canvas_drawing" not in st.session_state:
    st.session_state.canvas_drawing = {
        "version": CANVAS_VERSION,
        "objects": [],
    }

if "reference_image" not in st.session_state:
    if REFERENCE_PATH.exists():
        st.session_state.reference_image = Image.open(
            REFERENCE_PATH
        ).convert("RGB")
    else:
        st.session_state.reference_image = None

if "image_signature" not in st.session_state:
    if REFERENCE_METADATA_PATH.exists():
        with open(REFERENCE_METADATA_PATH, "r") as file:
            metadata = json.load(file)

        st.session_state.image_signature = (
            metadata["filename"],
            (metadata["width"], metadata["height"]),
            metadata["file_size"],
        )
    else:
        st.session_state.image_signature = None

if "canvas_restored" not in st.session_state:
    st.session_state.canvas_restored = False


# --------------------------------------------------
# 1. REFERENCE IMAGE SETUP
# --------------------------------------------------

st.header("1. Reference PCB Setup")

uploaded_file = st.file_uploader(
    "Upload a complete PCB reference image",
    type=["png", "jpg", "jpeg"],
)

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    from io import BytesIO

    image = Image.open(BytesIO(file_bytes)).convert("RGB")

    image_signature = (
        uploaded_file.name,
        image.size,
        len(file_bytes),
    )

    if image_signature != st.session_state.image_signature:

        # Save reference image
        image.save(REFERENCE_PATH, format="PNG")

        # Save reference metadata
        metadata = {
            "filename": uploaded_file.name,
            "width": image.width,
            "height": image.height,
            "file_size": len(file_bytes),
        }

        with open(REFERENCE_METADATA_PATH, "w") as file:
            json.dump(metadata, file, indent=4)

        st.session_state.reference_image = image
        st.session_state.image_signature = image_signature

        # Clear old annotations for the new reference
        st.session_state.annotations = []
        save_current_annotations()

        st.session_state.canvas_drawing = {
            "version": CANVAS_VERSION,
            "objects": [],
        }

        st.session_state.canvas_restored = True

        st.success("New reference PCB image saved successfully!")


if st.session_state.reference_image is None:
    st.info("Upload a complete PCB image to start annotating.")
    st.stop()


image = st.session_state.reference_image

st.success(
    f"Reference loaded: {image.width} × {image.height} pixels"
)


# --------------------------------------------------
# 2. COMPONENT ANNOTATION
# --------------------------------------------------

st.divider()
st.header("2. Annotate PCB Components")

st.write(
    "Draw a rectangle around each component using your mouse. "
    "Then register it with a component name."
)

display_width = min(image.width, MAX_DISPLAY_WIDTH)

display_height = int(
    image.height * display_width / image.width
)

display_image = image.resize(
    (display_width, display_height)
)


# --------------------------------------------------
# RESTORE SAVED ANNOTATIONS
# --------------------------------------------------

if not st.session_state.canvas_restored:

    st.session_state.canvas_drawing = create_canvas_drawing(
        st.session_state.annotations,
        display_width,
        display_height,
    )

    st.session_state.canvas_restored = True


canvas_col, info_col = st.columns([3, 1])

with canvas_col:

    st.subheader("PCB Annotation Canvas")

    canvas_result = st_canvas(
        fill_color="rgba(0, 150, 255, 0.15)",
        stroke_width=2,
        stroke_color="#00BFFF",
        background_image=display_image,
        update_streamlit=True,
        height=display_height,
        width=display_width,
        drawing_mode="rect",
        initial_drawing=st.session_state.canvas_drawing,
        key="pcb_annotation_canvas",
    )

    if canvas_result.json_data is not None:
        st.session_state.canvas_drawing = canvas_result.json_data


with info_col:

    st.subheader("Instructions")

    st.markdown(
        """
        1. Draw a rectangle around a component.
        2. Select its rectangle from the list.
        3. Enter its component name.
        4. Click Register Component.

        **Examples:**

        - R1: Resistor
        - C1: Capacitor
        - U1: IC
        - D1: Diode
        - L1: Inductor
        """
    )


# --------------------------------------------------
# 3. REGISTER COMPONENTS
# --------------------------------------------------

st.divider()
st.subheader("3. Register Components")

objects = (
    canvas_result.json_data.get("objects", [])
    if canvas_result.json_data
    else st.session_state.canvas_drawing.get("objects", [])
)

rectangles = [
    (index, obj)
    for index, obj in enumerate(objects)
    if str(obj.get("type", "")).lower() == "rect"
]

existing_names = {
    item["name"] for item in st.session_state.annotations
}

available_rectangles = [
    (index, obj)
    for index, obj in rectangles
    if not obj.get("component_name")
]

if available_rectangles:

    selected_index = st.selectbox(
        "Select an unassigned rectangle",
        options=[index for index, _ in available_rectangles],
        format_func=lambda index: f"Rectangle {index + 1}",
    )

    component_name = st.text_input(
        "Component name",
        placeholder="Example: R1, C1, U1",
    )

    if st.button("Register Component", type="primary"):

        name = component_name.strip().upper()

        selected_object = next(
            obj
            for index, obj in available_rectangles
            if index == selected_index
        )

        if not name:
            st.error("Please enter a component name.")

        elif name in existing_names:
            st.error("This component name already exists.")

        else:

            left = selected_object.get("left", 0)
            top = selected_object.get("top", 0)

            box_width = (
                selected_object.get("width", 0)
                * selected_object.get("scaleX", 1)
            )

            box_height = (
                selected_object.get("height", 0)
                * selected_object.get("scaleY", 1)
            )

            if box_width <= 0 or box_height <= 0:
                st.error("Please draw a valid rectangle.")

            else:

                annotation = add_annotation(
                    name,
                    left / display_width,
                    top / display_height,
                    box_width / display_width,
                    box_height / display_height,
                )

                annotation["image_width"] = image.width
                annotation["image_height"] = image.height

                st.session_state.annotations.append(annotation)

                # Store the name directly on the canvas rectangle
                selected_object["component_name"] = name

                st.session_state.canvas_drawing = canvas_result.json_data

                # Save immediately
                save_current_annotations()

                st.success(f"{name} registered and saved successfully!")

                st.rerun()

else:
    st.info("Draw a rectangle to register a component.")


# --------------------------------------------------
# 4. REGISTERED COMPONENTS
# --------------------------------------------------

st.divider()
st.subheader("4. Registered Components")

annotations = st.session_state.annotations

if annotations:

    st.dataframe(
        annotations,
        use_container_width=True,
    )

    st.success(f"{len(annotations)} component(s) registered.")

    if st.button("Save All Annotations"):
        save_current_annotations()
        st.success("All annotations saved successfully.")

    selected_delete = st.selectbox(
        "Component to delete",
        options=["Select"] + [
            item["name"] for item in annotations
        ],
        key="delete_component",
    )

    if st.button("Delete Selected Component"):

        if selected_delete == "Select":
            st.warning("Please select a component to delete.")

        else:

            st.session_state.annotations = delete_annotation(
                st.session_state.annotations,
                selected_delete,
            )

            # Rebuild canvas without the deleted component
            st.session_state.canvas_drawing = create_canvas_drawing(
                st.session_state.annotations,
                display_width,
                display_height,
            )

            # Persist deletion immediately
            save_current_annotations()

            st.success(f"{selected_delete} deleted successfully!")

            st.rerun()

else:
    st.warning("No components have been registered yet.")


# --------------------------------------------------
# 5. PCB INSPECTION
# --------------------------------------------------

st.divider()
st.header("5. Inspect Test PCB Images")

st.write(
    "Upload up to three photographs of the same PCB. "
    "The system will align each image with the reference and "
    "check the registered component locations."
)

if not st.session_state.annotations:
    st.warning(
        "Register at least one component before starting inspection."
    )

else:

    test_files = st.file_uploader(
        "Upload test PCB images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="test_pcb_uploader",
        help="Upload up to three images of the same PCB.",
    )

    if len(test_files) > 3:
        st.error("Please upload no more than three test images.")

    elif test_files:

        # Convert the stored reference image from RGB to OpenCV BGR.
        reference_bgr = cv2.cvtColor(
            np.array(st.session_state.reference_image),
            cv2.COLOR_RGB2BGR,
        )

        st.subheader("Inspection Results")

        for image_index, uploaded_test in enumerate(test_files):

            with st.expander(
                f"Test {image_index + 1}: {uploaded_test.name}",
                expanded=True,
            ):

                try:
                    file_bytes = uploaded_test.getvalue()

                    test_array = np.frombuffer(
                        file_bytes,
                        dtype=np.uint8,
                    )

                    test_bgr = cv2.imdecode(
                        test_array,
                        cv2.IMREAD_COLOR,
                    )

                    if test_bgr is None:
                        st.error("Could not read this image.")
                        continue

                    # Run alignment and component inspection.
                    result = inspect_pcb(
                        reference_bgr,
                        test_bgr,
                        st.session_state.annotations,
                    )

                    if not result["success"]:
                        st.error(result["message"])

                        st.write("Alignment diagnostics:")
                        st.json(result["alignment"])

                        continue

                    alignment = result["alignment"]

                    # Display alignment quality.
                    st.markdown("**Alignment Quality**")

                    metric_col1, metric_col2, metric_col3 = st.columns(3)

                    metric_col1.metric(
                        "Good matches",
                        alignment["good_matches"],
                    )

                    metric_col2.metric(
                        "Inlier ratio",
                        f"{alignment['inlier_ratio']:.1%}",
                    )

                    metric_col3.metric(
                        "Reprojection error",
                        f"{alignment['mean_reprojection_error']:.2f} px",
                    )

                    # Display overall inspection status.
                    missing = result["missing"]
                    uncertain = result["uncertain"]
                    present = result["present"]

                    if missing:
                        st.error(
                            "Potential missing components: "
                            + ", ".join(missing)
                        )

                    elif uncertain:
                        st.warning(
                            "Manual review required for: "
                            + ", ".join(uncertain)
                        )

                    else:
                        st.success(
                            "OK — All registered components appear present."
                        )

                    # Component-level results.
                    st.markdown("**Component Inspection Details**")

                    result_rows = []

                    for component in result["components"]:
                        result_rows.append({
                            "Component": component["name"],
                            "Status": component["status"],
                            "SSIM": component["ssim"],
                            "Difference": component["difference"],
                        })

                    st.dataframe(
                        result_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Draw result boxes on the aligned image.
                    annotated_image = result["aligned_image"].copy()

                    image_height, image_width = annotated_image.shape[:2]

                    for annotation in st.session_state.annotations:

                        component_result = next(
                            item
                            for item in result["components"]
                            if item["name"] == annotation["name"]
                        )

                        status = component_result["status"]

                        # OpenCV colors are BGR.
                        if status == "MISSING":
                            box_color = (0, 0, 255)
                        elif status == "UNCERTAIN":
                            box_color = (0, 165, 255)
                        else:
                            box_color = (0, 200, 0)

                        x1 = int(annotation["x"] * image_width)
                        y1 = int(annotation["y"] * image_height)

                        x2 = int(
                            (annotation["x"] + annotation["width"])
                            * image_width
                        )

                        y2 = int(
                            (annotation["y"] + annotation["height"])
                            * image_height
                        )

                        cv2.rectangle(
                            annotated_image,
                            (x1, y1),
                            (x2, y2),
                            box_color,
                            3,
                        )

                        label = f"{annotation['name']}: {status}"

                        cv2.putText(
                            annotated_image,
                            label,
                            (x1, max(25, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.65,
                            box_color,
                            2,
                            cv2.LINE_AA,
                        )

                    annotated_rgb = cv2.cvtColor(
                        annotated_image,
                        cv2.COLOR_BGR2RGB,
                    )

                    st.markdown("**Visual Inspection Result**")

                    st.image(
                        annotated_rgb,
                        caption="Green: Present | Red: Missing | Orange: Uncertain",
                        use_container_width=True,
                    )

                except Exception as error:
                    st.error(
                        f"Inspection failed for {uploaded_test.name}: {error}"
                    )
