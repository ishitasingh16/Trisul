# NAVIS Head 2 Sensor Contract

This document is the Phase 2 handoff to Head 1 and Head 3.

| Device | Topic | Frame | Configuration |
|---|---|---|---|
| Camera | `/camera/image_raw` | `camera_link` | 640 x 480, 30 FPS, 60 degree FOV (1.0472 rad) |
| LiDAR | `/scan` | `lidar_link` | 360 degree, 5.6 m maximum range, 200 horizontal samples |
| IMU | `/imu` | `imu_link` | 3-axis acceleration and 3-axis angular velocity |
| Odometry | `/odom` | `odom` to `base_link` | Derived from left/right wheel encoders |

Static TF offsets from `base_link`:

- `camera_link`: `(0.21, 0.00, 0.09)` m
- `lidar_link`: `(0.00, 0.00, 0.17)` m
- `imu_link`: `(0.00, 0.00, 0.16)` m

Differential-drive geometry:

- Wheel radius: `0.09` m
- Wheel separation: `0.38` m
- Webots basic time step: `32` ms
- All ROS nodes and configuration use `use_sim_time: true`.

Runtime verification commands:

```text
ros2 topic echo /camera/image_raw
ros2 topic echo /scan
ros2 topic echo /imu
ros2 topic echo /odom
ros2 run tf2_tools view_frames
```
