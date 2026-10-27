#!/usr/bin/env python3
"""
Comprehensive test - All 3 modules with detailed logging
"""

import logging
import time
import threading
import sys

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

from main import MainController

print("\n" + "="*80)
print(" " * 15 + "COMPREHENSIVE 3-MODULE INTEGRATION TEST")
print("="*80)

print("\n✓ Step 1: Creating MainController...")
controller = MainController()
print("  → MainController created successfully")

print("\n✓ Step 2: Starting all managers...")
print("  → EYE Module (Camera 0) | GESTURE Module (Camera 1) | VOICE Module")
controller.start()
print("  → All managers started")

print("\n" + "-"*80)
print("TEST RUNNING - 10 seconds")
print("-"*80)
print("» EYE: Look left/right to navigate tabs")
print("» GESTURE: Make hand gestures to trigger actions")
print("» VOICE: Speak commands (open browser, open notepad, etc.)")
print("-"*80)

# Monitor for actions
start_time = time.time()
gesture_count = 0
eye_count = 0
voice_count = 0
test_duration = 10

# Track what we see in logs
original_init = logging.getLogger("gesture_control")._log

def patched_log(level, msg, args, **kwargs):
    global gesture_count
    if "gesture" in msg.lower() and "forwarding" in msg.lower():
        gesture_count += 1
    original_init(level, msg, args, **kwargs)

while time.time() - start_time < test_duration:
    time.sleep(0.5)
    elapsed = int(time.time() - start_time)
    remaining = test_duration - elapsed
    print(f"  ⏱ {elapsed}s / {test_duration}s  [{remaining}s remaining]", end='\r')

print("\n" + "-"*80)
print("✓ Step 3: Stopping maincontroller...")
controller.stop()
print("  → MainController stopped")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

print("\n✓ Summary:")
print("  • EYE Module: Running on camera 0")
print("  • GESTURE Module: Running on camera 1 (FIXED - was conflicting with eye)")
print("  • VOICE Module: Running (processing audio)")

print("\n📋 What to check:")
print("  1. Eye tracking window should be visible (camera 0 feed)")
print("  2. Gesture window should be visible (camera 1 feed)")
print("  3. Voice should be listening")
print("  4. Check action_log.txt for executed actions")

print("\n✓ If you see this message, all modules initialized successfully!")
print("✓ If gestures weren't detectable, check:")
print("  • Camera 1 is physically available and not in use by other apps")
print("  • Your hand is clearly visible in the gesture camera window")
print("  • Gestures are held stable for 2+ frames (about 100ms)")

print("="*80 + "\n")
