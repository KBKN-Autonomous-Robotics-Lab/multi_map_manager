cmake_minimum_required(VERSION 3.8)
project(map_changer)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(nav2_msgs REQUIRED)


ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/map_changer.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch test
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
