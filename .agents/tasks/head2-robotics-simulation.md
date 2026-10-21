# Head 2 — Robotics & Simulation 🤖

**Codename:** Body
**Member:** (Assign name here)

---

## Department Ownership

You own these packages. Only you (or someone you authorize) should modify them:

| Package | Purpose |
|---------|---------|
| `navis_description/` | Robot URDF/Proto, Webots worlds, meshes, sensor configs |
| `navis_navigation/` | Custom navigation logic, goal manager, costmap updater |
| `navis_control/` | PID motion controller |

---

## Task List — By Phase

### Phase 2 — Virtual Robot in Webots

- [ ] Design `warehouse_simple.wbt` world
  - Flat textured floor
  - Boundary walls
  - 5–10 static obstacles (boxes, cones, shelves)
  - Marked start zone and goal zone
- [ ] Create or adapt differential-drive robot (e-puck / TIAGo / custom PROTO)
  - Two driven wheels + caster/ball
  - Configure wheel radius and separation
- [ ] Configure virtual sensors:
  - Camera: 640×480, 30 FPS, save FOV value
  - LiDAR: 360°, 5.6m range, ~200 points
  - IMU: 3-axis accel + gyro
  - Odometry (from wheel encoders)
- [ ] Create robot URDF with correct TF frames
  - `base_link` → `camera_link` (correct offset)
  - `base_link` → `lidar_link` (correct offset)
  - `base_link` → `imu_link`
- [ ] Integrate with `webots_ros2_driver`
- [ ] Verify with `ros2 run tf2_tools view_frames` — TF tree must be clean
- [ ] Test: Robot moves via `ros2 run teleop_twist_keyboard teleop_twist_keyboard`
- [ ] Test: All sensor topics publish data — verify with `ros2 topic echo`
- [ ] **Share with Head 1:** Camera FOV, LiDAR angular range, sensor frame names

### Phase 3 — SLAM & Autonomous Navigation

- [ ] Configure SLAM Toolbox (`slam_params.yaml`)
  - Online async mode
  - `use_sim_time: true`
- [ ] Generate warehouse map by driving robot via teleop
- [ ] Save map using `map_saver_cli`
- [ ] Configure Nav2 (`nav2_params.yaml`)
  - Planner: `NavfnPlanner` with `use_astar: true`
  - Controller: `DWBLocalPlanner` (or `RegulatedPurePursuit`)
  - Global costmap: static layer + inflation
  - Local costmap: obstacle layer + inflation + rolling window
  - Recovery behaviors: spin, backup, wait
  - `use_sim_time: true` everywhere
- [ ] Configure AMCL for localization on saved map
- [ ] Test: Send goal via RViz "2D Goal Pose" — robot navigates to it
- [ ] Test: Robot avoids static obstacles during navigation
- [ ] Test: Robot reaches goal and action returns `succeeded`
- [ ] Tune PID / controller parameters if robot oscillates or overshoots
- [ ] Measure: average navigation time, path length for 5 test goals

### Phase 7 — Dynamic Navigation & Replanning

- [ ] Create `warehouse_dynamic.wbt` (copy of simple + Supervisor-controlled moving obstacle)
- [ ] Write Webots Supervisor script to move an obstacle across the robot's path mid-navigation
- [ ] Verify Nav2 replanning:
  - Local costmap updates when obstacle enters LiDAR range
  - DWB finds alternative trajectory or triggers recovery
  - Global replanning if local fails
- [ ] Integrate YOLO-detected obstacles into Nav2 costmap (coordinate with Head 1)
  - Custom costmap layer or costmap filter
  - Subscribe to `/world_model/objects` for semantic obstacle positions
- [ ] Test: Robot detects moving obstacle, replans, reaches goal
- [ ] Test: Run 10 dynamic scenarios — measure success rate

### Phase 3 (Continued) — Motion Control

- [ ] Implement `pid_controller_node.py` (if not using Nav2's built-in controller)
  - Subscribe to planned path
  - Publish `/cmd_vel` (linear + angular velocity)
  - PID gains: tune P, I, D for smooth following
- [ ] OR: Use Nav2's controller server directly (recommended for MVP)

---

## Dependencies on Other Heads

| You Need | From | Status |
|----------|------|--------|
| `navis_msgs/` package built and available | Head 3 | ⬜ Pending |
| Launch files for full system bringup | Head 3 | ⬜ Pending |
| YOLO costmap obstacle data (Phase 7) | Head 1 | ⬜ Pending |

## What You Provide to Others

| You Provide | To | When |
|------------|-----|------|
| Camera topic `/camera/image_raw` publishing | Head 1 | Phase 2 complete |
| LiDAR topic `/scan` publishing | Head 1 | Phase 2 complete |
| Correct TF tree | Head 1, Head 3 | Phase 2 complete |
| Camera FOV, LiDAR specs (documented) | Head 1 | Phase 2 complete |
| Working Nav2 navigation | Head 3 | Phase 3 complete |
| Webots world with varied objects (for dataset) | Head 1 | Phase 3 complete |

---

## Key Rules for Head 2

1. **Phase 2 is the foundation. Nothing works without it.** Prioritize this above everything.
2. **Verify TF tree after every change** — `ros2 run tf2_tools view_frames`.
3. **Document sensor specs** (FOV, range, resolution) and share with Head 1 immediately.
4. **Don't modify YOLO nodes or the World Model.** Flag issues to Head 1.
5. **Don't modify message definitions or launch files unilaterally.** Coordinate with Head 3.
6. **Keep `use_sim_time: true`** in every config and launch file. Forgetting this breaks everything.
