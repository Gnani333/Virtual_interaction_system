#!/usr/bin/env python3
"""
Shared Camera Manager - Provides single camera feed to multiple modules
Prevents multiple modules from trying to open the same camera device
"""

import cv2
import threading
import time
import queue
import logging

# Save originals for safe display handling
ORIGINAL_IMSHOW = cv2.imshow
ORIGINAL_WAITKEY = cv2.waitKey
CV2_DISPLAY_ENABLED = False
CV2_DISPLAY_LOCK = threading.Lock()


class SharedCameraManager:
    """
    Manages a single camera and provides frames to multiple consumers
    Ensures only one camera handle is open at a time
    """
    
    def __init__(self, camera_index=0, width=1280, height=720, fps=30):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        
        self.cap = None
        self.running = False
        self.thread = None
        
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.frame_id = 0
        
        self.subscribers = {}  # { subscriber_id: Queue }
        self.subscriber_lock = threading.Lock()
        self.next_subscriber_id = 0
        
        self.logger = logging.getLogger(__name__)
    
    def initialize(self):
        """Initialize camera"""
        if self.cap is not None:
            return True
        
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            self.logger.error(f"Cannot open camera {self.camera_index}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        self.logger.info(f"✓ Shared camera initialized: camera {self.camera_index} ({self.width}x{self.height}@{self.fps}fps)")
        return True
    
    def subscribe(self):
        """Subscribe to camera frames. Returns subscriber_id"""
        with self.subscriber_lock:
            subscriber_id = self.next_subscriber_id
            self.next_subscriber_id += 1
            self.subscribers[subscriber_id] = queue.Queue(maxsize=2)  # Keep last 2 frames
            self.logger.info(f"✓ Subscriber {subscriber_id} subscribed to shared camera")
            return subscriber_id
    
    def unsubscribe(self, subscriber_id):
        """Unsubscribe from camera frames"""
        with self.subscriber_lock:
            if subscriber_id in self.subscribers:
                del self.subscribers[subscriber_id]
                self.logger.info(f"✓ Subscriber {subscriber_id} unsubscribed")
    
    def get_frame(self, subscriber_id, block=True, timeout=1.0):
        """Get latest frame for a subscriber"""
        with self.subscriber_lock:
            if subscriber_id not in self.subscribers:
                return None, None
            queue_obj = self.subscribers[subscriber_id]
        
        try:
            frame_id, frame = queue_obj.get(block=block, timeout=timeout)
            return frame_id, frame.copy() if frame is not None else None
        except queue.Empty:
            return None, None
    
    def _capture_loop(self):
        """Main loop - continuously capture frames and distribute to subscribers"""
        self.logger.info("Camera capture loop started")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning("Failed to read frame")
                continue
            
            with self.frame_lock:
                self.current_frame = frame
                self.frame_id += 1
                current_frame_id = self.frame_id
            
            # Distribute to all subscribers
            with self.subscriber_lock:
                for subscriber_id, queue_obj in self.subscribers.items():
                    try:
                        queue_obj.put_nowait((current_frame_id, frame.copy()))
                    except queue.Full:
                        # Drop oldest frame if queue is full
                        try:
                            queue_obj.get_nowait()
                            queue_obj.put_nowait((current_frame_id, frame.copy()))
                        except:
                            pass
        
        self.logger.info("Camera capture loop stopped")
    
    def start(self):
        """Start camera capture thread"""
        if not self.initialize():
            return False
        
        if self.thread and self.thread.is_alive():
            return True
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, name="SharedCameraCapture", daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop camera capture thread"""
        self.logger.info("Stopping shared camera manager")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.logger.info("Shared camera manager stopped")


# Global instance
_shared_camera = None
_camera_lock = threading.Lock()


def get_shared_camera():
    """Get or create the global shared camera instance"""
    global _shared_camera
    with _camera_lock:
        if _shared_camera is None:
            _shared_camera = SharedCameraManager(camera_index=0)
        return _shared_camera


def show_window(window_name, frame, wait_ms=1):
    """Safely show a window using the original cv2 functions.

    This temporarily enables display so legacy modules that have been
    monkeypatched can remain suppressed while unified display controls
    when windows are shown.
    Returns the key value from the original waitKey.
    """
    global CV2_DISPLAY_ENABLED
    with CV2_DISPLAY_LOCK:
        CV2_DISPLAY_ENABLED = True
        try:
            try:
                ORIGINAL_IMSHOW(window_name, frame)
            except Exception:
                # Best-effort show; swallow errors so display loop continues
                pass
            try:
                k = ORIGINAL_WAITKEY(wait_ms)
            except Exception:
                k = -1
        finally:
            CV2_DISPLAY_ENABLED = False
    return k
