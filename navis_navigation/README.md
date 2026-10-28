# navis_navigation

Head 2 navigation assets for SLAM, localization, Nav2 planning, and dynamic obstacle testing.

## Mapping

1. Start `navis_description` with `simulation.launch.py`.
2. Start `mapping.launch.py` to run online async SLAM.
3. Drive with `ros2 run teleop_twist_keyboard teleop_twist_keyboard`.
4. Save the map with `ros2 run nav2_map_server map_saver_cli -f navis_navigation/maps/warehouse`.

## Navigation

Use the saved map with `navigation.launch.py` and pass the map to Nav2's map server. The planner is Navfn with A*, the controller is DWB, and both costmaps use LiDAR obstacle marking/clearing plus inflation.

## Dynamic test

Open `worlds/warehouse_dynamic.wbt`. The Supervisor moves `MOVING_OBSTACLE` across the workspace. Confirm local costmap updates and Nav2 replanning before recording the 10-scenario success rate.
