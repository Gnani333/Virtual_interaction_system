# ============================================================
# VOICE CONTROL MODULE - Refactored for Integration
# ============================================================
# Emits events instead of direct control
# Works with event_bus and action_mapper

import os
import sys
import speech_recognition as sr
import pyttsx3
import time

# Delay imports to avoid circular dependency
VOICE_CONFIG = None
COLORS = None
EventType = None
emit_event = None


def _init_imports():
    global VOICE_CONFIG, COLORS, EventType, emit_event
    from config import VOICE_CONFIG as VC, COLORS as C
    from event_bus import EventType as ET, emit_event as EE
    VOICE_CONFIG = VC
    COLORS = C
    EventType = ET
    emit_event = EE


class VoiceController:
    """Refactored voice control - emits events"""
    
    def __init__(self):
        _init_imports()
        
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = VOICE_CONFIG.get("energy_threshold", 4000)
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[VOICE] Microphone initialized")
        except Exception as e:
            print(f"[VOICE] WARNING: Microphone init failed: {e}")
            self.microphone = None
        
        # Text-to-speech
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", VOICE_CONFIG.get("speech_rate", 170))
            self.tts_available = True
        except Exception as e:
            print(f"[VOICE] WARNING: TTS not available: {e}")
            self.tts_available = False
        
        self.running = True
        self.event_bus = None
        self.action_translator = None
        self.last_command_time = 0
        self.command_cooldown = VOICE_CONFIG.get("command_cooldown", 0.5)
        
        print("[VOICE] Initialized")
    
    def speak(self, text: str):
        """Text-to-speech feedback"""
        if not self.tts_available:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[VOICE] TTS error: {e}")
    
    def listen(self) -> str:
        """Listen for voice command"""
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5)
            
            # Try Google Speech Recognition first
            try:
                command = self.recognizer.recognize_google(audio)
                return command.lower().strip()
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None
        
        except sr.RequestError as e:
            print(f"[VOICE] API error: {e}")
            return None
        except Exception as e:
            print(f"[VOICE] Listen error: {e}")
            return None
    
    def local_intent(self, command: str) -> str:
        """Map command to intent using keyword matching"""
        if not command:
            return None
        
        cmd = command.lower().strip()
        
        # Remove common prefixes
        for prefix in ["please ", "could you ", "would you ", "hey ", "can you "]:
            if cmd.startswith(prefix):
                cmd = cmd[len(prefix):].strip()
        
        # Keyword -> intent mapping
        intent_map = {
            # Navigation
            "next_tab": ["next tab", "next", "go next", "forward"],
            "previous_tab": ["previous tab", "previous", "back", "go back"],
            "close_tab": ["close tab", "close this tab"],
            "new_tab": ["new tab", "open tab"],
            
            # Window
            "close_window": ["close window", "close app", "exit"],
            "minimize": ["minimize", "minimise", "minimize window"],
            "maximize": ["maximize", "fullscreen"],
            "show_desktop": ["show desktop", "minimize all"],
            
            # Text
            "copy": ["copy", "copy that"],
            "paste": ["paste"],
            "cut": ["cut"],
            "select_all": ["select all", "highlight all"],
            "undo": ["undo", "undo that"],
            "redo": ["redo"],
            "find": ["find", "search"],
            
            # Media
            "play_pause": ["play", "pause", "resume"],
            "volume_up": ["volume up", "louder", "increase volume"],
            "volume_down": ["volume down", "quieter", "decrease volume"],
            "mute": ["mute", "silence"],
            
            # System
            "screenshot": ["screenshot", "take screenshot", "capture"],
            "escape": ["escape", "cancel", "exit"],
            "enter": ["enter", "confirm", "submit"],
            
            # Applications
            "open_browser": ["open browser", "open chrome", "launch browser", "start browser", "open google"],
            "open_notepad": ["open notepad", "open text editor"],
            "open_terminal": ["open terminal", "open command prompt", "open cmd"],
        }
        
        for intent, phrases in intent_map.items():
            for phrase in phrases:
                if phrase in cmd:
                    return intent
        
        return None
    
    def execute_command(self, intent: str):
        """Execute intent by emitting event"""
        if not intent:
            return False
        
        # Check cooldown
        now = time.time()
        if (now - self.last_command_time) < self.command_cooldown:
            return False
        
        try:
            # Emit event through event bus
            if self.event_bus:
                from event_bus import emit_event, EventType
                emit_event(
                    EventType.VOICE_COMMAND,
                    "voice",
                    {"intent": intent, "action": intent},
                    priority=3
                )
            
            self.last_command_time = now
            return True
        
        except Exception as e:
            print(f"[VOICE] Execute error: {e}")
            return False
    
    def run(self):
        """Main voice control loop"""
        print("\n[VOICE] Started listening... (Press Ctrl+C to stop)")
        self.speak("Voice control activated")
        
        try:
            while self.running:
                # Listen for command
                command = self.listen()
                
                if command:
                    print(f"[VOICE] Heard: {command}")
                    
                    # Parse intent
                    intent = self.local_intent(command)
                    
                    if intent:
                        print(f"[VOICE] Intent: {intent}")
                        self.speak(f"Executing {intent}")
                        self.execute_command(intent)
                    else:
                        print(f"[VOICE] Unknown command")
                        self.speak("Command not recognized")
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n[VOICE] Stopped")
            self.running = False
        except Exception as e:
            print(f"[VOICE] Fatal error: {e}")
            self.running = False


if __name__ == "__main__":
    controller = VoiceController()
    controller.run()
