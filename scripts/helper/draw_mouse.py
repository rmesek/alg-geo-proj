import matplotlib.pyplot as plt


def draw_polygon_by_clicking() -> list[tuple[float, float]]:
    plt.ion()
    plt.figure()
    plt.title("Wprowadź wielokąt")
    plt.xlabel("X")
    plt.ylabel("Y")

    polygon: list[tuple[float, float]] = plt.ginput(n=-1, timeout=0, show_clicks=True)  # type: ignore

    plt.close()
    plt.ioff()

    return polygon


if __name__ == "__main__":
    print(draw_polygon_by_clicking())
