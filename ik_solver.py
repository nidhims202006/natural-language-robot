"""
ik_solver.py
Inverse Kinematics Engine.

Given a target position [x, y, z] in the 3D world,
this module calculates the required angles for all 6 joints
and animates the arm smoothly to reach that point.


"""
import pybullet as p
import time
import math


class IKSolver:
    def __init__(self, arm_id):
        self.arm_id     = arm_id
        self.num_joints = p.getNumJoints(arm_id)

        # The end effector is always the last link
        self.ee_index = self.num_joints - 1

        # Collect the indices of all REVOLUTE (rotating) joints
        self.revolute_joints = [
            i for i in range(self.num_joints)
            if p.getJointInfo(arm_id, i)[2] == p.JOINT_REVOLUTE
        ]

        print(f" IK Solver initialized")
        print(f"   Arm joints: {self.num_joints}  |  End-effector index: {self.ee_index}")
        print(f"   Revolute joints: {self.revolute_joints}")

    def calculate_ik(self, target_pos, target_orn=None):
        """
        Ask PyBullet: 'What joint angles would put the tip at target_pos?'
        Returns a list of angles (in radians).
        """
        if target_orn is None:
            # Default orientation: gripper points slightly downward
            target_orn = p.getQuaternionFromEuler([0, -math.pi / 2, 0])

        angles = p.calculateInverseKinematics(
            self.arm_id,
            self.ee_index,
            target_pos,
            target_orn,
            maxNumIterations=200,
            residualThreshold=0.001,
            jointDamping=[0.01] * self.num_joints
        )
        return angles

    def move_to_position(self, target_pos, target_orn=None,
                          steps=150, delay=1 / 120):
        """
        Smoothly animate the arm from its current pose to target_pos.

        Steps analogy: like a flip-book animation — more pages = smoother motion.

        Args:
            target_pos  : [x, y, z] destination in meters
            steps       : animation frames (120 = ~1 second at 120fps)
            delay       : seconds between frames
        Returns:
            True if successful, False if IK had no solution
        """
        print(f" Moving to {[round(v, 3) for v in target_pos]} ...")

        # Snapshot of where the joints are RIGHT NOW
        current_angles = [
            p.getJointState(self.arm_id, j)[0]
            for j in self.revolute_joints
        ]

        # Where do the joints need to END UP?
        target_angles_all = self.calculate_ik(target_pos, target_orn)
        target_angles = [target_angles_all[i]
                          for i in range(len(self.revolute_joints))]

        # Animate: interpolate smoothly from current → target
        for step in range(steps + 1):
            t = step / steps                     # 0.0 → 1.0
            t_smooth = t * t * (3.0 - 2.0 * t)  # smoothstep easing

            for i, joint_idx in enumerate(self.revolute_joints):
                if i < len(target_angles):
                    angle = (current_angles[i]
                              + (target_angles[i] - current_angles[i]) * t_smooth)
                    p.setJointMotorControl2(
                        self.arm_id, joint_idx,
                        p.POSITION_CONTROL,
                        targetPosition=angle,
                        force=150,
                        maxVelocity=3.0
                    )

            p.stepSimulation()
            time.sleep(delay)

        print(" Reached target!")
        return True

    def move_to_home(self, steps=120):
        """Return the arm to its upright resting position."""
        home = [0, 0.3, -0.8, 0, 0.5, 0]
        print(" Returning to home pose...")

        current = [p.getJointState(self.arm_id, j)[0]
                   for j in self.revolute_joints]

        for step in range(steps + 1):
            t = step / steps
            t_s = t * t * (3 - 2 * t)
            for i, j in enumerate(self.revolute_joints):
                if i < len(home):
                    angle = current[i] + (home[i] - current[i]) * t_s
                    p.setJointMotorControl2(
                        self.arm_id, j,
                        p.POSITION_CONTROL,
                        targetPosition=angle,
                        force=150,
                        maxVelocity=2.0
                    )
            p.stepSimulation()
            time.sleep(1 / 120)

        print(" Home!")

    def get_ee_position(self):
        """Returns the current [x, y, z] of the arm's tip."""
        state = p.getLinkState(self.arm_id, self.ee_index)
        return list(state[0])