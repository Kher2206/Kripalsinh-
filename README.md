Terminal -1

cd ~/ros2_ws
colcon build --packages-select serial_node
source install/setup.bash

Terminal-2 

source /opt/ros/iron/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run serial_node serial_node_ACM0

Terminal-3

source /opt/ros/iron/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic info /kher_serial_ACM0 --verbose
ros2 topic echo /kher_serial_ACM0

Terminal-4

source /opt/ros/iron/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic pub --once /kher_serial_ACM0 std_msgs/msg/String "{data: 'ffff'}"
