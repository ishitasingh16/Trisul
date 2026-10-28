cmake_minimum_required(VERSION 3.8)
project(navis_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch urdf worlds protos
  DESTINATION share/${PROJECT_NAME}
)

install(FILES SENSOR_CONTRACT.md DESTINATION share/${PROJECT_NAME})

ament_package()
