FROM osrf/ros:humble-desktop-full AS ros2
LABEL maintainer="mc45197@um.edu.mo"

ENV DEBIAN_FRONTEND=noninteractive
ENV HEADLESS=false
ARG DEVELOPMENT=false

# Install linux packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-pip \
    python3-venv \
    ros-humble-ackermann-msgs \
    ros-humble-teleop-twist-keyboard \
    ros-humble-rmw-cyclonedds-cpp \
    vim \
    ros-humble-tf-transformations \
    # ros-humble-navigation2 \
    # ros-humble-nav2-bringup \
    && rm -rf /var/lib/apt/lists/*

RUN pip install transforms3d

# you can change the directory name to your own
WORKDIR /root/humble_ws/

# RUN git clone https://github.com/isaac-sim/IsaacSim-ros_workspaces.git && \
#     cp -r IsaacSim-ros_workspaces/humble_ws /root/humble_ws

# Compile ROS packages
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd /root/humble_ws && \
    colcon build && \
    echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc"

# Set environment variables
# ENV ROS_DOMAIN_ID=0 
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Add alias commands
# RUN echo "alias pubtwist='ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r __ns:=/my_robot -r cmd_vel:=/YOUR_ROBOT/twist'" >> /root/.bashrc
