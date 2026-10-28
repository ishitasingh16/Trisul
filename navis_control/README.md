# navis_control

The `pid_controller_node` follows a `nav_msgs/Path` on `/plan` and publishes bounded `geometry_msgs/Twist` commands on `/cmd_vel`. Nav2's DWB controller remains the recommended MVP controller; this node is available for isolated controller tuning.
