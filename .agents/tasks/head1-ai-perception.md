# Head 1 — AI & Perception 🧠

**Codename:** Brain
**Member:** (Assign name here)

---

## Department Ownership

You own these packages. Only you (or someone you authorize) should modify them:

| Package | Purpose |
|---------|---------|
| `navis_perception/` | YOLO detector node, image processing, depth estimation |
| `navis_world_model/` | Semantic world model, object tracker, semantic layer |
| `navis_training/` | Offline dataset generation, YOLO training, validation, model export |

---

## Task List — By Phase

### Phase 4 — AI Perception

- [ ] Create `navis_perception` ROS 2 Python package (ament_python)
- [ ] Implement `yolo_detector_node.py`
  - Subscribe to `/camera/image_raw`
  - Run YOLOv8n inference (start with pre-trained COCO weights)
  - Publish `navis_msgs/DetectionArray` on `/detections`
  - Publish annotated image on `/detections/image`
- [ ] Implement `image_processor.py` — OpenCV utilities (resize, color conversion, preprocessing)
- [ ] Create `perception_params.yaml` config (model_path, confidence_threshold, device)
- [ ] Create `perception.launch.py`
- [ ] Test: YOLO detects at least 1 object in Webots camera feed
- [ ] Measure inference latency — target < 50ms (GPU) or < 200ms (CPU)

### Phase 5 — Sensor Fusion & Depth Estimation

- [ ] Implement `depth_estimator.py`
  - Map YOLO bounding box center to LiDAR angular range
  - Estimate object distance from corresponding LiDAR beams
  - Convert (angle, distance) → (x, y) in robot frame
  - Transform to map frame using TF2
- [ ] Coordinate with Head 2 to verify:
  - Camera FOV matches Webots sensor config
  - LiDAR topic `/scan` format and angular range
  - TF frames: `camera_link`, `lidar_link`, `base_link`
- [ ] Test: Estimated object position within ±0.5m of Webots ground truth

### Phase 6 — Semantic World Model

- [ ] Create `navis_world_model` ROS 2 Python package
- [ ] Implement `world_model_node.py`
  - Subscribe to `/detections`, `/scan`, `/tf`, `/map`, `/amcl_pose`
  - Maintain list of tracked WorldObjects (id, class, position, confidence, timestamp)
  - Object association: match new detections to existing objects within 0.5m
  - Prune stale objects (not seen for 30s)
  - Publish `/world_model/objects`
  - Publish `/world_model/status` (mission state)
- [ ] Implement `semantic_layer.py` — overlay detected objects onto occupancy grid
- [ ] Implement `object_tracker.py` — temporal filtering, moving average positions
- [ ] Create `world_model.launch.py`
- [ ] Test: Object appears in world model within 2s of first detection
- [ ] Test: Object is correctly pruned after leaving sensor view for 30s

### Phase 8 — Offline Training Pipeline

- [ ] Write `generate_dataset.py` — Webots Supervisor script
  - Randomize object positions, lighting
  - Capture camera images as PNG
  - Compute YOLO-format labels from 3D → 2D projection
  - Generate 1000–5000 images
- [ ] Define object classes: box (0), cone (1), person (2), shelf (3), pallet (4)
- [ ] Create `data.yaml` for Ultralytics training config
- [ ] Write `train_yolo.py` — training script
  - Base model: `yolov8n.pt`
  - Epochs: 50–100, imgsz: 640, patience: 20
- [ ] Write `validate_model.py` — evaluate mAP@0.5, precision, recall
- [ ] Write `export_model.py` — copy best.pt to `navis_perception/models/`
- [ ] Target: mAP@0.5 > 0.7 on validation set
- [ ] Document training results (curves, metrics) for demo

---

## Dependencies on Other Heads

| You Need | From | Status |
|----------|------|--------|
| Camera topic `/camera/image_raw` publishing | Head 2 | ⬜ Pending |
| LiDAR topic `/scan` publishing | Head 2 | ⬜ Pending |
| TF tree correct (`camera_link`, `lidar_link`) | Head 2 | ⬜ Pending |
| `navis_msgs/Detection.msg` and `DetectionArray.msg` built | Head 3 | ⬜ Pending |
| Webots world with objects for dataset collection | Head 2 | ⬜ Pending |

---

## Key Rules for Head 1

1. **Start with pre-trained YOLOv8n (COCO).** Don't wait for custom training to validate perception.
2. **Don't modify Webots worlds or Nav2 config.** Flag needs to Head 2.
3. **Don't modify message definitions unilaterally.** Coordinate with Head 3.
4. **Log inference time in every detection message** — judges will ask about latency.
5. **The World Model is your crown jewel.** This is what makes NAVIS more than just Nav2.
