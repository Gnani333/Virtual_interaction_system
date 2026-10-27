# Project Structure

This project is intentionally kept mostly flat so the existing imports keep working, but the runtime is organized around one entrypoint and one controller.

## Runtime Flow

```text
main.py
└─ main_controller.MainController
   ├─ camera_manager.get_shared_camera()
   ├─ gesture_control.GestureManager
   ├─ eye_control.EyeManager
   ├─ voice_control_wrapper.VoiceManager
   ├─ unified_display.UnifiedDisplay
   └─ system_actions.SystemActions
```

## Important Files

- `main.py` - thin entrypoint that starts the app
- `main_controller.py` - orchestrates camera, input modules, queue, and cleanup
- `camera_manager.py` - only shared camera owner
- `unified_display.py` - single OpenCV window and combined frame rendering
- `gesture_control.py` - gesture wrapper that forwards actions
- `eye_control.py` - eye wrapper that forwards actions
- `voice_control_wrapper.py` - background voice forwarding
- `system_actions.py` - canonical action execution

## Standalone Legacy Files

- `hand_gesture_control.py` - legacy gesture implementation, now defaulting to shared camera
- `eye.py` - legacy eye implementation, now defaulting to shared camera

## Run

```bash
python main.py
```

Expected result:

- one window named `AI Virtual Interaction System`
- one shared camera
- eye tracking, hand gesture, and voice control working together