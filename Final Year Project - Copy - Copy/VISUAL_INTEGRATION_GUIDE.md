# 📊 VISUAL GUIDE - How Your Three Modules Work Together

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     YOUR COMPUTER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                      │
│  │ WEBCAM   │    │ WEBCAM   │    │ MIC      │                      │
│  │ (Eye)    │    │(Hand)    │    │(Voice)   │                      │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘                      │
│       │               │               │                             │
│       └───────────────┼───────────────┘                             │
│                       │                                              │
│                       ▼                                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  THREE MODULES RUNNING IN PARALLEL                           │  │
│  │  ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐   │  │
│  │  │  EYE TRACKING   │ │ HAND GESTURE │ │ VOICE CONTROL   │   │  │
│  │  │ (eye_module.py) │ │gesture_mod.py│ │voice_module.py  │   │  │
│  │  └────────┬────────┘ └───────┬──────┘ └────────┬────────┘   │  │
│  │           │                  │                 │             │  │
│  │  Gaze:    │  Gesture:        │  Intent:       │             │  │
│  │  LEFT     │  PINCH           │  "next tab"    │             │  │
│  │  RIGHT    │  PEACE           │  "copy"        │             │  │
│  │  CENTER   │  SCROLL          │  "paste"       │             │  │
│  │  BLINK    │  THUMBS_UP       │  "undo"        │             │  │
│  │           │  FIST            │  etc...        │             │  │
│  │           │                  │                │             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                       │                                              │
│                       ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ EVENT BUS (event_bus.py)                                    │   │
│  │                                                              │   │
│  │ All events go here:                                        │   │
│  │ • EYE_GAZE_LEFT (priority: 1)                             │   │
│  │ • EYE_DOUBLE_BLINK (priority: 1)                          │   │
│  │ • GESTURE_PINCH (priority: 2)                             │   │
│  │ • GESTURE_PEACE (priority: 2)                             │   │
│  │ • VOICE_COMMAND (priority: 3) ← HIGHEST!                 │   │
│  │                                                              │   │
│  │ CONFLICT RESOLUTION:                                       │   │
│  │ If voice happens → block gesture and eye                  │   │
│  │ If gesture happens → block eye                            │   │
│  │ Eye can run freely otherwise                              │   │
│  └────────────┬─────────────────────────────────────────────┘    │
│               │                                                    │
│               ▼                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ ACTION MAPPER (action_mapper.py)                         │    │
│  │                                                          │    │
│  │ Converts events to actions:                             │    │
│  │ • "next_tab" → Ctrl+Tab                                 │    │
│  │ • "copy" → Ctrl+C                                       │    │
│  │ • "paste" → Ctrl+V                                      │    │
│  │ • "click" → Mouse click                                 │    │
│  │ • etc...                                                │    │
│  └──────────────┬───────────────────────────────────────────┘    │
│                 │                                                  │
│                 ▼                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ SYSTEM ACTIONS (pyautogui)                               │    │
│  │ • Keyboard commands                                      │    │
│  │ • Mouse movements                                        │    │
│  │ • Window management                                      │    │
│  │ • System control                                         │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Event Flow Timeline Example

### Scenario: User speaking "Copy" while making peace sign

```
TIME    EYE MODULE              GESTURE MODULE         VOICE MODULE
─────────────────────────────────────────────────────────────────────

0.0s                                                   🎤 "Copy" detected
       |                        |                       |
0.05s  |                        👉 Peace sign detected  |
       |                        |                       |
0.08s  👀 Looking right          |                       |
       |                        |                       |
       ▼                        ▼                       ▼
       
EVENT BUS RECEIVES:
  1. EYE_GAZE_RIGHT    (pri: 1) @ 0.08s
  2. GESTURE_PEACE     (pri: 2) @ 0.05s
  3. VOICE_COMMAND     (pri: 3) @ 0.0s

RESOLUTION:
  ✓ Voice (pri:3) WINS      → Execute "copy" (Ctrl+C)
  ✗ Gesture (pri:2) BLOCKED → Queued/dropped
  ✗ Eye (pri:1) BLOCKED     → Dropped

RESULT: Only "Copy" executes - no conflicts!
```

---

## Module Communication Flow

