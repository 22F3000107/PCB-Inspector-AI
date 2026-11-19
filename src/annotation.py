
import json
from pathlib import Path

ANNOTATION_DIR = Path("data/annotations")
ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)


def save_annotations(annotations, filename="reference_annotations.json"):
    path = ANNOTATION_DIR / filename

    with open(path, "w") as file:
        json.dump(annotations, file, indent=4)

    return path


def load_annotations(filename="reference_annotations.json"):
    path = ANNOTATION_DIR / filename

    if not path.exists():
        return []

    with open(path, "r") as file:
        return json.load(file)


def add_annotation(name, x, y, width, height):
    return {
        "name": name,
        "x": float(x),
        "y": float(y),
        "width": float(width),
        "height": float(height)
    }


def delete_annotation(annotations, component_name):
    return [
        item for item in annotations
        if item["name"] != component_name
    ]
