import numpy as np


def meshgrid_around_center_for_shape(shape):
    # Y
    if shape[0] % 2 == 0:
        half_y = shape[0] // 2
        y_offset = np.arange(-half_y + 1, half_y, 1)
        y = np.r_[y_offset[:half_y], [0], y_offset[half_y:]]
    else:
        y = np.arange(-(shape[0] // 2), shape[0] // 2 + 1, 1)
    # X
    if shape[1] % 2 == 0:
        half_x = shape[1] // 2
        x_offset = np.arange(-half_x + 1, half_x, 1)
        x = np.r_[x_offset[:half_x], [0], x_offset[half_x:]]
    else:
        x = np.arange(-(shape[1] // 2), shape[1] // 2 + 1, 1)

    return np.meshgrid(x, y)


def distances_to_center(shape):
    x, y = meshgrid_around_center_for_shape(shape)
    points = np.array([y, x])

    return np.linalg.norm(points, axis=0)


def angles_to_center(shape):
    x, y = meshgrid_around_center_for_shape(shape)
    return np.rad2deg(np.arctan2(x, y)).astype("int16")
