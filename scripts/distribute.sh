#!/bin/bash

BUILD_DIR="/build"
if [ -d "$BUILD_DIR" ]; then
  rm -rf "$BUILD_DIR"
fi

DIST_DIR="/dist"
if [ -d "$DIST_DIR" ]; then
  rm -rf "$DIST_DIR"
fi

# Print a simple string
echo "Distributing"

pyinstaller app_ui.spec