```
┌─────────────────┐
│ EYE MODULE      │ Detects gaze, blinks
└────────┬────────┘
         │
         │ emit_event(EYE_GAZE_LEFT, ...)
         │
         ▼
┌──────────────────────────────────────┐
│ EVENT BUS                            │
│ - Receives events from all modules   │
│ - Applies priority rules             │
│ - Resolves conflicts                 │
│ - Forwards to action mapper          │
└────────┬─────────────────────────────┘
         │ action: "previous_tab"
         ▼
┌──────────────────────────────────────┐
│ ACTION MAPPER                        │
│ - Maps action to system command      │
│ - Executes via pyautogui             │
│ - Records in action log              │
└──────────────────────────────────────┘


┌─────────────────┐
│ GESTURE MODULE  │ Detects hand poses
└────────┬────────┘
         │ emit_event(GESTURE_PINCH, ...)
         │
         ▼
┌──────────────────────────────────────┐
│ EVENT BUS (same as above)            │
└────────┬─────────────────────────────┘
         │ action: "click"
         ▼
┌──────────────────────────────────────┐
│ ACTION MAPPER (same as above)        │
└──────────────────────────────────────┘


┌─────────────────┐
│ VOICE MODULE    │ Detects speech
└────────┬────────┘
         │ emit_event(VOICE_COMMAND, ...)
         │
         ▼
┌──────────────────────────────────────┐
│ EVENT BUS (same as above)            │
└────────┬─────────────────────────────┘
         │ action: "next_tab"
         ▼
┌──────────────────────────────────────┐
│ ACTION MAPPER (same as above)        │
└──────────────────────────────────────┘
```

---

## Priority System

```
                        VOICE
                          ↑ (Priority: 3)
                          │ Highest ⭐
                          │
                      ┌───┴────┐
                      │         │
                   GESTURE   SYSTEM
                   (Pri: 2)  (Pri: 0)
                      │
                      │
                      └────┬────┐
                           │    │
                          EYE   │
                      (Pri: 1)  │
                         ▲      │
                         │      │
                    Lowest │    Ignored
                           └────┴─


CONFLICT RESOLUTION RULES:
═════════════════════════════════════════════════════════════

1. If VOICE_COMMAND is active:
   ✓ VOICE executes
   ✗ GESTURE blocked
   ✗ EYE blocked

2. If GESTURE is active (and no voice):
   ✓ GESTURE executes
   ✗ EYE blocked

3. If only EYE:
   ✓ EYE executes

4. Multiple voices/gestures/eyes:
   Last one in queue wins (FIFO)
   Others are blocked by cooldown
```

---

## State Transitions

```
SYSTEM STATE MACHINE:

                    ┌──────────────┐
                    │   RUNNING    │
                    │ All modules  │
                    │ active       │
                    └──────┬───────┘
                           │
                    Pause gesture
                           │
                           ▼
                    ┌──────────────┐
                    │   PAUSED     │
                    │ Voice only   │
                    │ (other blocked)
                    └──────┬───────┘
                           │
                    Pause gesture again
                           │
                           ▼
                    ┌──────────────┐
                    │   RUNNING    │
                    │ (back to normal)
                    └──────────────┘


PAUSE GESTURE: Fist hold for 1.5+ seconds
→ Toggles system between RUNNING and PAUSED states
```

---

## Cooldown Timeline

```
ACTION COOLDOWN PREVENTS RAPID REPEATS:

EYE GAZE ACTION:
─────────────────────────────────────────
0.0s    Look RIGHT → "next_tab" executes
        ✓ Cooldown starts (1.2 seconds)
        
0.1s    Still looking RIGHT
        ✗ Event blocked (within cooldown)
        
0.5s    Still looking RIGHT
        ✗ Event blocked (within cooldown)
        
1.2s    Cooldown expires
        ✓ Ready for next action
        
1.3s    Still looking RIGHT
        ✓ "next_tab" executes again


GESTURE ACTION:
─────────────────────────────────────────
0.0s    Pinch detected → "click" executes
        ✓ Cooldown starts (0.3 seconds)
        
0.1s    Still pinching
        ✗ Event blocked (within cooldown)
        
0.3s    Cooldown expires
        ✓ Ready for next pinch
        
0.4s    Pinch again
        ✓ "click" executes again


VOICE COMMAND:
─────────────────────────────────────────
0.0s    "next tab" → executes
        ✓ Cooldown starts (0.5 seconds)
        
0.2s    "copy"
        ✗ Blocked (within cooldown)
        
0.5s    Cooldown expires
        ✓ Ready for next command
        
0.6s    "paste"
        ✓ Executes
```

---

## Real-World Usage Examples

