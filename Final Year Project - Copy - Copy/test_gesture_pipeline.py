#!/usr/bin/env python3
"""
Test gesture detection through the entire pipeline
"""

import logging
import time
import threading

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] %(name)s (%(levelname)s): %(message)s'
)

# Patch each module to log what they're doing
from main import MainController

print("\n" + "="*70)
print("GESTURE DETECTION PIPELINE TEST")
print("="*70)

print("\n1. Creating MainController...")
controller = MainController()
print("   ✓ MainController created")

print("\n2. Starting all managers...")
controller.start()
print("   ✓ All managers started")

print("\n3. Monitoring queue for 5 seconds...")
print("   (Position your hand to make gestures)")
print("-"*70)

start_time = time.time()
actions_detected = []

# Monitor the queue
while time.time() - start_time < 5:
    try:
        # Try to peek at what's in the queue (non-blocking)
        if not controller.queue.empty():
            item = controller.queue.get_nowait()
            action_name, source, details = item
            actions_detected.append((action_name, source))
            print(f"   → Action in queue: {action_name} (from {source})")
            # Put it back for executor to process
            controller.queue.put(item)
    except:
        pass
    time.sleep(0.1)

print("-"*70)

print("\n4. Summary:")
print(f"   Actions detected: {len(actions_detected)}")
for action, source in actions_detected:
    print(f"     - {action} (from {source})")

print("\n5. Stopping...")
controller.stop()
print("   ✓ MainController stopped")

print("\n" + "="*70)
if actions_detected:
    print("✓ SUCCESS: Gestures are being detected!")
else:
    print("✗ ISSUE: No gesture actions detected in 5 seconds")
    print("  Check:")
    print("  - WebCam is working")
    print("  - Your hand is visible to camera")
    print("  - Gestures are stable (hold 2+ frames)")
print("="*70 + "\n")
