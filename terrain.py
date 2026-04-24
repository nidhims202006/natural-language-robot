"""
terrain.py
Manages loading and swapping between different ground surfaces.
Each terrain type removes the old floor and builds a new one.
"""
import pybullet as p
import pybullet_data
import random
import math


class TerrainManager:
    def __init__(self):
        self.terrain_bodies = []   # All PyBullet bodies in the current terrain
        self.terrain_type   = None
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

    # ── Internal: remove everything that belongs to the current terrain ──────
    def _clear(self):
        for body_id in self.terrain_bodies:
            try:
                p.removeBody(body_id)
            except Exception:
                pass
        self.terrain_bodies = []

    # ── TERRAIN 1: Flat laboratory floor ─────────────────────────────────────
    def load_flat_floor(self):
        self._clear()
        floor_id = p.loadURDF("plane.urdf")
        # White-ish lab tile color
        p.changeVisualShape(floor_id, -1, rgbaColor=[0.85, 0.85, 0.88, 1])
        self.terrain_bodies.append(floor_id)
        self.terrain_type = "lab"
        print(" Lab floor loaded")

    # ── TERRAIN 2: Rocky outdoor surface ─────────────────────────────────────
    def load_rocky_terrain(self):
        self._clear()
        # Start with a dark stone-colored base floor
        floor_id = p.loadURDF("plane.urdf")
        p.changeVisualShape(floor_id, -1, rgbaColor=[0.38, 0.35, 0.32, 1])
        self.terrain_bodies.append(floor_id)

        # Scatter 50 random rocks across the floor
        random.seed(123)   # Fixed seed = same layout every time you load it
        count = 0
        for _ in range(80):
            x = random.uniform(-2.5, 2.5)
            y = random.uniform(-2.5, 2.5)
            # Keep the area directly under the arm clear
            if math.sqrt(x * x + y * y) < 0.55:
                continue

            scale = random.uniform(0.02, 0.08)
            gray  = random.uniform(0.30, 0.55)
            color = [gray, gray * 0.96, gray * 0.88, 1]

            # Mix of spheres and irregular boxes for variety
            if random.random() > 0.5:
                cshape = p.createCollisionShape(p.GEOM_SPHERE, radius=scale)
                vshape = p.createVisualShape(p.GEOM_SPHERE, radius=scale, rgbaColor=color)
            else:
                e = [scale,
                     scale * random.uniform(0.5, 1.6),
                     scale * random.uniform(0.3, 0.9)]
                cshape = p.createCollisionShape(p.GEOM_BOX, halfExtents=e)
                vshape = p.createVisualShape(p.GEOM_BOX, halfExtents=e, rgbaColor=color)

            rock_id = p.createMultiBody(
                baseMass=0,   # mass=0 means static — it won't slide around
                baseCollisionShapeIndex=cshape,
                baseVisualShapeIndex=vshape,
                basePosition=[x, y, scale * 0.6],
                baseOrientation=p.getQuaternionFromEuler([
                    random.uniform(0, 0.4),
                    random.uniform(0, 0.4),
                    random.uniform(0, 3.14)
                ])
            )
            self.terrain_bodies.append(rock_id)
            count += 1

        self.terrain_type = "rocky"
        print(f"Rocky terrain loaded ({count} rocks)")

    # ── TERRAIN 3: Sandy desert ───────────────────────────────────────────────
    def load_sand_terrain(self):
        self._clear()
        floor_id = p.loadURDF("plane.urdf")
        p.changeVisualShape(floor_id, -1, rgbaColor=[0.85, 0.76, 0.48, 1])
        self.terrain_bodies.append(floor_id)

        # Add gentle sand dunes (low flat boxes)
        random.seed(456)
        for _ in range(25):
            x = random.uniform(-2.0, 2.0)
            y = random.uniform(-2.0, 2.0)
            if math.sqrt(x * x + y * y) < 0.65:
                continue
            rx = random.uniform(0.08, 0.22)
            ry = random.uniform(0.08, 0.20)
            rz = random.uniform(0.02, 0.05)
            cshape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[rx, ry, rz])
            vshape = p.createVisualShape(
                p.GEOM_BOX, halfExtents=[rx, ry, rz],
                rgbaColor=[0.82, 0.73, 0.44, 1]
            )
            dune_id = p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=cshape,
                baseVisualShapeIndex=vshape,
                basePosition=[x, y, rz],
                baseOrientation=p.getQuaternionFromEuler(
                    [0, 0, random.uniform(0, 3.14)]
                )
            )
            self.terrain_bodies.append(dune_id)

        self.terrain_type = "sand"
        print(" Sandy terrain loaded")

    # ── Public swap method ────────────────────────────────────────────────────
    def swap_terrain(self, terrain_type):
        dispatch = {
            "lab":   self.load_flat_floor,
            "rocky": self.load_rocky_terrain,
            "sand":  self.load_sand_terrain,
        }
        if terrain_type in dispatch:
            dispatch[terrain_type]()
        else:
            print(f" Unknown terrain '{terrain_type}'. Options: lab, rocky, sand")