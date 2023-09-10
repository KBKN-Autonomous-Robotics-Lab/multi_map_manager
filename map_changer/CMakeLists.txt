cmake_minimum_required(VERSION 3.0.2)
project(map_changer)


find_package(catkin REQUIRED
  rospy
  std_msgs
  nav_msgs
  std_srvs
)


catkin_package(
  LIBRARIES ${PROJECT_NAME}
)

catkin_install_python(PROGRAMS
  scripts/map_changer.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
