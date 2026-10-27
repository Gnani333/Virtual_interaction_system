import logging
import threading
import time
import queue

from gesture_control import GestureManager
from voice_control_wrapper import VoiceManager
from eye_control import EyeManager
from unified_display import UnifiedDisplay
from system_actions import SystemActions
from config import SYSTEM_CONFIG
from camera_manager import get_shared_camera


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class MainController:
    def __init__(self):
        self.logger = logging.getLogger("MainController")
        self.system_actions = SystemActions()
        self.queue = queue.Queue()
        self.last_enqueued = {}
        self.duplicate_window = 0.6
        self._lock = threading.Lock()
        self.mode = "auto"
        self.running = False

        self.gesture = GestureManager(self._enqueue_action, camera_index=0)
        self.voice = VoiceManager(self._enqueue_action)
        self.eye = EyeManager(self._enqueue_action)
        self.display = UnifiedDisplay()

        self.exec_thread = threading.Thread(target=self._executor_loop, name="Executor", daemon=True)

    def _enqueue_action(self, action_name, source, details=None):
        now = time.time()
        key = (action_name, source)
        last = self.last_enqueued.get(key, 0)
        if now - last < self.duplicate_window:
            self.logger.debug(f"Dropping duplicate action {action_name} from {source} (within {self.duplicate_window}s)")
            return

        self.last_enqueued[key] = now
        self.logger.info(f"Enqueue: {action_name} from {source}")
        try:
            self.queue.put((action_name, source, details or ""), block=False)
        except Exception:
            self.queue.put((action_name, source, details or ""))

    def _should_accept(self, source: str) -> bool:
        if self.mode == "gesture" and source != "gesture":
            return False
        if self.mode == "voice" and source != "voice":
            return False
        return True

    def _executor_loop(self):
        self.logger.info("Executor loop started")
        pri = SYSTEM_CONFIG.get("input_priority", {})
        while self.running:
            try:
                action_name, source, details = self.queue.get(timeout=0.2)
            except Exception:
                continue

            if not self._should_accept(source):
                self.logger.info(f"Blocked by mode ({self.mode}): {action_name} from {source}")
                continue

            with self._lock:
                try:
                    try:
                        nxt = self.queue.get_nowait()
                        self.queue.put(nxt)
                        next_action, next_source, _ = nxt
                        cur_p = pri.get(source, 1)
                        next_p = pri.get(next_source, 1)
                        if next_p > cur_p:
                            self.logger.info(f"Deferring {action_name} ({source}) to honor higher priority {next_action} ({next_source})")
                            self.queue.put((action_name, source, details))
                            continue
                    except Exception:
                        pass

                    self.logger.info(f"Executing {action_name} from {source}")
                    self.system_actions.perform(action_name, source, details)
                    time.sleep(0.05)
                except Exception:
                    self.logger.exception("Error while executing action")

    def start(self):
        self.running = True
        self.logger.info("Starting unified system...")

        shared_cam = get_shared_camera()
        self.logger.info("✓ Starting shared camera")
        shared_cam.start()

        self.logger.info("✓ Starting gesture manager")
        self.gesture.start()

        self.logger.info("✓ Starting eye manager")
        self.eye.start()

        self.logger.info("✓ Starting voice manager")
        self.voice.start()

        self.exec_thread.start()

        self.logger.info("✓ All managers started")
        self.logger.info("✓ Starting unified display...")
        time.sleep(1.0)

        try:
            self.display.run()
        except KeyboardInterrupt:
            self.logger.info("Display interrupted")
        except Exception:
            self.logger.exception("Display error")
        finally:
            self.stop()

    def stop(self):
        self.logger.info("Stopping unified system...")
        self.running = False
        try:
            self.gesture.stop()
            self.voice.stop()
            self.eye.stop()
            self.display.stop()
        except Exception:
            self.logger.exception("Error stopping managers")

        shared_cam = get_shared_camera()
        shared_cam.stop()

        self.exec_thread.join(timeout=2.0)
        self.logger.info("✓ MainController stopped")

    def set_mode(self, mode: str):
        if mode not in ("auto", "gesture", "voice", "eye"):
            raise ValueError("mode must be one of 'auto','gesture','voice','eye'")
        self.mode = mode
        self.logger.info(f"Mode switched to: {mode}")