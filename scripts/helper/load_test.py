from pathlib import Path
from scripts.helper.draw_mouse import draw_polygon_by_clicking

TESTS_PATH = Path(__file__).parent.parent.parent.absolute() / "data" / "tests"

def load_polygon(name: str) -> list[tuple[float, float]]:
    test_path = TESTS_PATH / fr"{name}.txt"
    lines = []
    polygon = []
    with open(test_path, mode="r") as f:
        for line in f.readlines():
            lines.append(line.strip().split())
    for line in lines:
        if line:
            x, y = float(line[0]), float(line[1])
            polygon.append((x, y))
    return polygon

def save_polygon() -> None:
    polygon = draw_polygon_by_clicking()
    name = input("Input <name>.txt (c - cancel): ").strip()
    if name.lower()[0] == "c":
        print("Canceled!")
        return
    test_path = TESTS_PATH / fr"{name}.txt"
    lines = []
    for x, y in polygon:
        lines.append(f"{str(x)} {str(y)}\n")
    with open(test_path, mode="w") as f:
        f.writelines(lines)

if __name__=="__main__":
    # name = input("Input <name>.txt: ").strip()
    save_polygon()