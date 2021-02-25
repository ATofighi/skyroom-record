#!/bin/bash

Xvfb :99 -screen 0 1368x885x24 &

touch ~/.Xauthority

flask run -h 0.0.0.0 -p 5000 & 

sleep 5
