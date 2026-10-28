class Topics:
    CAMERA_RAW = '/camera/image_raw'
    SCAN = '/scan'
    ODOM = '/odom'
    CMD_VEL = '/cmd_vel'
    MAP = '/map'
    AMCL_POSE = '/amcl_pose'
    PLAN = '/plan'
    GOAL_POSE = '/goal_pose'
    DETECTIONS = '/detections'
    DETECTIONS_IMAGE = '/detections/image'
    WORLD_OBJECTS = '/world_model/objects'
    MISSION_STATUS = '/world_model/status'
    DIAGNOSTICS = '/diagnostics'


class Frames:
    MAP = 'map'
    ODOM = 'odom'
    BASE_LINK = 'base_link'
    CAMERA_LINK = 'camera_link'
    LIDAR_LINK = 'lidar_link'
    IMU_LINK = 'imu_link'


class MissionStates:
    IDLE = 'IDLE'
    NAVIGATING = 'NAVIGATING'
    REPLANNING = 'REPLANNING'
    RECOVERY = 'RECOVERY'
    GOAL_REACHED = 'GOAL_REACHED'
    FAILED = 'FAILED'
