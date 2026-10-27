#!/usr/bin/env python3
"""
Direct gesture detection test - standalone
"""

import time
from hand_gesture_control import HandGestureController

print("\n" + "="*70)
print("STANDALONE GESTURE DETECTION TEST")
print("="*70)

print("Testing gesture detection on camera 1...")
print("(Show your hand and make gestures)")
print("(Press Q in the window to quit)")
print("-"*70)

try:
    controller = HandGestureController(camera_index=1)
    print("✓ Gesture controller initialized with camera 1")
    
    # Enable debug logging to see gesture detection
    controller.debug_logging = True
    
    # Run for 10 seconds or until Q is pressed
    print("Running gesture detection...")
    controller.run()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("-"*70)
print("=" *70 + "\n")
