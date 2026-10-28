import argparse
from pathlib import Path
from ultralytics import YOLO


class YoloTrainer:

    def __init__(
        self,
        data_yaml: str,
        base_model: str = 'yolov8n.pt',
        epochs: int = 50,
        imgsz: int = 640,
        patience: int = 20,
        device: str = 'cpu',
        project: str = 'runs/detect',
        name: str = 'navis_yolo_run',
    ):
        self.data_yaml = str(Path(data_yaml).resolve())
        self.base_model = base_model
        self.epochs = epochs
        self.imgsz = imgsz
        self.patience = patience
        self.device = device
        self.project = project
        self.name = name

    def execute(self):
        model = YOLO(self.base_model)
        results = model.train(
            data=self.data_yaml,
            epochs=self.epochs,
            imgsz=self.imgsz,
            patience=self.patience,
            device=self.device,
            project=self.project,
            name=self.name,
            verbose=True,
            save=True,
        )
        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data/data.yaml')
    parser.add_argument('--base-model', type=str, default='yolov8n.pt')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--patience', type=int, default=20)
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--project', type=str, default='runs/detect')
    parser.add_argument('--name', type=str, default='navis_yolo_run')
    args = parser.parse_args()

    trainer = YoloTrainer(
        data_yaml=args.data,
        base_model=args.base_model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        patience=args.patience,
        device=args.device,
        project=args.project,
        name=args.name,
    )
    trainer.execute()


if __name__ == '__main__':
    main()
