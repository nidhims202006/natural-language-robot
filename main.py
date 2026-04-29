"""
Natural Language to Robot Motion
Day 8: Control Panel GUI connected to simulation
"""
import pybullet as p
import pybullet_data
import time
import queue
from generate_arm import save_arm_urdf
from terrain import TerrainManager
from objects import SceneObjects
from ik_solver import IKSolver
from gui import ControlPanel

ARM_SCALE   = 1.0
ARM_LENGTHS = [0.30, 0.25, 0.20, 0.15, 0.10, 0.05]

save_arm_urdf(scale=ARM_SCALE, link_lengths=ARM_LENGTHS)

# Communication channel between GUI and simulation
command_queue = queue.Queue()

# Start GUI in background
panel = ControlPanel(command_queue)
panel.start()
time.sleep(0.6)   # Give GUI time to open

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
for _ in range(150):
    p.stepSimulation()
    time.sleep(1 / 480)

ik = IKSolver(arm_id)
terrain_slider  = p.addUserDebugParameter("Terrain  0=Lab  1=Rocky  2=Sand", 0, 2, 0)
current_terrain = 0
TERRAIN_MAP     = {0: "lab", 1: "rocky", 2: "sand"}

panel.log("✅ Simulation ready! (AI brain not connected yet — comes Day 9)")
panel.set_status("● Ready — GUI connected to simulation")

print("\n✅ Two windows open: PyBullet (3D) + Control Panel (GUI)")
print("⏹️  Ctrl+C to quit\n")

try:
    while True:
        p.stepSimulation()

        t_val = round(p.readUserDebugParameter(terrain_slider))
        if t_val != current_terrain:
            current_terrain = t_val
            terrain.swap_terrain(TERRAIN_MAP[t_val])

        try:
            msg_type, msg_data = command_queue.get_nowait()
            if msg_type == "command":
                panel.log(f"📨 Command received: '{msg_data}' (AI connects Day 9)")
                panel.set_status("● Ready")
        except queue.Empty:
            pass

        time.sleep(1 / 240)

except KeyboardInterrupt:
    print("\n👋 Goodbye!")
    p.disconnect()