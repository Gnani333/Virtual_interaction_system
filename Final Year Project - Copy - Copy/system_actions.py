import logging

from action_mapper import get_mapper


class SystemActions:
    """
    Centralized safe executor that uses the project's ActionMapper to run actions.
    Provides a single point for logging and exception handling.
    """

    def __init__(self):
        self.mapper = get_mapper()
        self.logger = logging.getLogger(__name__)
        # Debounce recent executions to avoid duplicates from monkeypatched modules
        self._last_executed = {}
        self._debounce_window = 0.6  # seconds

    def perform(self, action_name: str, source: str, details: str = None) -> bool:
        import time
        try:
            now = time.time()
            key = (action_name, source)
            last = self._last_executed.get(key, 0)
            if now - last < self._debounce_window:
                self.logger.info(f"[ACTION] Debounced duplicate: {action_name} from {source}")
                return False

            self.logger.info(f"[ACTION] Request: {action_name} from {source} details={details}")
            success = self.mapper.execute_action(action_name, source, details)
            self.logger.info(f"[ACTION] Result: {action_name} -> {success}")
            if success:
                self._last_executed[key] = now
            return bool(success)
        except Exception:
            self.logger.exception("Action execution failed")
            return False
