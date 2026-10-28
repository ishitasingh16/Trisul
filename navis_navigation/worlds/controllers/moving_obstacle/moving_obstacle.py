from math import sin

from controller import Supervisor


supervisor = Supervisor()
step = int(supervisor.getBasicTimeStep())
obstacle = supervisor.getFromDef('MOVING_OBSTACLE')
translation = obstacle.getField('translation')
phase = 0.0

while supervisor.step(step) != -1:
    phase += 0.04
    translation.setSFVec3f([2.0 * sin(phase), 0.0, 0.55])
