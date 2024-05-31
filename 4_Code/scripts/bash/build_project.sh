#!/bin/bash

# Shell script to invoke CMake to build the complete project.

# @author  Manuel Haerer (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    25.11.2022

# Check if ninja is installed
echo "Ninja version: $(ninja --version)"
EXIT_STATUS="$( echo $? )"

# Handle ninja not installed.
if [ "$EXIT_STATUS" -ne 0 ]; then
	echo "Ninja is not installed. Please install using: sudo apt-get install ninja-build"
	exit "$EXIT_STATUS"
fi

# Save the current working directory.
START_DIR="$( pwd )"

# Get the current directory of the script; change to the code directory.
# It is expected that this script resides in ".../4_Code/scripts/bash/".
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/../.."

# If the debug directory does not exist, create it.
mkdir -p build

# Setup CMake...
cd "./build"

# Build
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release ..        # Change to Debug if needed
EXIT_STATUS="$( echo $? )"

# Handle CMake error.
if [ "$EXIT_STATUS" -ne 0 ]; then
	echo "CMake setup command failed. Refer to the CMake error message for details."
	cd "$START_DIR"
	exit "$EXIT_STATUS"
fi

# Build "artery" (and the scenarios)...
ninja
EXIT_STATUS="$( echo $? )"

# Handle CMake error.
if [ "$EXIT_STATUS" -ne 0 ]; then
	echo "Ninja build command failed. Refer to the Ninja error message for details."
	cd "$START_DIR"
	exit "$EXIT_STATUS"
fi

# Make runner script runnable.
cd "./artery"
chmod +x "./run_artery.sh"

# Handle chmod error.
if [ "$EXIT_STATUS" -ne 0 ]; then
	echo "Failed to make the runner script runnable."
	cd "$START_DIR"
	exit "$EXIT_STATUS"
fi

cd "$START_DIR"
exit 0
