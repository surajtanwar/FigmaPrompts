import json

INPUT_FILE = "figma_design_data.json"
OUTPUT_FILE = "relative_node_coordinates.json"

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920


def get_box(node):
    return node.get("absoluteBoundingBox")


def round_box_value(value):
    return int(round(value))


def extract_nodes_from_frame(node, frame, hierarchy, results):
    frame_box = get_box(frame)
    node_box = get_box(node)

    if node_box and node.get("id") != frame.get("id"):
        relative_x = node_box["x"] - frame_box["x"]
        relative_y = node_box["y"] - frame_box["y"]
        width = node_box["width"]
        height = node_box["height"]

        results.append({
            "frame_name": frame.get("name"),
            "frame_id": frame.get("id"),
            "node_name": node.get("name"),
            "node_id": node.get("id"),
            "node_type": node.get("type"),
            "hierarchy": hierarchy,
            "relative_position": {
                "x": round_box_value(relative_x),
                "y": round_box_value(relative_y)
            },
            "center_position": {
                "x": round_box_value(relative_x + width / 2),
                "y": round_box_value(relative_y + height / 2)
            },
            "size": {
                "width": round_box_value(width),
                "height": round_box_value(height)
            }
        })

    for child in node.get("children", []):
        extract_nodes_from_frame(
            child,
            frame,
            hierarchy + [child.get("name", "")],
            results
        )


def find_frames(node, frames):
    if node.get("type") == "FRAME":
        box = get_box(node)
        if box:
            width = round_box_value(box.get("width", 0))
            height = round_box_value(box.get("height", 0))

            if width == SCREEN_WIDTH and height in [SCREEN_HEIGHT, SCREEN_HEIGHT + 1]:
                frames.append(node)

    for child in node.get("children", []):
        find_frames(child, frames)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        figma_data = json.load(file)

    document = figma_data.get("document", {})

    frames = []
    find_frames(document, frames)

    output = []

    for frame in frames:
        extract_nodes_from_frame(
            node=frame,
            frame=frame,
            hierarchy=[frame.get("name", "")],
            results=output
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"Done. Extracted {len(output)} nodes.")
    print(f"Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()