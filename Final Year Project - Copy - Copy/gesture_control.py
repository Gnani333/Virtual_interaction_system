import threading
import logging
import cv2

from hand_gesture_control import HandGestureController as LegacyGesture
import camera_manager as cam_manager
from camera_manager import get_shared_camera


class GestureManager:
    """
    Runs the legacy `HandGestureController` in a background thread and forwards
    detected canonical action names to the provided callback instead of executing
    system calls directly.
    """

    def __init__(self, on_action_callback, camera_index=0):
        self.on_action = on_action_callback
        self.camera_index = camera_index
        self.thread = None
        self.controller = None
        self.running = False
        self.logger = logging.getLogger(__name__)

    def _make_forwarder(self):
        def _forward(action: str):
            try:
                self.logger.info(f"[GESTURE] Forwarding action: {action}")
                self.logger.info(f"[GESTURE] Calling on_action callback...")
                self.on_action(action, source="gesture", details=action)
                self.logger.info(f"[GESTURE] ✓ Action forwarded successfully: {action}")
            except Exception as e:
                self.logger.exception(f"[GESTURE] Error forwarding gesture action: {e}")

        return _forward

    def _disable_cv2_display(self):
        """
        Monkeypatch cv2 functions to suppress window display
        when running with shared camera (display handled by unified_display.py)
        """
        def mock_imshow(window_name, image):
            try:
                if getattr(cam_manager, 'CV2_DISPLAY_ENABLED', False):
                    return cam_manager.ORIGINAL_IMSHOW(window_name, image)
            except Exception:
                pass
            self.logger.debug(f"[GESTURE] Suppressed cv2.imshow('{window_name}')")
            return None

        def mock_waitkey(delay=1):
            try:
                if getattr(cam_manager, 'CV2_DISPLAY_ENABLED', False):
                    return cam_manager.ORIGINAL_WAITKEY(delay)
            except Exception:
                pass
            return -1

        try:
            cv2.imshow = mock_imshow
            cv2.waitKey = mock_waitkey
            self.logger.info("[GESTURE] ✓ Disabled cv2.imshow and cv2.waitKey (guarded)")
        except Exception as e:
            self.logger.exception(f"Failed to monkeypatch cv2: {e}")

    def _run(self):
        try:
            self.logger.info(f"Initializing LegacyGesture with camera index {self.camera_index} (use_shared_camera=True)")
            self.controller = LegacyGesture(camera_index=self.camera_index, use_shared_camera=True)
            self.logger.info("LegacyGesture controller initialized")

            # Disable cv2 display since we're using shared camera
            self._disable_cv2_display()

            # If the legacy controller exposes a hook to trigger actions, replace it.
            forwarder = self._make_forwarder()
            if hasattr(self.controller, "_trigger_once"):
                try:
                    self.logger.info("Replacing _trigger_once method with forwarder")
                    self.controller._trigger_once = forwarder
                    self.logger.info("✓ _trigger_once replacement successful")
                except Exception as e:
                    self.logger.exception(f"Failed to replace _trigger_once: {e}")
            else:
                self.logger.error("Controller doesn't have _trigger_once method!")

            # If the controller exposes a `run` method, call it; otherwise try `start`.
            self.running = True
            self.logger.info("GestureManager running")
            if hasattr(self.controller, "run"):
                self.controller.run()
            elif hasattr(self.controller, "start"):
                self.controller.start()
        except Exception:
            self.logger.exception("Gesture loop crashed")
        finally:
            self.running = False
            self.logger.info("GestureManager stopped")

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="GestureManager", daemon=True)
        self.thread.start()

    def stop(self, timeout=2.0):
        try:
            if self.controller and hasattr(self.controller, "running"):
                try:
                    self.controller.running = False
                except Exception:
                    pass
            if self.thread:
                self.thread.join(timeout=timeout)
        except Exception:
            self.logger.exception("Error stopping GestureManager")
