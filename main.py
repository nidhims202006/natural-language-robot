"""
Natural Language to Robot Motion
 Inverse Kinematics — arm moves to target positions
"""
import pybullet as p
import pybullet_data
import time
from generate_arm import save_arm_urdf
from terrain import TerrainManager
from objects import SceneObjects
from ik_solver import IKSolver

ARM_SCALE   = 1.0
ARM_LENGTHS = [0.30, 0.25, 0.20, 0.15, 0.10, 0.05]

save_arm_urdf(scale=ARM_SCALE, link_lengths=ARM_LENGTHS)

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.resetDebugVisualizerCamera(
    cameraDistance=1.5, cameraYaw=50,
    cameraPitch=-30, cameraTargetPosition=[0.3, 0, 0.2]
)
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)
p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)

terrain = TerrainManager()
terrain.load_flat_floor()

arm_id = p.loadURDF("robot_arm.urdf", [0, 0, 0],
                     p.getQuaternionFromEuler([0, 0, 0]), useFixedBase=True)
revolute_joints = [i for i in range(p.getNumJoints(arm_id))
                   if p.getJointInfo(arm_id, i)[2] == p.JOINT_REVOLUTE]
for i, j in enumerate(revolute_joints):
    if i < 6:
        p.resetJointState(arm_id, j, [0, 0.3, -0.8, 0, 0.5, 0][i])

scene = SceneObjects()
scene.setup_default_scene()

# Let things settle
for _ in range(150):
    p.stepSimulation()
    time.sleep(1 / 480)

# Create the IK solver
ik = IKSolver(arm_id)

# ── Test IK: move arm to visit each object ────────────────────────────────────
print("\n IK Test: Moving arm to visit each object...")
test_targets = ["red_cube", "blue_cube", "green_cube"]

for obj_name in test_targets:
    pos = scene.get_position(obj_name)
    if pos:
        # Hover above the object
        hover_pos = [pos[0], pos[1], pos[2] + 0.12]
        ik.move_to_position(hover_pos)
        time.sleep(0.4)

ik.move_to_home()

print("\n IK test complete!")
print(" Ctrl+C to quit\n")

try:
    while True:
        p.stepSimulation()
        time.sleep(1 / 240)
except KeyboardInterrupt:
    print("\n Goodbye!")
    p.disconnect()