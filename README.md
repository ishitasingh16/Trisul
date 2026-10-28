<p align="center">
  <strong>🔱 NAVIS — Navigational Autonomous Vehicle with Intelligent Sensing</strong>
</p>

<p align="center">
  <em>An AI-powered autonomous warehouse robot built on ROS 2 Humble + Webots + YOLOv8</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/ROS_2-Humble-blue?logo=ros&logoColor=white" alt="ROS 2 Humble" />
  <img src="https://img.shields.io/badge/Simulator-Webots-green?logo=webots&logoColor=white" alt="Webots" />
  <img src="https://img.shields.io/badge/AI-YOLOv8-purple?logo=pytorch&logoColor=white" alt="YOLOv8" />
  <img src="https://img.shields.io/badge/Nav-Nav2-orange?logo=ros&logoColor=white" alt="Nav2" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License" />
</p>

---

## Overview

**NAVIS** (codename **Trishul** 🔱) is a fully autonomous warehouse navigation robot that combines:

- **Real-time AI perception** — YOLOv8 object detection fused with LiDAR depth estimation
- **Semantic world understanding** — tracked objects, dynamic obstacle awareness, mission state machine
- **Autonomous navigation** — SLAM, AMCL localization, Nav2 path planning with dynamic replanning
- **Live web dashboard** — browser-based mission control with real-time sensor visualization

The robot operates inside a Webots simulation of a warehouse environment, navigating between zones while detecting and avoiding both static and dynamic obstacles.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        NAVIS System Architecture                   │
├──────────────────┬──────────────────────┬──────────────────────────┤
│   Head 1 (Brain) │   Head 2 (Body)      │   Head 3 (Interface)     │
│   AI & Perception│   Robotics & Sim     │   Platform & Integration │
├──────────────────┼──────────────────────┼──────────────────────────┤
│ navis_perception │ navis_description    │ navis_bringup            │
│ navis_world_model│ navis_navigation     │ navis_dashboard          │
│ navis_training   │ navis_control        │ navis_msgs               │
│                  │                      │ navis_interfaces         │
└──────────────────┴──────────────────────┴──────────────────────────┘
```

### Data Flow

```
Camera ──► YOLO Detector ──► DetectionArray ──► World Model ──► Dashboard
                                                    │
LiDAR  ──► Depth Estimator ──► 3D Positions ───────┘
                                                    │
LiDAR  ──► Nav2 Costmap ◄── Semantic Layer ◄────────┘
                │
Odometry ──► AMCL ──► TF ──► Nav2 Planner ──► cmd_vel ──► Robot
```

---

## Packages

### Head 1 — AI & Perception

| Package | Description |
|---------|-------------|
| [`navis_perception`](src/navis_perception/) | YOLOv8 detector node, image preprocessing, depth estimation via LiDAR fusion |
| [`navis_world_model`](src/navis_world_model/) | Semantic world model — object tracking, association, pruning, and semantic costmap layer |
| [`navis_training`](src/navis_training/) | Offline dataset generation from Webots, YOLO training, validation, and model export |

### Head 2 — Robotics & Simulation

| Package | Description |
|---------|-------------|
| [`navis_description`](navis_description/) | Robot URDF, Webots PROTO models, sensor configs, warehouse world files |
| [`navis_navigation`](navis_navigation/) | SLAM Toolbox config, Nav2 params, AMCL localization, maps, launch files |
| [`navis_control`](navis_control/) | PID motion controller node for differential-drive velocity control |

### Head 3 — Platform & Integration

| Package | Description |
|---------|-------------|
| [`navis_bringup`](src/navis_bringup/) | Top-level launch files (`navis_sim`, `navis_full`), metrics collector |
| [`navis_dashboard`](src/navis_dashboard/) | Web-based mission control dashboard (HTML/CSS/JS + rosbridge) |
| [`navis_msgs`](src/navis_msgs/) | Custom ROS 2 message and service definitions |
| [`navis_interfaces`](src/navis_interfaces/) | Shared constants (topic names, frame IDs, thresholds) |

---

## Prerequisites

| Dependency | Version |
|------------|---------|
| Ubuntu | 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| Webots | R2023b+ |
| Python | 3.10+ |
| Nav2 | Humble release |
| SLAM Toolbox | Humble release |

### Python Dependencies

```
ultralytics>=8.0.0
opencv-python>=4.7.0
numpy>=1.24.0
```

### ROS 2 Package Dependencies

```bash
sudo apt install \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-webots-ros2-driver \
  ros-humble-rosbridge-suite \
  ros-humble-tf2-tools \
  ros-humble-teleop-twist-keyboard
