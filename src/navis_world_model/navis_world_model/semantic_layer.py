import math
from typing import List
import numpy as np
from navis_world_model.object_tracker import TrackedWorldObject


class SemanticLayer:

    def __init__(self, obstacle_inflation_radius: float = 0.3, cost_value: int = 100):
        self.inflation_radius = obstacle_inflation_radius
        self.cost_value = cost_value

    def overlay(
        self,
        grid: np.ndarray,
        objects: List[TrackedWorldObject],
        resolution: float,
        origin_x: float,
        origin_y: float,
    ) -> np.ndarray:
        if grid.size == 0 or resolution <= 0.0 or not objects:
            return grid

        height, width = grid.shape
        radius_cells = int(math.ceil(self.inflation_radius / resolution))
        y_indices, x_indices = np.ogrid[-radius_cells:radius_cells + 1, -radius_cells:radius_cells + 1]
        mask = (x_indices * x_indices + y_indices * y_indices) <= (radius_cells * radius_cells)

        for obj in objects:
            gx = int((obj.x - origin_x) / resolution)
            gy = int((obj.y - origin_y) / resolution)

            if 0 <= gx < width and 0 <= gy < height:
                x_min = max(0, gx - radius_cells)
                x_max = min(width, gx + radius_cells + 1)
                y_min = max(0, gy - radius_cells)
                y_max = min(height, gy + radius_cells + 1)

                mask_x_min = x_min - (gx - radius_cells)
                mask_x_max = mask_x_min + (x_max - x_min)
                mask_y_min = y_min - (gy - radius_cells)
                mask_y_max = mask_y_min + (y_max - y_min)

                sub_mask = mask[mask_y_min:mask_y_max, mask_x_min:mask_x_max]
                region = grid[y_min:y_max, x_min:x_max]
                region[sub_mask] = np.maximum(region[sub_mask], self.cost_value)

        return grid
