#!/usr/bin/env python3
"""
Diagnose Webcam and MediaPipe Detection Issues
"""

import cv2
import mediapipe as mp
import time
import sys

print("\n" + "="*70)
print("WEBCAM & DETECTION DIAGNOSTIC")
print("="*70)

# ============================================================
# TEST 1: OpenCV and Webcam Access
# ============================================================
print("\n[TEST 1] OpenCV & Webcam Access")
print("-"*70)

print(f"OpenCV Version: {cv2.__version__}")

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✓ Webcam is accessible")
    ret, frame = cap.read()
    if ret:
        print(f"✓ Frame captured successfully: {frame.shape}")
    else:
        print("✗ Cannot read frame from webcam")
        sys.exit(1)
    cap.release()
else:
    print("✗ WEBCAM NOT ACCESSIBLE")
    print("\nPossible causes:")
    print("  1. Webcam in use by another app")
    print("  2. Webcam driver not installed")
    print("  3. Camera disabled in settings")
    sys.exit(1)

# ============================================================
# TEST 2: MediaPipe Initialization
# ============================================================
print("\n[TEST 2] MediaPipe Initialization")
print("-"*70)

try:
    mp_hands = mp.solutions.hands
    mp_face_mesh = mp.solutions.face_mesh
    print("✓ MediaPipe libraries imported")
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ Hand detector initialized")
    
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ Face detector initialized")
except Exception as e:
    print(f"✗ MediaPipe error: {e}")
    sys.exit(1)

# ============================================================
# TEST 3: Live Detection Test (10 frames)
# ============================================================
print("\n[TEST 3] Live Detection Test")
print("-"*70)
print("Processing 10 frames with detection...")
print("(Position your hand and/or face in front of camera)")
print()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

hand_detected = False
face_detected = False
frame_count = 0

for i in range(10):
    ret, frame = cap.read()
    if not ret:
        print(f"✗ Failed to read frame {i}")
        break
    
    frame_count += 1
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect hands
    hand_results = hands.process(frame_rgb)
    if hand_results.multi_hand_landmarks:
        hand_detected = True
        num_hands = len(hand_results.multi_hand_landmarks)
        print(f"Frame {i}: ✓ Hand(s) detected ({num_hands})")
    
    # Detect face
    face_results = face_mesh.process(frame_rgb)
    if face_results.multi_face_landmarks:
        face_detected = True
        num_faces = len(face_results.multi_face_landmarks)
        print(f"Frame {i}: ✓ Face(s) detected ({num_faces})")
    
    if not (hand_results.multi_hand_landmarks or face_results.multi_face_landmarks):
        print(f"Frame {i}: No detections")

cap.release()

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("DIAGNOSTIC SUMMARY")
print("="*70)

print(f"\nFrames processed: {frame_count}/10")
print(f"Hand detection: {'✓ WORKING' if hand_detected else '✗ NOT WORKING'}")
print(f"Face detection: {'✓ WORKING' if face_detected else '✗ NOT WORKING'}")

if hand_detected and face_detected:
    print("\n✓ ALL SYSTEMS WORKING!")
    print("Your webcam and detection are functioning correctly.")
    print("\nTroubleshooting: Check camera settings in your app config.")

elif hand_detected and not face_detected:
    print("\n⚠ Hand detection works, face detection not working")
    print("\nTroubleshooting:")
    print("  • Ensure your face is clearly visible in camera")
    print("  • Check lighting conditions")
    print("  • Increase face detection confidence threshold")

elif not hand_detected and face_detected:
    print("\n⚠ Face detection works, hand detection not working")
    print("\nTroubleshooting:")
    print("  • Position your hand clearly in camera view")
    print("  • Ensure good lighting on your hand")
    print("  • Reduce gesture_frames_required in config.py")

else:
    print("\n✗ NO DETECTIONS WORKING")
    print("\nTroubleshooting steps:")
    print("1. Check lighting - ensure bright, even lighting")
    print("2. Position subject - get face/hand close to camera")
    print("3. Clean camera - wipe lens clean")
    print("4. Check permissions - ensure camera app has permission")
    print("5. Try different distance - experiment with positioning")
    print("6. Update config - adjust confidence thresholds in config.py")
    print()
    print("If still not working:")
    print("  • Try: python eye_module.py (alone)")
    print("  • Check console for specific error messages")

print("\n" + "="*70)
