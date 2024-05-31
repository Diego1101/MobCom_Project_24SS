# Top level CMake file; required for building a scenario outside the "artery" directory.

# @file    CMakeLists.txt
# @author  Manuel Haerer
# @date    05.11.2021

# Basic project settings.
cmake_minimum_required(VERSION 3.4)
project(MobComV2XPrivacy)

# Use "artery"; include the "scenarios" directory explicitly.
add_subdirectory(artery)
add_subdirectory(scenarios)
