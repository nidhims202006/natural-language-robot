"""
Natural Language to Robot Motion
Day 3: 6-DOF Robotic Arm in the Scene
"""
import pybullet as p
import pybullet_data
import time
from generate_arm import save_arm_urdf

# ── CUSTOMIZE YOUR ARM ────────────────────────────────────────────────────────
ARM_SCALE   = 1.0
ARM_LENGTHS = [0.30, 0.25, 0.20, 0.15, 0.10, 0.05]
# ─────────────────────────────────────────────────────────────────────────────

# Generate the arm blueprint file before loading
save_arm_urdf(scale=ARM_SCALE, link_lengths=ARM_LENGTHS)

# Start PyBullet
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.resetDebugVisualizerCamera(
    cameraDistance=1.8, cameraYaw=45,
    cameraPitch=-25, cameraTargetPosition=[0, 0, 0.5]
)
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)
p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)

# Load floor and arm
floor_id = p.loadURDF("plane.urdf")
arm_id = p.loadURDF(
    "robot_arm.urdf", [0, 0, 0],
    p.getQuaternionFromEuler([0, 0, 0]),
    useFixedBase=True   # Bolted to the floor, doesn't fall over
)
print(f" Arm loaded! Body ID = {arm_id}")

# Print joint information
num_joints = p.getNumJoints(arm_id)
print(f"\n📋 Your arm has {num_joints} joints:")
revolute_joints = []
for i in range(num_joints):
    info      = p.getJointInfo(arm_id, i)
    jname     = info[1].decode("utf-8")
    jtype_num = info[2]
    jtype_str = {0: "REVOLUTE", 1: "PRISMATIC", 4: "FIXED"}.get(jtype_num, "?")
    print(f"   [{i}] {jname}  ({jtype_str})")
    if jtype_num == p.JOINT_REVOLUTE:
        revolute_joints.append(i)

# Set a natural starting pose (slightly bent looks better than fully upright)
start_angles = [0, 0.3, -0.8, 0, 0.5, 0]
for i, joint_idx in enumerate(revolute_joints):
    if i < len(start_angles):
        p.resetJointState(arm_id, joint_idx, start_angles[i])

print("\n🎮 Camera: left-drag=rotate | scroll=zoom | right-drag=pan")
print("⏹️  Ctrl+C to quit\n")

try:
    while True:
        p.stepSimulation()
        time.sleep(1 / 240)
except KeyboardInterrupt:
    print("\n Goodbye!")
    p.disconnect()