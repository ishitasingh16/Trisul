import math
from controller import Supervisor


def main():
    robot = Supervisor()
    timestep = int(robot.getBasicTimeStep())
    node = robot.getSelf()
    trans_field = node.getField("translation")

    center_x = 0.0
    center_y = 0.0
    center_z = 0.5
    amplitude = 2.5
    speed = 0.5

    t = 0.0
    while robot.step(timestep) != -1:
        t += (timestep / 1000.0) * speed
        current_y = center_y + amplitude * math.sin(t)
        trans_field.setSFVec3f([center_x, current_y, center_z])


if __name__ == '__main__':
    main()
