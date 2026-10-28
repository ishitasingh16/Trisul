import argparse
import shutil
from pathlib import Path
from ultralytics import YOLO


class ModelExporter:

    def __init__(self, weights_path: str, destination_dir: str, export_onnx: bool = True):
        self.weights_path = Path(weights_path).resolve()
        self.destination_dir = Path(destination_dir).resolve()
        self.export_onnx = export_onnx

    def export(self) -> Path:
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        dest_pt = self.destination_dir / 'navis_yolov8n.pt'
        shutil.copyfile(self.weights_path, dest_pt)

        if self.export_onnx:
            model = YOLO(str(dest_pt))
            model.export(format='onnx', imgsz=640, dynamic=False)

        return dest_pt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='runs/detect/navis_yolo_run/weights/best.pt')
    parser.add_argument('--dest', type=str, default='../navis_perception/models')
    parser.add_argument('--onnx', action='store_true', default=True)
    args = parser.parse_args()

    exporter = ModelExporter(
        weights_path=args.weights,
        destination_dir=args.dest,
        export_onnx=args.onnx,
    )
    target = exporter.export()
    print(f"Exported model to: {target}")


if __name__ == '__main__':
    main()
