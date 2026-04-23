"""
Natural Language to Robot Motion
Day 2: Basic 3D World — your first PyBullet scene
"""
import pybullet as p
import pybullet_data
import time

# ── Connect to PyBullet with a visual window ──────────────────────────────────
# Think of this like turning on a TV — it opens the 3D display window
physics_client = p.connect(p.GUI)

# Tell PyBullet where its built-in models are (like plane.urdf)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Set gravity (9.81 m/s² downward — same as real world)
p.setGravity(0, 0, -9.81)

# ── Camera starting view ──────────────────────────────────────────────────────
p.resetDebugVisualizerCamera(
    cameraDistance=2.0,   # How far back the camera is
    cameraYaw=45,          # Rotated 45° to the right
    cameraPitch=-30,       # Tilted 30° downward
    cameraTargetPosition=[0, 0, 0]
)

# Turn on shadows for nicer visuals
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)
p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)

# ── Load the flat floor ───────────────────────────────────────────────────────
floor_id = p.loadURDF("plane.urdf")
print(" Floor loaded!")

# ── Add a test box so the scene isn't empty ───────────────────────────────────
# createCollisionShape = defines the physics shape (for bumping into things)
# createVisualShape    = defines how it looks (color, size)
box_collision = p.createCollisionShape(
    p.GEOM_BOX,
    halfExtents=[0.1, 0.1, 0.1]   # Half-size in each direction
)
box_visual = p.createVisualShape(
    p.GEOM_BOX,
    halfExtents=[0.1, 0.1, 0.1],
    rgbaColor=[0.8, 0.2, 0.2, 1]  # Red, Green, Blue, Alpha (0-1 scale)
)
box_id = p.createMultiBody(
    baseMass=1.0,                         # 1 kilogram
    baseCollisionShapeIndex=box_collision,
    baseVisualShapeIndex=box_visual,
    basePosition=[0.5, 0.0, 0.1]          # x=0.5m right, y=0 center, z=0.1m up
)
print(" Test red box created!")

print("\n CAMERA CONTROLS (click inside the 3D window first):")
print("   Left-click + drag  → Rotate the view")
print("   Scroll wheel       → Zoom in / out")
print("   Right-click + drag → Pan (slide) the view")
print("\n⏹️  Press Ctrl+C here in the terminal to quit\n")

# ── Main simulation loop ──────────────────────────────────────────────────────
# This is the heartbeat of the simulation — runs 240 times per second
try:
    while True:
        p.stepSimulation()          # Advance physics by one tiny step
        time.sleep(1 / 240)         # Wait 1/240th of a second
except KeyboardInterrupt:
    print("\n Simulation ended.")
    p.disconnect()