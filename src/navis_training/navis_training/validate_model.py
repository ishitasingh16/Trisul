import argparse
from pathlib import Path
from typing import Dict, Any
from ultralytics import YOLO


class YoloValidator:

    def __init__(self, model_path: str, data_yaml: str, imgsz: int = 640, device: str = 'cpu'):
        self.model_path = str(Path(model_path).resolve())
        self.data_yaml = str(Path(data_yaml).resolve())
        self.imgsz = imgsz
        self.device = device

    def evaluate(self) -> Dict[str, Any]:
        model = YOLO(self.model_path)
        metrics = model.val(
            data=self.data_yaml,
            imgsz=self.imgsz,
            device=self.device,
            split='val',
            verbose=True,
        )

        map50 = float(metrics.box.map50)
        map50_95 = float(metrics.box.map)
        precision = float(metrics.box.mp)
        recall = float(metrics.box.mr)

        results = {
            'mAP_0.5': map50,
            'mAP_0.5_0.95': map50_95,
            'precision': precision,
            'recall': recall,
            'target_achieved': map50 >= 0.70,
        }
        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='runs/detect/navis_yolo_run/weights/best.pt')
    parser.add_argument('--data', type=str, default='data/data.yaml')
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--device', type=str, default='cpu')
    args = parser.parse_args()

    validator = YoloValidator(
        model_path=args.model,
        data_yaml=args.data,
        imgsz=args.imgsz,
        device=args.device,
    )
    results = validator.evaluate()
    for metric, value in results.items():
        print(f"{metric}: {value}")


if __name__ == '__main__':
    main()
