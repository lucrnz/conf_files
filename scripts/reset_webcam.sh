#!/bin/bash
echo "Resetting webcam..."
sudo modprobe -r uvcvideo 2>/dev/null
sleep 1
sudo modprobe uvcvideo
echo "Done! Go test it"

