# INTEGRATION GUIDE - Three Modules Working Together

## Overview

You now have **three fully integrated input modules** that work together seamlessly:

1. **Eye Tracking Module** (`eye_module.py`) - Iris tracking & gaze detection
2. **Hand Gesture Module** (`gesture_module.py`) - Hand pose & gesture recognition  
3. **Voice Control Module** (`voice_module.py`) - Speech recognition & command parsing

All three communicate through a **unified event bus** with automatic conflict resolution.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              USER INPUT MODALITIES                       │
├──────────────┬──────────────┬──────────────┐
│              │              │              │
│   EYE        │   GESTURE    │   VOICE      │
│  TRACKING    │  CONTROL     │  COMMANDS    │
│              │              │              │
└──────┬───────┴──────┬───────┴──────┬───────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
       ┌─────────────────────────────┐
       │   EVENT BUS (event_bus.py)  │
       │  - Thread-safe coordination │
       │  - Priority-based conflict  │
       │    resolution               │
       │  - Unified event handling   │
       └─────────────┬───────────────┘
                      │
                      ▼
       ┌─────────────────────────────┐
       │ ACTION MAPPER (action_mapper│
       │  Unified action execution   │
       └─────────────┬───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  SYSTEM       │
              │  ACTIONS      │
              │  (pyautogui)  │
              └───────────────┘
```

---

## How to Use

### Option 1: Run All Modules Together (Recommended)

```bash
python integrator.py
```

This starts all three modules in parallel with automatic coordination.

### Option 2: Run Individual Modules

```bash
# Terminal 1: Eye tracking
python eye_module.py

# Terminal 2: Hand gesture (separate terminal)
python gesture_module.py

# Terminal 3: Voice control (separate terminal)
python voice_module.py
```

### Option 3: Use the Original Files (Legacy)

If you prefer the original standalone files:

```bash
python eye.py          # Standalone eye tracking
python hand_gesture_control.py  # Standalone gesture control
python voice_control.py  # Standalone voice control
```

**⚠️ Note**: Original files execute actions directly. Multiple modules running simultaneously may cause conflicts.

---

## Module Details

### Eye Module (`eye_module.py`)

**Detects:**
- Gaze direction (LEFT, RIGHT, CENTER)
- Blink patterns (single, double, triple blinks)
- Eye aspect ratio (EAR) for blink detection

**Events emitted:**
- `EYE_GAZE_LEFT` → Mapped to: `previous_tab`
- `EYE_GAZE_RIGHT` → Mapped to: `next_tab`
- `EYE_DOUBLE_BLINK` → Mapped to: `next_tab`
- `EYE_TRIPLE_BLINK` → Mapped to: `show_desktop`

**Configuration** (`config.py`):
```python
EYE_CONFIG = {
    "gaze_hold_time": 0.8,        # Hold gaze for action
    "gaze_cooldown": 1.2,         # Wait before next action
    "blink_threshold": 0.25,      # Eye aspect ratio threshold
    ...
}
```

---

### Hand Gesture Module (`gesture_module.py`)

**Detects:**
- Pinch gesture (thumb + index)
- OK gesture (pinch + middle up)
- Peace sign (index + middle)
- Open palm (all fingers up)
- Fist (all fingers down)
- Thumbs up/down
- Scroll gestures (three finger combinations)
- Cursor movement (index finger only)

**Events emitted:**
- `GESTURE_PINCH` → Mapped to: `click`
- `GESTURE_PEACE` → Mapped to: `copy`
- `GESTURE_PAUSE` → Toggles system pause

**Configuration** (`config.py`):
```python
GESTURE_CONFIG = {
    "gesture_frames_required": 2,  # Frames needed to confirm
    "action_cooldown": 0.3,        # Cooldown between actions
    "pause_cooldown": 0.8,         # Cooldown for pause toggle
    ...
}
```

---

### Voice Module (`voice_module.py`)

**Detects:**
- Natural language commands via speech recognition
- Intent mapping with keyword matching
- System voice feedback

**Supported intents:**
- Navigation: `next_tab`, `previous_tab`, `new_tab`, `close_tab`
- Window: `close_window`, `minimize`, `maximize`
- Text: `copy`, `paste`, `cut`, `undo`, `redo`, `select_all`
- Media: `play_pause`, `mute`, `volume_up`, `volume_down`
- System: `screenshot`, `escape`, `enter`

**Events emitted:**
- `VOICE_COMMAND` → Intent-based action

**Configuration** (`config.py`):
```python
VOICE_CONFIG = {
    "energy_threshold": 4000,      # Microphone sensitivity
    "command_cooldown": 0.5,       # Cooldown between commands
    "speech_rate": 170,            # TTS speech speed
    ...
}
```

---

## Event Bus & Conflict Resolution

### How Conflicts Are Resolved

The **event bus** automatically handles conflicts when multiple inputs occur simultaneously:

**Priority Order:**
1. **Voice** (Highest) - Always processed
2. **Gesture** (Medium) - Blocked if voice just executed
3. **Eye** (Lowest) - Blocked if gesture is active

**Example Scenarios:**

| Situation | Action |
|-----------|--------|
| Voice + Eye at same time | Voice executes, eye is blocked |
| Gesture + Eye at same time | Gesture executes, eye is blocked |
| Voice + Gesture at same time | Voice executes, gesture is blocked |
| All three at same time | Voice wins, others blocked |

### Cooldowns & Debouncing

Each modality has individual cooldowns to prevent accidental repetition:

```python
EYE: gaze_cooldown = 1.2 seconds
GESTURE: action_cooldown = 0.3 seconds
VOICE: command_cooldown = 0.5 seconds
```

---

## Testing

### Quick Test

```bash
python test_integration.py
```

This runs all checks without requiring:
- Webcam
- Microphone
- Any actual system actions

**Output:**
```
✓ All three modules can be imported
✓ Event bus is functional
✓ Configuration system is in place
✓ Event flow works end-to-end
```

---

## Configuration

All settings are in [`config.py`](config.py):

```python
# Eye tracking settings
EYE_CONFIG = { ... }

# Hand gesture settings
GESTURE_CONFIG = { ... }

# Voice command settings
VOICE_CONFIG = { ... }

# System-wide settings
SYSTEM_CONFIG = { ... }
```

**To customize:**
1. Open `config.py`
2. Edit the relevant `*_CONFIG` dictionary
3. Restart the application

---

## Troubleshooting

### Issue: "Cannot open webcam"

```
[EYE] ERROR: Cannot open webcam!
[GESTURE] ERROR: Cannot open webcam!
```

**Solution:**
- Check if webcam is being used by another app
- Try: `python eye_module.py` alone
- Check webcam permissions

### Issue: "Microphone init failed"

```
[VOICE] WARNING: Microphone init failed: ...
```

**Solution:**
- Check microphone is connected
- Check system microphone permissions
- Try: `python -m pip install --upgrade pyaudio`

### Issue: "AttributeError: module 'X' has no attribute 'Y'"

**Solution:**
- Run: `pip install -r requirements.txt`
- Delete `__pycache__/` folder
- Restart application

### Issue: Actions execute multiple times

**Solution:**
- Increase cooldown values in `config.py`
- Check event bus queue size in logs
- Restart application

---

## Files Overview

| File | Purpose |
|------|---------|
| `integrator.py` | Main orchestrator (start this) |
| `event_bus.py` | Central event coordination |
| `action_mapper.py` | Unified action execution |
| `eye_module.py` | **Refactored** eye tracking |
| `gesture_module.py` | **Refactored** hand gestures |
| `voice_module.py` | **Refactored** voice control |
| `config.py` | All configuration settings |
| `test_integration.py` | Integration tests |
| --- | --- |
| `eye.py` | Legacy standalone eye tracking |
| `hand_gesture_control.py` | Legacy standalone gestures |
| `voice_control.py` | Legacy standalone voice |

---

## Performance Tips

1. **Reduce camera resolution** if CPU usage is high:
   ```python
   EYE_CONFIG["camera_width"] = 640  # instead of 1280
   GESTURE_CONFIG["camera_width"] = 640
   ```

2. **Increase gesture confirmation frames** for stability:
   ```python
   GESTURE_CONFIG["gesture_frames_required"] = 5  # instead of 2
   ```

3. **Increase cooldown values** for slower systems:
   ```python
   EYE_CONFIG["gaze_cooldown"] = 2.0  # instead of 1.2
   ```

4. **Disable HUD** for better performance:
   ```python
   SYSTEM_CONFIG["hud_enabled"] = False
   ```

---

## Development Notes

### Adding New Actions

1. Add to `ACTION_MAPPINGS` in `config.py`:
   ```python
   "my_action": ("hotkey", ("ctrl", "alt", "m")),
   ```

2. Reference in module configs:
   ```python
   EYE_CONFIG["actions"]["my_event"] = "my_action"
   ```

### Adding New Gestures

1. Detect in `gesture_module.py`:
   ```python
   if condition:
       emit_event(EventType.GESTURE_DETECTED, "gesture",
                 {"gesture": "my_gesture"}, priority=2)
   ```

2. Map in `action_mapper.py`:
   ```python
   if gesture == "my_gesture":
       return "my_action"
   ```

### Adding New Voice Commands

Update `local_intent()` in `voice_module.py`:
```python
"my_intent": ["my phrase", "alternative phrase"],
```

---

## Support & Issues

If modules aren't working together:

1. **Run test**: `python test_integration.py`
2. **Enable debug mode** in `config.py`:
   ```python
   SYSTEM_CONFIG["debug_mode"] = True
   ```
3. **Check logs** in `action_log.txt`
4. **Read**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

## Summary

✅ **All three modules now work together correctly**

- Event bus prevents conflicts
- Automatic priority resolution
- Thread-safe coordination
- Unified action execution
- Configurable behavior

**Start with:** `python integrator.py`

Enjoy integrated multi-modal control! 🎉
