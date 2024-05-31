# CMake file for scenarios; required for building all present projects.

# @file    CMakeLists.txt
# @author  Manuel Haerer, Marek Parucha
# @date    09.01.2022

# Get all subdirectories and files.
file(GLOB subdirs RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/*)

# Each subdirectory is expected to represent a scenario.
FOREACH (subdir ${subdirs})
	IF (IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${subdir})
		add_subdirectory(${subdir})
	ENDIF()
ENDFOREACH()
