import threading
import logging

from voice_control import VoiceController as LegacyVoice


class VoiceManager:
    """
    Runs the legacy `VoiceController` in a background thread and intercepts
    intent execution so intents are forwarded to the central controller.
    """

    def __init__(self, on_action_callback):
        self.on_action = on_action_callback
        self.thread = None
        self.controller = None
        self.logger = logging.getLogger(__name__)

    def _intent_forwarder(self, intent: str):
        """Replace the legacy execute_intent with this forwarder."""
        try:
            self.logger.info(f"[VOICE] Forward intent: {intent}")
            self.on_action(intent, source="voice", details=intent)
            return True
        except Exception:
            self.logger.exception("Error forwarding voice intent")
            return True

    def _run(self):
        try:
            self.controller = LegacyVoice()
            # Monkeypatch the legacy executor to forward actions
            if hasattr(self.controller, "execute_intent"):
                try:
                    self.controller.execute_intent = self._intent_forwarder
                except Exception:
                    pass

            self.logger.info("VoiceManager running")
            if hasattr(self.controller, "run"):
                self.controller.run()
            elif hasattr(self.controller, "start"):
                self.controller.start()

        except Exception:
            self.logger.exception("Voice loop crashed")
        finally:
            self.logger.info("VoiceManager stopped")

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="VoiceManager", daemon=True)
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
            self.logger.exception("Error stopping VoiceManager")
