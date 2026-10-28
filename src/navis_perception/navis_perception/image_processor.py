import cv2
import numpy as np


class ImageProcessor:

    def __init__(self):
        self.box_color = (246, 92, 139)
        self.text_color = (255, 255, 255)
        self.bg_color = (23, 14, 10)

    def preprocess(self, frame: np.ndarray, target_size: int) -> np.ndarray:
        h, w = frame.shape[:2]
        if h == target_size and w == target_size:
            return frame
        scale = min(target_size / h, target_size / w)
        nh, nw = int(h * scale), int(w * scale)
        resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((target_size, target_size, 3), 114, dtype=np.uint8)
        top = (target_size - nh) // 2
        left = (target_size - nw) // 2
        canvas[top : top + nh, left : left + nw] = resized
        return canvas

    def annotate(self, frame: np.ndarray, detections: list) -> np.ndarray:
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.box_color, 2)
            label = f"{det.class_name} {det.confidence:.2f}"
            (text_w, text_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            y_label = max(y1, text_h + 4)
            cv2.rectangle(
                frame,
                (x1, y_label - text_h - 4),
                (x1 + text_w + 4, y_label + baseline),
                self.bg_color,
                -1,
            )
            cv2.putText(
                frame,
                label,
                (x1 + 2, y_label - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.text_color,
                1,
                cv2.LINE_AA,
            )
        return frame
