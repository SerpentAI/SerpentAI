import numpy as np


def generate_rays(player_to_center_angle, mode="UNIFORM", quantity=12, starting_angle=30):
    rays = {"Ray Player": player_to_center_angle}

    clockwise = True
    current_angle = starting_angle
    current_angle_count = 0

    if mode == "UNIFORM":
        while len(rays) < quantity:
            ray_label = f"Ray Player {'-' if clockwise else '+'} {str(current_angle)}"

            if clockwise:
                rays[ray_label] = (player_to_center_angle - current_angle + 179) % 360 - 179
            else:
                rays[ray_label] = (player_to_center_angle + current_angle + 179) % 360 - 179

            current_angle_count += 1
            clockwise = not clockwise

            if current_angle_count == 2:
                current_angle_count = 0
                current_angle += starting_angle

    return rays


def calculate_minimum_collision_distances(rays, thresholded_frame, angle_mapping_array, distance_mapping_array):
    ray_collision_distances = dict()

    for label, angle in rays.items():
        ray_collision_mask = (
            (angle_mapping_array == angle) &
            (thresholded_frame == 1)
        )

        collision_distances = distance_mapping_array[ray_collision_mask == True]

        ray_collision_distances[label] = np.min(collision_distances) if collision_distances.size else 9999

    return ray_collision_distances
