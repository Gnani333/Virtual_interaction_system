# Implementation Checklist & Validation Guide

## Pre-Launch Checklist

### Dependencies ✓
- [ ] OpenCV (`cv2`) installed
- [ ] MediaPipe installed
- [ ] PyAutoGUI installed
- [ ] Speech recognition libraries available
- [ ] Camera device accessible (/dev/video0 or equivalent)

### Code Changes Verification

#### unified_display.py
- [ ] Imports `get_shared_camera` from camera_manager
- [ ] NO `cv2.VideoCapture(0)` for eye camera
- [ ] NO `cv2.VideoCapture(0)` for gesture camera
- [ ] Uses `self.shared_camera = get_shared_camera()`
- [ ] Subscribes to shared camera: `self.subscriber_id = self.shared_camera.subscribe()`
- [ ] `process_frame()` method exists and handles BOTH eye + gesture
- [ ] Only ONE `cv2.imshow("AI Virtual Interaction System", display_frame)` call
- [ ] `run()` method gets frames using `self.shared_camera.get_frame()`
- [ ] Includes `start()` and `stop()` methods

#### gesture_control.py
- [ ] Imports `cv2`
- [ ] Has `_disable_cv2_display()` method
- [ ] Monkeypatches `cv2.imshow` and `cv2.waitKey`
- [ ] Calls `_disable_cv2_display()` in `_run()` BEFORE controller init
- [ ] Logs: "[GESTURE] ✓ Disabled cv2.imshow and cv2.waitKey"

#### eye_control.py
- [ ] Imports `cv2`
- [ ] Has `_disable_cv2_display()` method
- [ ] Monkeypatches `cv2.imshow` and `cv2.waitKey`
- [ ] Calls `_disable_cv2_display()` in `_run()` BEFORE controller init
- [ ] Logs: "[EYE] ✓ Disabled cv2.imshow and cv2.waitKey"

#### main.py
- [ ] Imports `UnifiedDisplay` from unified_display
- [ ] Creates `self.display = UnifiedDisplay()` in `__init__`
- [ ] Calls `shared_cam.start()` FIRST
- [ ] Then starts gesture, eye, voice managers
- [ ] Then starts executor thread
- [ ] Calls `self.display.run()` (blocking, in main thread)
- [ ] Calls `self.display.stop()` in cleanup
- [ ] Properly handles KeyboardInterrupt

#### camera_manager.py
- [ ] NO changes needed - verify it's intact

---

## Launch Testing

### Step 1: Start System
```bash
python main.py
```

### Step 2: Verify Output (should see):
✓ MainController logging
✓ Shared camera starting  
✓ GestureManager starting
✓ EyeManager starting
✓ VoiceManager starting
✓ Window titled "AI Virtual Interaction System" appearing

### Step 3: Verify Behavior

#### Eye Tracking:
- [ ] Face detected → iris circles appear (left: blue, right: red)
- [ ] No face → "✗ No Face" in status

#### Gesture Recognition:
- [ ] Hands detected → hand landmarks appear (purple dots)
- [ ] No hands → "✗ No Hands" in status

#### Voice Control:
- [ ] NO visible window
- [ ] Running in background
- [ ] Commands recognized in console logs

### Step 4: Verify No Stray Windows
- [ ] Only ONE window visible
- [ ] No separate "Eye Tracking" window
- [ ] No separate "Hand Gesture Control" window
- [ ] No cv2 debug windows

### Step 5: Test Quit
- [ ] Press 'Q' in the window
- [ ] System shuts down gracefully
- [ ] All threads stop
- [ ] No hanging processes

---

## Debug Commands

### Check if Multiple Camera Instances
```bash
# In terminal, while system running:
lsof | grep /dev/video0
# Should show ONLY ONE process accessing camera
```

### Enable Debug Logging
In any manager file, change:
```python
logging.basicConfig(level=logging.DEBUG)  # instead of INFO
```

### Verify Shared Camera Subscription
Look for logs like:
```
✓ Subscribed to shared camera with ID 0
✓ Subscribed to shared camera with ID 1
✓ Subscribed to shared camera with ID 2
```

### Confirm Display Monkeypatching
Look for logs like:
```
[GESTURE] ✓ Disabled cv2.imshow and cv2.waitKey
[EYE] ✓ Disabled cv2.imshow and cv2.waitKey
```

---

## Performance Metrics

### Expected Behavior:
- FPS: 15-30 depending on hardware
- CPU: 40-60% (full system)
- Memory: 300-500 MB
- Latency: <200ms from gesture to action

### If Performance Issues:
1. Reduce hand detection confidence
2. Reduce face mesh refinement
3. Lower video resolution
4. Disable debug logging
5. Check system resources

---

## Common Issues & Solutions

### Issue: Multiple Windows Opening
**Cause**: cv2 monkeypatching not working
**Fix**: 
- Verify `_disable_cv2_display()` called BEFORE `controller.run()`
- Check that cv2 import happens in gesture_control.py and eye_control.py

### Issue: No Display Window
**Cause**: display.run() not executing
**Fix**:
- Check main.py line 104: `self.display.run()`
- Verify UnifiedDisplay imported correctly
- Check for exceptions in logs

### Issue: Camera Locked/Unavailable
**Cause**: Legacy script or another app using camera
**Fix**:
- Killall Python processes: `pkill -f python`
- Check: `lsof | grep video0`
- Restart system

### Issue: Actions Not Executing
**Cause**: Mode set incorrectly
**Fix**:
- Check default mode: `self.mode = "auto"`
- Verify _should_accept() logic
- Check action queue in logs

### Issue: Voice Not Working
**Cause**: No audio input
**Fix**:
- Test microphone separately
- Check audio device: `arecord -l`
- Verify voice_control_wrapper.py microphone setting

---

## Success Indicators ✓

You know it's working when:

1. ✓ Single "AI Virtual Interaction System" window appears
2. ✓ Eye tracking shows: "Face Detected" with iris circles
3. ✓ Gesture shows: Hand count detected
4. ✓ Voice logs show microphone listening
5. ✓ Perform a gesture → action logged in console
6. ✓ Say a voice command → intent recognized
7. ✓ Press 'Q' → clean shutdown
8. ✓ No stray opencv windows
9. ✓ No camera lock warnings
10. ✓ All threads properly stopped

---

## Next Steps After Validation

1. ✓ Test all gestures: swipe, pinch, thumbs_up, etc.
2. ✓ Test voice commands: "screenshot", "volume up", etc.
3. ✓ Test mode switching if implemented
4. ✓ Test long-duration run (1+ hours)
5. ✓ Stress test with rapid gestures
6. ✓ Fine-tune detection confidence
7. ✓ Calibrate eye gaze if needed

---

## Rollback Instructions

If something breaks, restore from:
1. git (if version controlled)
2. Or manually revert these files:
   - unified_display.py
   - gesture_control.py
   - eye_control.py
   - main.py

---

**Status**: Ready for testing! All modifications complete.
