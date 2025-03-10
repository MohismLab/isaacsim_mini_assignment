from isaacsim import SimulationApp
# should always be on the top of import statements
simulation_app = SimulationApp({"headless": False})

from move_to_point import MoveToTargetPoint
import threading
from pxr import Gf, UsdGeom
from transforms3d.euler import quat2euler
from omni.isaac.wheeled_robots.robots import WheeledRobot
from omni.isaac.wheeled_robots.controllers.differential_controller import DifferentialController
from omni.isaac.nucleus import get_assets_root_path
from omni.isaac.core.objects import FixedCuboid
from omni.isaac.core.utils.prims import define_prim, get_prim_at_path
from omni.isaac.core import World
import numpy as np
import carb



class MoveToTarget:
    def __init__(
        self,
        target_x: float = 2.0,
        target_y: float = 2.0,
    ) -> None:
        """
        Use a simple p controller to move the robot to a target point.
        """
        self.target_pos = [target_x, target_y, 0, 0]

        self.reset_needed = False
        self.thread = None
        self.thread_running = False

        # spawn world
        self.my_world = World(stage_units_in_meters=1.0,
                              physics_dt=1 / 500, rendering_dt=1 / 50)
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/Jetbot/jetbot.usd"

        # Add a jetbot robot
        self.my_jetbot = self.my_world.scene.add(
            WheeledRobot(
                prim_path="/World/Jetbot",
                name="my_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0.0, 0.0, 0.0]),
            )
        )

        # Add a cube as a target
        cube = self.my_world.scene.add(
            FixedCuboid(
                name="cube",
                position=np.array([target_x, target_y, 0.2]),
                prim_path="/World/Cube",
                scale=np.array([0.5, 0.5, 0.5]),
                size=1.0,
                color=np.array([0, 0, 1]),
            )
        )
        prim = define_prim("/World/Ground", "Xform")
        # Get the prim of base link of the robot
        prim_jetbot = get_prim_at_path("/World/Jetbot/chassis")

        asset_path = assets_root_path + "/Isaac/Environments/Grid/default_environment.usd"
        prim.GetReferences().AddReference(asset_path)

        # Get groudtruth pose
        self.xform = UsdGeom.Xformable(prim_jetbot)
        self.translate_op = self.xform.GetOrderedXformOps()[0]
        self.rotate_op = self.xform.GetOrderedXformOps()[1]

        # initialize the differential controller
        self.jetbot_controller = DifferentialController(
            name="simple_control", wheel_radius=0.03, wheel_base=0.1125)
        self.move_to_point = MoveToTargetPoint()

        self.my_world.reset()

    def get_current_pose(self):
        """
        Gets the current position and orientation of the robot.
        """
        translate_values = self.translate_op.Get()
        rotate_values = self.rotate_op.Get()
        quaternion = [rotate_values.GetReal(), rotate_values.GetImaginary(
        )[0], rotate_values.GetImaginary()[1], rotate_values.GetImaginary()[2]]
        euler_angles = quat2euler(quaternion)
        current_translation = [translate_values[0], translate_values[
            1], translate_values[2]]
        current_rotation = [np.degrees(euler_angles[0]), np.degrees(
            euler_angles[1]), np.degrees(euler_angles[2])]
        return current_translation, current_rotation

    def update_pose_and_move(self):
        current_pose = self.get_current_pose()
        if current_pose:
            print(f"Current pose: {current_pose}")
            current_pos, current_rot = current_pose  # Unpack the tuple directly
            self.move_to_point.update_current_pose(current_pos, current_rot)

    def setpoint_(self):
        pos = self.target_pos
        self.move_to_point.setpoint(pos)
        self.threading_running = False

    def execute_movement(self):
        self.update_pose_and_move()
        self.my_jetbot.apply_wheel_actions(
            self.jetbot_controller.forward(command=[self.move_to_point.linear_velocity, self.move_to_point.angular_velocity]))

        if not self.thread_running:
            self.thread_running = True
            self.thread = threading.Thread(target=self.setpoint_)
            self.thread.start()

    def run_goto_target(self):
        reset_needed = False
        while simulation_app.is_running():
            self.my_world.step(render=True)
            if self.my_world.is_stopped() and not reset_needed:
                reset_needed = True
            if self.my_world.is_playing():
                if reset_needed:
                    self.my_world.reset()
                    self.jetbot_controller.reset()
                    reset_needed = False

                self.execute_movement()


if __name__ == "__main__":
    control = MoveToTarget(target_x=2.0, target_y=2.0)
    control.run_goto_target()
