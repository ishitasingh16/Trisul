import os
import random
import math
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np


class SyntheticDatasetGenerator:

    def __init__(self, output_dir: str = 'dataset', width: int = 640, height: int = 480):
        self.output_dir = Path(output_dir)
        self.width = width
        self.height = height
        self.classes = {0: 'box', 1: 'cone', 2: 'person', 3: 'shelf', 4: 'pallet'}
        self.splits = ['train', 'val', 'test']
        self.split_ratios = (0.7, 0.2, 0.1)

    def setup_directories(self):
        for split in self.splits:
            (self.output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)

    def determine_split(self) -> str:
        r = random.random()
        if r < self.split_ratios[0]:
            return 'train'
        if r < self.split_ratios[0] + self.split_ratios[1]:
            return 'val'
        return 'test'

    def project_3d_box_to_2d(
        self,
        box_center: Tuple[float, float, float],
        box_extent: Tuple[float, float, float],
        cam_pos: Tuple[float, float, float],
        cam_yaw: float,
        fov_rad: float,
    ) -> Tuple[float, float, float, float]:
        dx = box_center[0] - cam_pos[0]
        dy = box_center[1] - cam_pos[1]
        dz = box_center[2] - cam_pos[2]

        rel_x = dx * math.cos(-cam_yaw) - dy * math.sin(-cam_yaw)
        rel_y = dx * math.sin(-cam_yaw) + dy * math.cos(-cam_yaw)
        rel_z = dz

        if rel_x <= 0.2:
            return 0.0, 0.0, 0.0, 0.0

        focal_x = (self.width / 2.0) / math.tan(fov_rad / 2.0)
        focal_y = focal_x

        cx_px = (self.width / 2.0) - (rel_y / rel_x) * focal_x
        cy_px = (self.height / 2.0) - (rel_z / rel_x) * focal_y

        w_px = (box_extent[1] / rel_x) * focal_x
        h_px = (box_extent[2] / rel_x) * focal_y

        norm_x = np.clip(cx_px / self.width, 0.0, 1.0)
        norm_y = np.clip(cy_px / self.height, 0.0, 1.0)
        norm_w = np.clip(w_px / self.width, 0.0, 1.0)
        norm_h = np.clip(h_px / self.height, 0.0, 1.0)

        return float(norm_x), float(norm_y), float(norm_w), float(norm_h)

    def render_synthetic_sample(self, sample_idx: int) -> Tuple[np.ndarray, List[Tuple[int, float, float, float, float]]]:
        canvas = np.full((self.height, self.width, 3), random.randint(30, 80), dtype=np.uint8)
        num_objects = random.randint(1, 5)
        labels = []

        cam_pos = (0.0, 0.0, 0.8)
        cam_yaw = 0.0
        fov = 1.04719755

        for _ in range(num_objects):
            cls_id = random.choice(list(self.classes.keys()))
            dist_x = random.uniform(1.0, 5.0)
            dist_y = random.uniform(-1.5, 1.5)
            obj_z = random.uniform(0.1, 0.5)

            obj_w = random.uniform(0.3, 0.8)
            obj_d = random.uniform(0.3, 0.8)
            obj_h = random.uniform(0.3, 1.2)

            nx, ny, nw, nh = self.project_3d_box_to_2d(
                (dist_x, dist_y, obj_z),
                (obj_d, obj_w, obj_h),
                cam_pos,
                cam_yaw,
                fov
            )

            if nw > 0.02 and nh > 0.02:
                labels.append((cls_id, nx, ny, nw, nh))
                px1 = int((nx - nw / 2.0) * self.width)
                py1 = int((ny - nh / 2.0) * self.height)
                px2 = int((nx + nw / 2.0) * self.width)
                py2 = int((ny + nh / 2.0) * self.height)
                color = (
                    random.randint(60, 240),
                    random.randint(60, 240),
                    random.randint(60, 240)
                )
                cv2.rectangle(canvas, (px1, py1), (px2, py2), color, -1)

        return canvas, labels

    def save_sample(self, split: str, idx: int, image: np.ndarray, labels: List[Tuple[int, float, float, float, float]]):
        img_name = f"sample_{idx:05d}.png"
        lbl_name = f"sample_{idx:05d}.txt"

        img_path = self.output_dir / 'images' / split / img_name
        lbl_path = self.output_dir / 'labels' / split / lbl_name

        cv2.imwrite(str(img_path), image)

        with open(lbl_path, 'w') as f:
            for cls_id, nx, ny, nw, nh in labels:
                f.write(f"{cls_id} {nx:.6f} {ny:.6f} {nw:.6f} {nh:.6f}\n")

    def run(self, count: int = 1000):
        self.setup_directories()
        for i in range(count):
            split = self.determine_split()
            img, labels = self.render_synthetic_sample(i)
            self.save_sample(split, i, img, labels)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=1000)
    parser.add_argument('--output', type=str, default='dataset')
    args = parser.parse_args()

    generator = SyntheticDatasetGenerator(output_dir=args.output)
    generator.run(count=args.count)


if __name__ == '__main__':
    main()
