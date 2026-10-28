cmake_minimum_required(VERSION 3.8)
project(navis_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch maps worlds scripts DESTINATION share/${PROJECT_NAME})

ament_package()