```

---

## Build

```bash
# Clone the repository
git clone https://github.com/Vaibhavsolanki1/Trisul.git navis_ws
cd navis_ws

# Install ROS 2 dependencies
rosdep install --from-paths . --ignore-src -r -y

# Build all packages
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

---

## Run

### Simulation Only

Launch the Webots simulation with the robot spawned in the warehouse:

```bash
ros2 launch navis_bringup navis_sim.launch.py
```

### Full System

Launch everything — simulation, navigation, perception, world model, and dashboard:

```bash
ros2 launch navis_bringup navis_full.launch.py
```

### Individual Components

```bash
# SLAM mapping (drive with teleop to build map)
ros2 launch navis_navigation mapping.launch.py

# Autonomous navigation (uses saved map)
ros2 launch navis_navigation navigation.launch.py

# AI perception pipeline
ros2 launch navis_perception perception.launch.py

# Dashboard (open http://localhost:8080 in browser)
ros2 launch navis_dashboard dashboard.launch.py

# Teleop for manual driving
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## ROS 2 Topics

### Sensor Topics

| Topic | Type | Source |
|-------|------|--------|
| `/camera/image_raw` | `sensor_msgs/Image` | Webots camera driver |
| `/scan` | `sensor_msgs/LaserScan` | Webots LiDAR driver |
| `/imu` | `sensor_msgs/Imu` | Webots IMU driver |
| `/odom` | `nav_msgs/Odometry` | Webots wheel encoders |

### Perception Topics

| Topic | Type | Source |
|-------|------|--------|
| `/detections` | `navis_msgs/DetectionArray` | YOLO detector node |
| `/detections/image` | `sensor_msgs/Image` | Annotated camera feed |

### World Model Topics

| Topic | Type | Source |
|-------|------|--------|
| `/world_model/objects` | `navis_msgs/WorldObjectArray` | World model node |
| `/world_model/status` | `navis_msgs/MissionStatus` | Mission state machine |

### Navigation Topics

| Topic | Type | Source |
|-------|------|--------|
| `/cmd_vel` | `geometry_msgs/Twist` | Nav2 controller / PID |
| `/map` | `nav_msgs/OccupancyGrid` | SLAM / map server |
| `/plan` | `nav_msgs/Path` | Nav2 planner |
| `/goal_pose` | `geometry_msgs/PoseStamped` | RViz / Dashboard |
| `/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | AMCL |

### Diagnostics

| Topic | Type | Source |
|-------|------|--------|
| `/diagnostics` | `diagnostic_msgs/DiagnosticArray` | Metrics collector |

---

## Custom Messages

### `navis_msgs/Detection`
```
string    class_name
float32   confidence
int32[4]  bbox
float32[2] center
```

### `navis_msgs/DetectionArray`
```
std_msgs/Header header
Detection[]     detections
float32         inference_time_ms
```

### `navis_msgs/WorldObject`
```
uint32                    id
string                    class_name
geometry_msgs/Point       position
float32                   confidence
builtin_interfaces/Time   last_seen
bool                      is_dynamic
```

### `navis_msgs/WorldObjectArray`
```
std_msgs/Header header
WorldObject[]   objects
```

### `navis_msgs/MissionStatus`
```
string   state
float32  elapsed_time
float32  distance_traveled
uint32   objects_detected
uint32   collision_count
```

### Services

**`navis_msgs/SetGoal`**
```
float64 goal_x
float64 goal_y
---
bool    success
string  message
```

**`navis_msgs/GetWorldState`**
```
---
WorldObjectArray       objects
geometry_msgs/Pose     robot_pose
```

---

## TF Frame Tree

```
map
 └── odom
      └── base_link
           ├── camera_link
           ├── lidar_link
           └── imu_link
```

---

## Project Structure

