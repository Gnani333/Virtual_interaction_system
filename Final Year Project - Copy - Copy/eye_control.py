import threading
import logging
import cv2
import time

import eye as eye_module
import camera_manager as cam_manager


class EyeManager:
    """
    Runs the legacy `IrisTracker` from `eye.py` and monkeypatches
    `pyautogui` calls so they forward canonical actions to the main controller.
    Also disables cv2 display functions since display is handled by unified_display.py
    """

    KEYMAP = {
        ("ctrl", "tab"): "next_tab",
        ("ctrl", "shift", "tab"): "previous_tab",
        ("printscreen",): "screenshot",
        ("volumeup",): "volume_up",
        ("volumedown",): "volume_down",
    }

    def __init__(self, on_action_callback):
        self.on_action = on_action_callback
        self.thread = None
        self.controller = None
        self.running = False
        self.logger = logging.getLogger(__name__)

    def _map_keys_to_action(self, *keys):
        k = tuple(k.lower() for k in keys)
        return self.KEYMAP.get(k)

    def _make_pyautogui_wrappers(self):
        """Create wrappers for hotkey/press/screenshot used by IrisTracker."""

        def hotkey(*keys):
            act = self._map_keys_to_action(*keys)
            if act:
                self.logger.info(f"[EYE->ACTION] hotkey {keys} -> {act}")
                self.on_action(act, source="eye", details=str(keys))
            else:
                self.logger.info(f"[EYE] Ignored hotkey {keys}")

        def press(key):
            act = self._map_keys_to_action(key)
            if act:
                self.logger.info(f"[EYE->ACTION] press {key} -> {act}")
                self.on_action(act, source="eye", details=key)
            else:
                self.logger.info(f"[EYE] Ignored press {key}")

        def screenshot(fname=None):
            act = "screenshot"
            self.logger.info(f"[EYE->ACTION] screenshot -> {act}")
            self.on_action(act, source="eye", details=fname or "")

        return hotkey, press, screenshot

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
            self.logger.debug(f"[EYE] Suppressed cv2.imshow('{window_name}')")
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
            self.logger.info("[EYE] ✓ Disabled cv2.imshow and cv2.waitKey (guarded)")
        except Exception as e:
            self.logger.exception(f"Failed to monkeypatch cv2: {e}")

    def _run(self):
        try:
            self.controller = eye_module.IrisTracker(use_shared_camera=True)

            # Disable cv2 display since we're using shared camera
            self._disable_cv2_display()

            # Monkeypatch pyautogui functions used by the eye module
            try:
                hotkey, press, screenshot = self._make_pyautogui_wrappers()
                eye_module.pyautogui.hotkey = hotkey
                eye_module.pyautogui.press = press
                eye_module.pyautogui.screenshot = screenshot
            except Exception:
                self.logger.exception("Failed to monkeypatch pyautogui for eye module")

            self.running = True
            self.logger.info("EyeManager running")
            if hasattr(self.controller, "run"):
                self.controller.run()
            elif hasattr(self.controller, "start"):
                self.controller.start()

        except Exception:
            self.logger.exception("Eye tracking loop crashed")
        finally:
            self.running = False
            self.logger.info("EyeManager stopped")

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="EyeManager", daemon=True)
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
            self.logger.exception("Error stopping EyeManager")
