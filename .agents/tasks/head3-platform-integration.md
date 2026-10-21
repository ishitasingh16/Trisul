# Head 3 — Platform & Integration 🖥️

**Codename:** Interface
**Member:** (Assign name here)

---

## Department Ownership

You own these packages. Only you (or someone you authorize) should modify them:

| Package | Purpose |
|---------|---------|
| `navis_bringup/` | Top-level launch files, Nav2/SLAM config files, RViz config, maps |
| `navis_dashboard/` | Web dashboard frontend, rosbridge relay |
| `navis_msgs/` | Custom message and service definitions (shared, but you maintain) |
| `navis_interfaces/` | Shared constants, transform utilities |

---

## Task List — By Phase

### Phase 1 — Project Setup & Infrastructure

- [ ] Initialize the ROS 2 workspace structure in the repo
- [ ] Create all package directories with correct `package.xml` and `setup.py`/`CMakeLists.txt`
- [ ] Create `.gitignore` for ROS 2 project (ignore `build/`, `install/`, `log/`, `datasets/`, `runs/`, `*.pyc`, `__pycache__/`)
- [ ] Verify `colcon build` succeeds on empty packages
- [ ] Document build instructions in `README.md`

### Phase 2–3 — Launch Files & Config

- [ ] Create `navis_sim.launch.py` — launches Webots + robot driver only
- [ ] Create `navis_nav.launch.py` — launches sim + SLAM or AMCL + Nav2
- [ ] Create `navis_full.launch.py` — launches everything (sim + nav + perception + world model + dashboard)
- [ ] Create `rviz_config.rviz` — pre-configured RViz layout showing:
  - Map
  - Robot model
  - LiDAR scan
  - Camera image
  - Navigation path
  - TF tree
  - Costmap
- [ ] Coordinate with Head 2 on Nav2 config file locations and parameters

### Phase 4 — Message Definitions

- [ ] Create `navis_msgs` package (ament_cmake, required for msg generation)
- [ ] Define and build messages:
  - `Detection.msg` (class_name, confidence, bbox, center)
  - `DetectionArray.msg` (header, detections[], inference_time_ms)
  - `WorldObject.msg` (id, class_name, position, confidence, last_seen, is_dynamic)
  - `WorldObjectArray.msg` (header, objects[])
  - `MissionStatus.msg` (state, elapsed_time, distance_traveled, objects_detected, collision_count)
- [ ] Define services:
  - `SetGoal.srv` (goal_x, goal_y → success, message)
  - `GetWorldState.srv` (→ WorldObjectArray, robot_pose)
- [ ] Verify messages build: `ros2 interface show navis_msgs/msg/Detection`
- [ ] **Freeze message definitions** — no changes after this without all-team agreement

### Phase 9 — Dashboard

- [ ] Install and configure `rosbridge_suite`
  - `sudo apt install ros-humble-rosbridge-suite`
  - Launch: `rosbridge_websocket_launch.xml`
- [ ] Create dashboard HTML/CSS/JS using the NAVIS design system (see `ui-design-rules.md`)
- [ ] Implement dashboard panels:
  - [ ] **Robot Position** — dot on 2D map (subscribe to `/amcl_pose` or `/tf`)
  - [ ] **Camera Feed** — live video from `/camera/image_raw/compressed`
  - [ ] **Detections** — annotated image from `/detections/image`
  - [ ] **LiDAR Visualization** — 2D scatter from `/scan`
  - [ ] **Map** — occupancy grid from `/map`
  - [ ] **Navigation Path** — planned route from `/plan`
  - [ ] **Mission Status** — state, timer, metrics from `/world_model/status`
  - [ ] **Metrics Table** — inference latency, distance, collisions, objects detected
- [ ] Implement navigation goal control — click on map to publish `/goal_pose`
- [ ] Use `roslibjs` for WebSocket communication
- [ ] Test: Dashboard connects to rosbridge and shows live data
- [ ] Test: Navigation goal sent from dashboard triggers robot movement

### Ongoing — Testing & Metrics

- [ ] Create `metrics_collector_node.py` (Python)
  - Subscribe to `/odom`, `/detections`, `/cmd_vel`, `/world_model/status`
  - Track: mission time, distance, collisions, replanning events, inference times
  - Publish to `/diagnostics` (DiagnosticArray)
  - Log to CSV for post-analysis
- [ ] Write integration test scripts:
  - T01: Robot spawns → sensors publish within 5s
  - T04: Nav2 goal → robot reaches within 2x optimal time
  - T11: Full mission → A→B with dynamic obstacles, no collision
- [ ] Run benchmark protocol: 100 randomized missions
- [ ] Generate results table for demo

### Ongoing — Documentation

- [ ] Maintain `README.md` with:
  - Project description
  - Setup instructions
  - Build and run instructions
  - Architecture diagram
- [ ] Document all ROS 2 topics, messages, and TF frames in the repo
- [ ] Prepare demo slides / architecture diagram for presentation

---

## Dependencies on Other Heads

| You Need | From | Status |
|----------|------|--------|
| Webots world + robot working | Head 2 | ⬜ Pending |
| Nav2 navigation working | Head 2 | ⬜ Pending |
| YOLO detector publishing `/detections` | Head 1 | ⬜ Pending |
| World Model publishing `/world_model/objects` | Head 1 | ⬜ Pending |

## What You Provide to Others

| You Provide | To | When |
|------------|-----|------|
| Built `navis_msgs` package | Head 1, Head 2 | Phase 4 start |
| Launch files that compose everything | Head 1, Head 2 | Phase 2–3 |
| RViz config for debugging | Head 1, Head 2 | Phase 2 |
| Dashboard for demo | Everyone | Phase 9 |

---

## Key Rules for Head 3

1. **Message definitions are your most critical early deliverable.** Head 1 and Head 2 are blocked until messages build.
2. **You are the integration gatekeeper.** If someone's node doesn't work with the full launch, you flag it.
3. **Follow `ui-design-rules.md` strictly** for all dashboard work. No freelancing on colors.
4. **Don't modify YOLO code, Webots worlds, or Nav2 algorithms.** Your job is to connect and present them.
5. **Start dashboard work early** using mock/dummy data. Don't wait for real topics to exist.
6. **Test end-to-end after every integration.** Break early, fix early.
