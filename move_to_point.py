import math


class MoveToTargetPoint:
    def __init__(self,
                 position_tolerance=0.1,
                 angle_tolerance=5.0
                 ):
        self.position_tolerance = position_tolerance
        self.angle_tolerance = angle_tolerance

        self.target_pose = None  # target pose
        self.current_pose = None  # current pose

        self.linear_velocity = 0.0  # velocity command
        self.angular_velocity = 0.0

    def setpoint(self, pos):
        self.target_pose = {"x": pos[0],
                            "y": pos[1], "z": pos[2], "yaw": pos[3]}
        print(f"Target set to: {self.target_pose}")
        self._move_to_target()
        if self.is_ready():
            print("Target reached!.")
            self.linear_velocity = 0.0  # velocity command
            self.angular_velocity = 0.0

    def is_ready(self):
        """
        check if the robot has reached the target pose.
        """
        current_pose = self.current_pose  # get current pose
        if self._check_pose_reached_2d(current_pose, self.target_pose):
            print("Target reached.")
            return True
        else:
            return False

    def _move_to_target(self):
        """
        control the robot to move to the target pose.
        """
        while not self.is_ready() and self.current_pose:
            current_pose = self.current_pose
            # calculate position error
            position_error = self._calculate_position_error(
                current_pose, self.target_pose)
            # calculate velocity
            v, omega = self._calculate_velocity(position_error)
            self.linear_velocity = v
            self.angular_velocity = omega

    def update_current_pose(self, current_tran, current_rot):
        self.current_pose = {
            "x": current_tran[0],
            "y": current_tran[1],
            "z": current_tran[2],
            "roll": current_rot[0],
            "pitch": current_rot[1],
            "yaw": current_rot[2]
        }
        # print(f"update_current_pose: {self.current_pose}")
        return self.current_pose

    def _check_pose_reached_2d(self, current_pose, target_pose):
        position_reached = (
            abs(current_pose["x"] - target_pose["x"]) < self.position_tolerance and
            abs(current_pose["y"] - target_pose["y"]) < self.position_tolerance
        )
        return position_reached

    def _calculate_position_error(self, current_pose, target_pose):
        """
        calculate the position error between the current pose and the target pose.
        """
        position_error = {
            "x": target_pose["x"] - current_pose["x"],
            "y": target_pose["y"] - current_pose["y"],
            "z": target_pose["z"] - current_pose["z"],
            "yaw": math.degrees(math.atan2(target_pose["y"] - current_pose["y"], target_pose["x"] - current_pose["x"])) - current_pose["yaw"]
        }
        print(f"Position error: {position_error}")
        return position_error

    def _calculate_velocity(self, position_error):
        """
        a simple proportional controller to calculate the velocity command.
        """
        # simple proportional control
        k_v = 0.1  # linear velocity gain
        k_omega = 0.05  # angular velocity gain
        
        v = k_v * (position_error["x"]**2 + position_error["y"]**2)**0.5
        omega = k_omega * position_error["yaw"]  # we only control yaw
        return v, omega

