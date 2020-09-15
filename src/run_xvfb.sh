#!/bin/bash

Xvfb :99 -screen 0 1920x1197x24 &

touch ~/.Xauthority

python3 screenshot.py & 