```
navis_ws/
├── AGENTS.md                         # AI agent rules (root)
├── .agents/                          # AI agent config (local only)
│   ├── rules/
│   │   ├── ai-core-rules.md
│   │   └── ui-design-rules.md
│   └── tasks/
│       ├── head1-ai-perception.md
│       ├── head2-robotics-simulation.md
│       └── head3-platform-integration.md
├── .gitignore
├── navis_control/                    # [Head 2] PID controller
│   ├── navis_control/
│   │   └── pid_controller_node.py
│   ├── package.xml
│   └── setup.py
├── navis_description/                # [Head 2] Robot model & worlds
│   ├── controllers/
│   │   └── obstacle_mover/
│   ├── launch/
│   │   └── simulation.launch.py
│   ├── protos/
│   ├── urdf/
│   │   └── navis_robot.urdf
│   └── worlds/
│       ├── warehouse_simple.wbt
│       └── warehouse_dynamic.wbt
├── navis_navigation/                 # [Head 2] Nav2 + SLAM config
│   ├── config/
│   │   ├── nav2_params.yaml
│   │   └── slam_params.yaml
│   ├── launch/
│   │   ├── mapping.launch.py
│   │   └── navigation.launch.py
│   ├── maps/
│   └── scripts/
├── src/
│   ├── navis_bringup/                # [Head 3] Top-level launch
│   │   ├── launch/
│   │   │   ├── navis_sim.launch.py
│   │   │   └── navis_full.launch.py
│   │   ├── navis_bringup/
│   │   │   └── metrics_collector_node.py
│   │   └── config/
│   ├── navis_dashboard/              # [Head 3] Web dashboard
│   │   ├── navis_dashboard/
│   │   │   └── server.py
│   │   └── www/
│   │       ├── index.html
│   │       ├── css/
│   │       └── js/
│   ├── navis_interfaces/             # [Head 3] Shared constants
│   │   └── navis_interfaces/
│   │       └── constants.py
│   ├── navis_msgs/                   # [Head 3] Message definitions
│   │   ├── msg/
│   │   │   ├── Detection.msg
│   │   │   ├── DetectionArray.msg
│   │   │   ├── WorldObject.msg
│   │   │   ├── WorldObjectArray.msg
│   │   │   └── MissionStatus.msg
│   │   └── srv/
│   │       ├── SetGoal.srv
│   │       └── GetWorldState.srv
│   ├── navis_perception/             # [Head 1] YOLO + depth
│   │   ├── navis_perception/
│   │   │   ├── yolo_detector_node.py
│   │   │   ├── image_processor.py
│   │   │   └── depth_estimator.py
│   │   ├── config/
│   │   └── launch/
│   │       └── perception.launch.py
│   ├── navis_training/               # [Head 1] Dataset & training
│   │   ├── navis_training/
│   │   │   ├── generate_dataset.py
│   │   │   ├── train_yolo.py
│   │   │   ├── validate_model.py
│   │   │   └── export_model.py
│   │   └── data/
│   └── navis_world_model/            # [Head 1] Semantic model
│       ├── navis_world_model/
│       │   ├── world_model_node.py
│       │   ├── object_tracker.py
│       │   └── semantic_layer.py
│       ├── config/
│       └── launch/
```

---

## Dashboard

The NAVIS Dashboard is a browser-based mission control interface accessible at `http://localhost:8080` when running the full system.

**Panels:**
- **Robot Position** — real-time 2D map with robot dot
- **Camera Feed** — live video stream from onboard camera
- **Detections** — YOLO-annotated image with bounding boxes
- **LiDAR Visualization** — 2D point cloud scatter plot
- **Map** — occupancy grid from SLAM
- **Navigation Path** — planned route overlay
- **Mission Status** — state machine, timer, metrics
- **Metrics Table** — inference latency, distance, collisions, objects

**Navigation control:** click on the map to send a goal pose directly from the browser.

---

## Training Pipeline

Generate a custom YOLO dataset from Webots and train on warehouse-specific objects:

```bash
# 1. Generate dataset (runs Webots Supervisor)
ros2 run navis_training generate_dataset

# 2. Train YOLOv8n
ros2 run navis_training train_yolo

# 3. Validate model (target: mAP@0.5 > 0.7)
ros2 run navis_training validate_model

# 4. Export best weights to perception package
ros2 run navis_training export_model
```

**Object classes:** `box (0)`, `cone (1)`, `person (2)`, `shelf (3)`, `pallet (4)`

---

## Team Structure

| Head | Codename | Domain | Packages |
|------|----------|--------|----------|
| **Head 1** | Brain | AI & Perception | `navis_perception`, `navis_world_model`, `navis_training` |
| **Head 2** | Body | Robotics & Simulation | `navis_description`, `navis_navigation`, `navis_control` |
| **Head 3** | Interface | Platform & Integration | `navis_bringup`, `navis_dashboard`, `navis_msgs`, `navis_interfaces` |

---

## License

This project is developed as part of an autonomous robotics competition/research initiative.

---

<p align="center">
  <strong>🔱 Trishul — Three Heads, One Mission</strong>
</p>