### Example 1: Browsing with Multiple Inputs
```
Action: I want to copy current URL, then move to next tab

Solution:
─────────────────────────────────────────
1. Say "Copy" 
   → Voice module detects
   → EVENT BUS: VOICE_COMMAND (pri:3)
   → ACTION_MAPPER: copy (Ctrl+C)
   → ✓ URL copied to clipboard

2. Make peace sign 
   → Gesture module detects
   → Wait for voice cooldown (0.5s)
   → EVENT BUS: GESTURE_PEACE (pri:2)
   → ACTION_MAPPER: copy again (ignored, already copied)
   
   Alternative: Look RIGHT instead
   → Eye module detects
   → Wait for cooldown (1.2s)
   → EVENT BUS: EYE_GAZE_RIGHT (pri:1)
   → ACTION_MAPPER: next_tab (Ctrl+Tab)
   → ✓ Moved to next tab

3. Look LEFT (to go back)
   → EYE_GAZE_LEFT emitted
   → Wait for cooldown
   → ✓ Previous tab loaded
```

### Example 2: Gaming Controls
```
Action: Quick actions in game

Solution:
─────────────────────────────────────────
1. Say "Jump"     (if mapped to spacebar)
   → ✓ Executes immediately

2. While jumping, make pinch
   → Gesture blocked (voice just executed)
   → Prevented accidental action

3. After voice cooldown (0.5s), gesture works
   → ✓ Pinch executes next action

4. Eye tracking provides passive info
   → Doesn't interfere with active actions
```

### Example 3: Document Editing
```
Action: Edit document with mixed inputs

Solution:
─────────────────────────────────────────
1. Voice: "Select all"     → Ctrl+A executed
2. Voice: "Copy"           → Ctrl+C executed (0.5s cooldown enforced)
3. Gesture: Peace sign     → Blocked (within voice cooldown)
4. Wait 0.5s, gesture works
5. Eye look RIGHT          → Next page (after gesture cooldown)
6. Eye look LEFT           → Previous (after 1.2s eye cooldown)
```

---

## System Resources

```
TYPICAL RESOURCE USAGE:

EYE TRACKING:
  CPU: 15-25% (depends on resolution)
  Memory: 150-200 MB
  Latency: 30-50ms

HAND GESTURE:
  CPU: 20-30% (MediaPipe hand tracking)
  Memory: 200-250 MB
  Latency: 40-60ms

VOICE CONTROL:
  CPU: 10-15% (listening)
  Memory: 100-150 MB
  Latency: 2-5s (speech recognition)

EVENT BUS:
  CPU: <1%
  Memory: <10 MB
  Latency: <1ms

TOTAL:
  CPU: 45-70% on modern 4-core system
  Memory: 500-700 MB
  Overall latency: ~100-150ms end-to-end
```

---

## Thread Architecture

```
MAIN PROCESS
│
├─ Thread 1: EYE_TRACKER
│  └─ Captures webcam frames
│  └─ Detects gaze & blinks
│  └─ Emits eye events
│
├─ Thread 2: GESTURE_CONTROLLER
│  └─ Captures webcam frames
│  └─ Detects hand poses
│  └─ Emits gesture events
│
├─ Thread 3: VOICE_CONTROLLER
│  └─ Listens to microphone
│  └─ Recognizes speech
│  └─ Emits voice events
│
├─ Thread 4: EVENT_BUS_PROCESSOR
│  └─ Receives events (thread-safe queue)
│  └─ Resolves conflicts
│  └─ Routes to action mapper
│
├─ Thread 5: ACTION_EXECUTOR
│  └─ Executes pyautogui commands
│  └─ Records action log
│  └─ Returns status
│
└─ MAIN THREAD (HUD/Display)
   └─ Shows real-time visualization
   └─ Displays status & statistics
```

---

## Quick Decision Tree

```
WHICH INPUT SHOULD I USE?

                    START
                      │
              ┌────────┴────────┐
              │                 │
         Quick action?      Need precision?
              │                 │
              NO               YES
              │                 │
              ▼                 │
         Try VOICE         Need free hands?
         (fastest)               │
              ▼          ┌────────┴────────┐
         "Next tab"      │                 │
         "Copy"          YES              NO
         "Paste"         │                 │
         etc...          ▼                 │
                    Try EYE TRACK    Try GESTURE
                    (passive,       (precise,
                     hands free)     gesture-based)
                          │                 │
                          └────────┬────────┘
                                   │
                          ┌────────┴─────────┐
                          │                  │
                    Combine them!    Use cooldowns
                    Priority handles   to prevent
                    conflicts         conflicts
```

---

## Summary

```
YOUR SYSTEM:

  ✅ Eye Module         → Gaze & blink detection
  ✅ Gesture Module     → Hand pose & gesture recognition
  ✅ Voice Module       → Speech recognition & intent parsing
  ✅ Event Bus          → Thread-safe coordination
  ✅ Action Mapper      → Unified action execution
  
  🎯 Result: Seamless multi-modal control with automatic conflict resolution!
  
  🚀 Start with: python integrator.py
```

---

*This visual guide explains how your three modules work together. For detailed information, see THREE_MODULES_INTEGRATION.md*
