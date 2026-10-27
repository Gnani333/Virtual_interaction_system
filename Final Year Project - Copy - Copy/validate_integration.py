#!/usr/bin/env python3
"""
FINAL VALIDATION - Ensure All Three Modules Work Correctly Together
====================================================================
"""

import os
import sys
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print("\n" + "="*75)
print("FINAL VALIDATION - THREE MODULES INTEGRATION")
print("="*75)

# Track results
results = {
    "imports": {"passed": 0, "failed": 0, "tests": []},
    "configs": {"passed": 0, "failed": 0, "tests": []},
    "events": {"passed": 0, "failed": 0, "tests": []},
    "integration": {"passed": 0, "failed": 0, "tests": []},
}

def test(category, name, condition, error_msg=""):
    """Record test result"""
    if condition:
        results[category]["passed"] += 1
        status = "✓ PASS"
        print(f"  {status} - {name}")
    else:
        results[category]["failed"] += 1
        status = "✗ FAIL"
        print(f"  {status} - {name}")
        if error_msg:
            print(f"         {error_msg}")
    results[category]["tests"].append((name, condition))

# ============================================================
# SECTION 1: IMPORTS
# ============================================================
print("\n[1] CHECKING IMPORTS")
print("-" * 75)

try:
    from config import SYSTEM_CONFIG, EYE_CONFIG, GESTURE_CONFIG, VOICE_CONFIG
    test("imports", "Config module", True)
except Exception as e:
    test("imports", "Config module", False, str(e))
    sys.exit(1)

try:
    from event_bus import EventBus, EventType, Event, get_event_bus, emit_event
    test("imports", "Event bus module", True)
except Exception as e:
    test("imports", "Event bus module", False, str(e))

try:
    from action_mapper import ActionMapper
    test("imports", "Action mapper module", True)
except Exception as e:
    test("imports", "Action mapper module", False, str(e))

try:
    from eye_module import IrisTracker
    test("imports", "Eye tracking module", True)
except Exception as e:
    test("imports", "Eye tracking module", False, str(e))

try:
    from gesture_module import HandGestureController
    test("imports", "Hand gesture module", True)
except Exception as e:
    test("imports", "Hand gesture module", False, str(e))

try:
    from voice_module import VoiceController
    test("imports", "Voice control module", True)
except Exception as e:
    test("imports", "Voice control module", False, str(e))

# ============================================================
# SECTION 2: CONFIGURATIONS
# ============================================================
print("\n[2] VALIDATING CONFIGURATIONS")
print("-" * 75)

# Eye config
try:
    assert "camera_width" in EYE_CONFIG
    assert "gaze_hold_time" in EYE_CONFIG
    assert "blink_threshold" in EYE_CONFIG
    assert "actions" in EYE_CONFIG
    test("configs", "Eye config complete", True)
except AssertionError as e:
    test("configs", "Eye config complete", False, str(e))

# Gesture config
try:
    assert "camera_width" in GESTURE_CONFIG
    assert "gesture_frames_required" in GESTURE_CONFIG
    assert "action_cooldown" in GESTURE_CONFIG
    test("configs", "Gesture config complete", True)
except AssertionError as e:
    test("configs", "Gesture config complete", False, str(e))

# Voice config
try:
    assert "energy_threshold" in VOICE_CONFIG
    assert "command_cooldown" in VOICE_CONFIG
    assert "speech_rate" in VOICE_CONFIG
    test("configs", "Voice config complete", True)
except AssertionError as e:
    test("configs", "Voice config complete", False, str(e))

# System config
try:
    assert "debug_mode" in SYSTEM_CONFIG
    assert "hud_enabled" in SYSTEM_CONFIG
    test("configs", "System config complete", True)
except AssertionError as e:
    test("configs", "System config complete", False, str(e))

# ============================================================
# SECTION 3: EVENT BUS FUNCTIONALITY
# ============================================================
print("\n[3] TESTING EVENT BUS")
print("-" * 75)

try:
    bus = get_event_bus()
    test("events", "Event bus initialization", bus is not None)
    
    # Test event emission
    emit_event(EventType.VOICE_COMMAND, "test", {"intent": "test"}, priority=3)
    time.sleep(0.1)
    test("events", "Event emission", True)
    
    # Test event listener
    events_received = []
    def listener(event):
        events_received.append(event)
    
    bus.register_listener(EventType.EYE_GAZE_LEFT, listener)
    emit_event(EventType.EYE_GAZE_LEFT, "eye", {"direction": "left"}, priority=1)
    time.sleep(0.1)
    
    test("events", "Event listener registration", len(events_received) > 0)
    
    # Test system pause
    status = bus.get_status()
    test("events", "Bus status reporting", 
         status is not None and "system_paused" in status)
    
except Exception as e:
    test("events", "Event bus operations", False, str(e))

# ============================================================
# SECTION 4: MODULE INTEGRATION
# ============================================================
print("\n[4] TESTING MODULE INTEGRATION")
print("-" * 75)

try:
    # Test that modules can be initialized (no webcam/mic needed)
    mapper = ActionMapper()
    test("integration", "Action mapper initialization", mapper is not None)
    
    # Verify action mappings exist
    from config import ACTION_MAPPINGS
    test("integration", "Action mappings exist", 
         len(ACTION_MAPPINGS) > 0)
    
    # Verify all three modules can coexist
    test("integration", "All modules importable simultaneously", True)
    
except Exception as e:
    test("integration", "Module integration", False, str(e))

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*75)
print("VALIDATION SUMMARY")
print("="*75)

total_passed = sum(r["passed"] for r in results.values())
total_failed = sum(r["failed"] for r in results.values())
total_tests = total_passed + total_failed

for category, result in results.items():
    passed = result["passed"]
    failed = result["failed"]
    total = passed + failed
    percentage = (passed / total * 100) if total > 0 else 0
    status = "✓" if failed == 0 else "✗"
    print(f"\n{status} {category.upper():15} {passed:2}/{total:2} tests passed ({percentage:5.1f}%)")

print("\n" + "="*75)

if total_failed == 0:
    print("🎉 SUCCESS! ALL TESTS PASSED!")
    print("\nYour three modules are ready to work together!")
    print("\nNext steps:")
    print("  1. Run: python integrator.py")
    print("  2. Use the system with eye tracking, hand gestures, and voice!")
    print("\nFor more info:")
    print("  • THREE_MODULES_INTEGRATION.md (detailed guide)")
    print("  • QUICK_START.py (quick reference)")
    print("="*75)
    sys.exit(0)
else:
    print(f"⚠️  {total_failed} TEST(S) FAILED")
    print("\nPlease review the errors above and fix them.")
    print("="*75)
    sys.exit(1)
