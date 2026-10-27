#!/usr/bin/env python3
"""
Check available camera devices
"""

import cv2

print("\n" + "="*70)
print("AVAILABLE CAMERA DEVICES")
print("="*70)

cameras_found = []
for i in range(5):  # Check first 5 camera indices
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cameras_found.append(i)
            print(f"✓ Camera {i}: Available (Frame size: {frame.shape})")
        else:
            print(f"✗ Camera {i}: Accessible but no frames")
        cap.release()
    else:
        print(f"✗ Camera {i}: Not accessible")

print("="*70)
if len(cameras_found) > 1:
    print(f"✓ Multiple cameras found: {cameras_found}")
    print(f"  Solution: Assign gesture to camera {cameras_found[1]}")
elif len(cameras_found) == 1:
    print(f"✗ Only one camera found: {cameras_found[0]}")
    print(f"  Issue: Both eye and gesture modules cannot use the same camera simultaneously")
    print(f"  Solution: Run only one module at a time, or modify code to share camera feed")
else:
    print("✗ No cameras found!")
print("="*70 + "\n")
