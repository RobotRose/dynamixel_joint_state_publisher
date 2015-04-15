cmake_minimum_required(VERSION 2.8.3)
project(dynamixel_joint_state_publisher)

find_package(catkin REQUIRED
	dynamixel_msgs
	rospy
	sensor_msgs
)

catkin_package()
