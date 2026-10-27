# ============================================================
# UNIFIED MULTI-MODAL SYSTEM - Eyes + Gestures + Voice
# ============================================================
# Single display window showing eye tracking + gesture recognition

import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import os
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'

from config import EYE_CONFIG, GESTURE_CONFIG, COLORS
from event_bus import EventType, get_event_bus, emit_event
from camera_manager import get_shared_camera, show_window
import camera_manager as cam_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class UnifiedDisplay:
    """Combined eye tracking and gesture recognition using shared camera"""
    
    def __init__(self):
        self.logger = logging.getLogger("UnifiedDisplay")
        self.event_bus = get_event_bus()
        self.running = True
        
        # Use shared camera manager - NO separate camera instances!
        self.shared_camera = get_shared_camera()
        self.subscriber_id = self.shared_camera.subscribe()
        self.logger.info(f"✓ Subscribed to shared camera with ID {self.subscriber_id}")
        
        # MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        
        # Eye landmarks
        self.left_iris_indices = [468, 469, 470, 471, 472]
        self.right_iris_indices = [473, 474, 475, 476, 477]
        self.left_eye_indices = [33, 160, 158, 133, 153, 144]
        self.right_eye_indices = [263, 387, 385, 362, 380, 373]
        
        # State
        self.current_frame = None
        self.eye_status = "Initializing..."
        self.gesture_status = "Initializing..."
        self.eye_gaze = "CENTER"
        self.gesture_type = "neutral"
        
        self.logger.info("[UNIFIED] Display initialized with shared camera")
    
    def process_frame(self, frame):
        """Process single frame for BOTH eye tracking and gesture recognition"""
        h, w, c = frame.shape
        result_frame = frame.copy()
        
        # Process for eye tracking
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = self.face_mesh.process(rgb_frame)
        
        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            
            # Draw iris circles
            left_iris_x = int(np.mean([landmarks[i].x for i in self.left_iris_indices]) * w)
            left_iris_y = int(np.mean([landmarks[i].y for i in self.left_iris_indices]) * h)
            cv2.circle(result_frame, (left_iris_x, left_iris_y), 8, (0, 200, 255), 2)
            
            right_iris_x = int(np.mean([landmarks[i].x for i in self.right_iris_indices]) * w)
            right_iris_y = int(np.mean([landmarks[i].y for i in self.right_iris_indices]) * h)
            cv2.circle(result_frame, (right_iris_x, right_iris_y), 8, (255, 0, 100), 2)
            
            self.eye_status = "✓ Face Detected"
        else:
            self.eye_status = "✗ No Face"
        
        # Process for gesture recognition
        gesture_frame = result_frame
        rgb_gesture = cv2.cvtColor(gesture_frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb_gesture)
        
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for idx, lm in enumerate(hand_landmarks.landmark):
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    cv2.circle(gesture_frame, (x, y), 3, (100, 0, 255), -1)
            self.gesture_status = f"✓ {len(hand_results.multi_hand_landmarks)} hand(s)"
        else:
            self.gesture_status = "✗ No Hands"
        
        # Use gesture_frame result (it has both detections)
        result_frame = gesture_frame
        
        return result_frame
    
    def start(self):
        """Start unified display loop"""
        self.logger.info("Starting unified display...")
    
    def stop(self):
        """Stop unified display"""
        self.logger.info("Stopping unified display...")
        self.running = False
        if self.shared_camera and self.subscriber_id is not None:
            self.shared_camera.unsubscribe(self.subscriber_id)
        cv2.destroyAllWindows()
    
    def run(self):
        """Main display loop - gets frames from shared camera and processes both modules"""
        self.logger.info("\n" + "="*70)
        self.logger.info("UNIFIED MULTI-MODAL SYSTEM - Hand Gesture + Eye Gaze")
        self.logger.info("="*70)
        self.logger.info("[UNIFIED] Press Q to quit")
        self.logger.info("="*70 + "\n")
        
        try:
            frame_count = 0
            while self.running:
                # Get frame from shared camera
                frame_id, frame = self.shared_camera.get_frame(self.subscriber_id, block=False, timeout=0.1)
                
                if frame is None:
                    time.sleep(0.001)
                    continue
                
                # Process frame for BOTH eye tracking and gesture recognition
                display_frame = self.process_frame(frame)
                
                # Draw HUD overlay
                h, w = display_frame.shape[:2]
                cv2.rectangle(display_frame, (10, 10), (w-10, 90), (0, 0, 0), -1)
                cv2.rectangle(display_frame, (10, 10), (w-10, 90), (0, 255, 0), 2)
                
                cv2.putText(display_frame, "AI Virtual Interaction System", (20, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, f"Eye: {self.eye_status} | Gesture: {self.gesture_status}", (20, 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Display ONLY ONE window using camera_manager.show_window
                key = show_window("AI Virtual Interaction System", display_frame, wait_ms=1) & 0xFF
                if key == ord('q'):
                    self.logger.info("[UNIFIED] Quit requested")
                    self.running = False
                    break
                
                frame_count += 1
                if frame_count % 100 == 0:
                    self.logger.info(f"Frame {frame_count} | Eye: {self.eye_status} | Gesture: {self.gesture_status}")
                
                time.sleep(0.001)
        
        except Exception as e:
            self.logger.exception(f"[UNIFIED] Display error: {e}")
        finally:
            self.running = False
            self.stop()
            self.logger.info("[UNIFIED] Display stopped\n")


if __name__ == "__main__":
    try:
        display = UnifiedDisplay()
        display.run()
    except Exception as e:
        print(f"[ERROR] {e}")

