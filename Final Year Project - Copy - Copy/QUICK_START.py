#!/usr/bin/env python3
"""
QUICK START - Running All Three Modules Together
=================================================

This guide will get you started with integrated eye, hand, and voice control.
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║                    QUICK START GUIDE                            ║
║           Eye Tracking + Hand Gesture + Voice Control            ║
╚══════════════════════════════════════════════════════════════════╝

📋 BEFORE YOU START:
═══════════════════════════════════════════════════════════════════

1. Install Dependencies:
   $ pip install -r requirements.txt

2. Verify Imports:
   $ python test_integration.py

3. Check Hardware:
   - Webcam: Connect and test
   - Microphone: Connect and test


🚀 STARTING ALL MODULES (RECOMMENDED):
═══════════════════════════════════════════════════════════════════

Simply run:
   $ python integrator.py

This starts all three modules in parallel with:
  ✓ Eye tracking  
  ✓ Hand gestures
  ✓ Voice commands
  ✓ Unified event bus
  ✓ Automatic conflict resolution


💬 HOW TO USE EACH MODULE:
═══════════════════════════════════════════════════════════════════

1️⃣  EYE TRACKING:
   Look LEFT   → Previous Tab (Ctrl+Shift+Tab)
   Look RIGHT  → Next Tab (Ctrl+Tab)
   Blink 2x    → Next Tab
   Blink 3x    → Show Desktop

2️⃣  HAND GESTURES:
   Index Only         → Move Mouse
   Thumb + Index      → Click
   Thumb + Index ✌️  → OK (copy)
   Index + Middle     → Peace (copy)
   All Fingers Up     → Open Palm
   Fist               → Fist (close)
   Thumb Up           → Thumbs Up
   Thumb Down         → Thumbs Down
   3-Finger Scroll    → Scroll

3️⃣  VOICE COMMANDS:
   "Next tab"         → Next Tab
   "Previous tab"     → Previous Tab
   "New tab"          → New Tab
   "Close tab"        → Close Tab
   "Copy"             → Copy (Ctrl+C)
   "Paste"            → Paste (Ctrl+V)
   "Undo"             → Undo (Ctrl+Z)
   "Screenshot"       → Take Screenshot
   ... and many more!


📊 SYSTEM BEHAVIOR:
═══════════════════════════════════════════════════════════════════

CONFLICTS ARE AUTOMATICALLY RESOLVED:
  • Voice always wins (highest priority)
  • Gesture blocks eye (medium priority)
  • Eye has lowest priority
  
EXAMPLE: If you say "Copy" while looking right and doing a peace sign:
  ✓ Voice "Copy" executes
  ✗ Gesture "Peace" is blocked
  ✗ Eye "Right Gaze" is blocked


⚙️ CONFIGURATION:
═══════════════════════════════════════════════════════════════════

Edit these settings in config.py:

Eye Tracking:
  EYE_CONFIG["gaze_hold_time"] = 0.8      # Time to hold gaze
  EYE_CONFIG["gaze_cooldown"] = 1.2       # Wait between actions
  
Hand Gesture:
  GESTURE_CONFIG["gesture_frames_required"] = 2
  GESTURE_CONFIG["action_cooldown"] = 0.3
  
Voice:
  VOICE_CONFIG["energy_threshold"] = 4000  # Mic sensitivity
  VOICE_CONFIG["command_cooldown"] = 0.5


🔧 TROUBLESHOOTING:
═══════════════════════════════════════════════════════════════════

Webcam not working?
  $ python eye_module.py
  If error: Check another app isn't using it

Microphone not working?
  $ python voice_module.py
  If error: Check system audio settings

Module crashes?
  Enable debug mode in config.py:
  SYSTEM_CONFIG["debug_mode"] = True

Nothing happening?
  $ python test_integration.py
  Check all tests pass


📂 FILE STRUCTURE:
═══════════════════════════════════════════════════════════════════

integrator.py              ← START HERE (main coordinator)
├── eye_module.py          ← Eye tracking (emits events)
├── gesture_module.py      ← Hand gestures (emits events)
├── voice_module.py        ← Voice commands (emits events)
├── event_bus.py           ← Event coordination & conflict resolution
├── action_mapper.py       ← Unified action execution
└── config.py              ← All configuration


📚 NEXT STEPS:
═══════════════════════════════════════════════════════════════════

1. Run integration test:
   $ python test_integration.py

2. Start all modules:
   $ python integrator.py

3. Try each input method:
   - Look in different directions
   - Make hand gestures
   - Speak commands

4. Read detailed guide:
   See: THREE_MODULES_INTEGRATION.md


🎯 EXPECTED OUTPUT:
═══════════════════════════════════════════════════════════════════

[integrator.py] Should show:
  ✓ [EYE] Starting eye tracker...
  ✓ [GESTURE] Starting gesture controller...
  ✓ [VOICE] Starting voice controller...
  ✓ Multi-modal control system initialized

Then you'll see real-time events:
  [EYE] Gaze detected: RIGHT
  [GESTURE] Gesture: pinch
  [VOICE] Command: next_tab


✨ TIPS & TRICKS:
═══════════════════════════════════════════════════════════════════

• Combine inputs smartly:
  - Use eye for quick navigation
  - Use gestures for precise actions
  - Use voice for complex commands

• Adjust sensitivity:
  Edit GESTURE_CONFIG or EYE_CONFIG
  
• Disable unwanted inputs:
  Comment out start_eye_tracker(), etc. in integrator.py

• Custom actions:
  Add to ACTION_MAPPINGS in config.py


🎉 YOU'RE READY!
═══════════════════════════════════════════════════════════════════

Run: python integrator.py

And enjoy integrated multi-modal control!

Questions? Check:
  • THREE_MODULES_INTEGRATION.md (detailed guide)
  • INTEGRATION_GUIDE.md (complete documentation)
  • README.md (project overview)

═══════════════════════════════════════════════════════════════════
""")
