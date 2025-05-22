#!/usr/bin/env python3
"""
Gaming Voice Chat Translator - Complete Version
Real-time translation for multilingual gaming
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import time
import json
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check for required libraries
try:
    import pyaudio
    import speech_recognition as sr
    AUDIO_AVAILABLE = True
    logger.info("✓ Audio libraries loaded")
except ImportError:
    AUDIO_AVAILABLE = False
    logger.error("✗ Audio libraries missing: pip install pyaudio speechrecognition")

try:
    from googletrans import Translator
    TRANSLATE_AVAILABLE = True
    logger.info("✓ Google Translate available")
except ImportError:
    TRANSLATE_AVAILABLE = False
    logger.error("✗ Google Translate missing: pip install googletrans==4.0.0-rc1")

try:
    import pyttsx3
    TTS_AVAILABLE = True
    logger.info("✓ Text-to-Speech available")
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("✗ TTS not available: pip install pyttsx3")

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
    logger.info("✓ Google TTS available")
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("✗ Google TTS not available: pip install gtts pygame")

# Constants
APP_TITLE = "Gaming Voice Chat Translator"
APP_VERSION = "1.0"
BG_COLOR = "#0a0e27"
CARD_BG = "#1a1f3a"
TEXT_COLOR = "#e1e5f2"
ACCENT_COLOR = "#4c9eff"
SUCCESS_COLOR = "#00d26a"
WARNING_COLOR = "#ff9500"
ERROR_COLOR = "#ff3333"

# Gaming languages with flags
GAMING_LANGUAGES = {
    'en': {'name': 'English', 'flag': '🇺🇸'},
    'es': {'name': 'Spanish', 'flag': '🇪🇸'},
    'pt': {'name': 'Portuguese', 'flag': '🇧🇷'},
    'fr': {'name': 'French', 'flag': '🇫🇷'},
    'de': {'name': 'German', 'flag': '🇩🇪'},
    'it': {'name': 'Italian', 'flag': '🇮🇹'},
    'ru': {'name': 'Russian', 'flag': '🇷🇺'},
    'pl': {'name': 'Polish', 'flag': '🇵🇱'},
    'tr': {'name': 'Turkish', 'flag': '🇹🇷'},
    'ar': {'name': 'Arabic', 'flag': '🇸🇦'},
    'zh': {'name': 'Chinese', 'flag': '🇨🇳'},
    'ja': {'name': 'Japanese', 'flag': '🇯🇵'},
    'ko': {'name': 'Korean', 'flag': '🇰🇷'},
    'hi': {'name': 'Hindi', 'flag': '🇮🇳'},
    'th': {'name': 'Thai', 'flag': '🇹🇭'},
    'vi': {'name': 'Vietnamese', 'flag': '🇻🇳'},
    'sv': {'name': 'Swedish', 'flag': '🇸🇪'},
    'da': {'name': 'Danish', 'flag': '🇩🇰'},
    'no': {'name': 'Norwegian', 'flag': '🇳🇴'},
    'fi': {'name': 'Finnish', 'flag': '🇫🇮'},
    'nl': {'name': 'Dutch', 'flag': '🇳🇱'},
    'cs': {'name': 'Czech', 'flag': '🇨🇿'},
    'hu': {'name': 'Hungarian', 'flag': '🇭🇺'},
    'ro': {'name': 'Romanian', 'flag': '🇷🇴'},
    'uk': {'name': 'Ukrainian', 'flag': '🇺🇦'}
}

class VoiceMessage:
    def __init__(self, text, language, is_outgoing=False, translation=None):
        self.text = text
        self.language = language
        self.is_outgoing = is_outgoing
        self.translation = translation
        self.timestamp = datetime.now()

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer() if AUDIO_AVAILABLE else None
        self.microphone = None
        self.is_listening = False
        self.callback = None
        
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
    
    def start_listening(self, device_index, callback):
        if not AUDIO_AVAILABLE or self.is_listening:
            return False
        
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            self.callback = callback
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
            self.listen_thread.start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start listening: {e}")
            return False
    
    def stop_listening(self):
        self.is_listening = False
    
    def _listen_worker(self):
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    if self.is_listening:
                        threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()
                        
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                logger.error(f"Listen error: {e}")
                time.sleep(0.5)
    
    def _process_audio(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
            if text and self.callback:
                self.callback(text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")

class VoiceTranslator:
    def __init__(self):
        self.translator = Translator() if TRANSLATE_AVAILABLE else None
    
    def translate_text(self, text, target_lang, source_lang=None):
        if not self.translator:
            return None
        
        try:
            if not source_lang:
                detection = self.translator.detect(text)
                source_lang = detection.lang
            
            if source_lang == target_lang:
                return text
            
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    def detect_language(self, text):
        if not self.translator:
            return "en"
        
        try:
            detection = self.translator.detect(text)
            return detection.lang
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"

class VoiceSynthesizer:
    def __init__(self):
        self.pyttsx3_engine = None
        if TTS_AVAILABLE:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty('rate', 150)
                self.pyttsx3_engine.setProperty('volume', 0.9)
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")
    
    def speak_text(self, text, language="en"):
        if GTTS_AVAILABLE:
            threading.Thread(target=self._speak_gtts, args=(text, language), daemon=True).start()
        elif self.pyttsx3_engine:
            threading.Thread(target=self._speak_pyttsx3, args=(text,), daemon=True).start()
    
    def _speak_gtts(self, text, language):
        try:
            import tempfile
            tts = gTTS(text=text, lang=language, slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_filename = temp_file.name
                tts.save(temp_filename)
            
            pygame.mixer.init()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.quit()
            os.unlink(temp_filename)
            
        except Exception as e:
            logger.error(f"gTTS error: {e}")
    
    def _speak_pyttsx3(self, text):
        try:
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
        except Exception as e:
            logger.error(f"pyttsx3 error: {e}")

class GamingOverlay:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.overlay = None
        self.is_visible = False
        self.messages = []
    
    def create_overlay(self):
        try:
            self.overlay = tk.Toplevel()
            self.overlay.title("Gaming Translator")
            self.overlay.geometry("400x250+100+100")
            self.overlay.configure(bg=BG_COLOR)
            
            self.overlay.attributes('-alpha', 0.9)
            self.overlay.attributes('-topmost', True)
            self.overlay.overrideredirect(True)
            
            self._setup_ui()
            self._make_draggable()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create overlay: {e}")
            return False
    
    def _setup_ui(self):
        main_frame = tk.Frame(self.overlay, bg=BG_COLOR, bd=2, relief=tk.RAISED)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Header
        header = tk.Frame(main_frame, bg=CARD_BG, height=25)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🎮 Voice Translator", bg=CARD_BG, fg=TEXT_COLOR, 
                font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=2)
        
        close_btn = tk.Button(header, text="✕", bg=ERROR_COLOR, fg="white",
                             font=("Arial", 8, "bold"), bd=0, width=2,
                             command=self.hide_overlay)
        close_btn.pack(side=tk.RIGHT, padx=2)
        
        # Messages area
        self.messages_text = tk.Text(main_frame, bg=BG_COLOR, fg=TEXT_COLOR,
                                    font=("Consolas", 9), wrap=tk.WORD, bd=0,
                                    padx=5, pady=5, state=tk.DISABLED, height=8)
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input area
        input_frame = tk.Frame(main_frame, bg=CARD_BG, height=35)
        input_frame.pack(fill=tk.X)
        input_frame.pack_propagate(False)
        
        self.response_entry = tk.Entry(input_frame, bg=BG_COLOR, fg=TEXT_COLOR,
                                      font=("Segoe UI", 10), relief=tk.FLAT, bd=3)
        self.response_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.response_entry.bind('<Return>', self._send_response)
        
        speak_btn = tk.Button(input_frame, text="🔊", bg=ACCENT_COLOR, fg="white",
                             font=("Arial", 10, "bold"), bd=0, width=3,
                             command=self._speak_response)
        speak_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.header = header
    
    def _make_draggable(self):
        def start_drag(event):
            self.overlay.x = event.x
            self.overlay.y = event.y
        
        def on_drag(event):
            try:
                x = self.overlay.winfo_pointerx() - self.overlay.x
                y = self.overlay.winfo_pointery() - self.overlay.y
                self.overlay.geometry(f"+{x}+{y}")
            except tk.TclError:
                pass
        
        self.header.bind("<Button-1>", start_drag)
        self.header.bind("<B1-Motion>", on_drag)
    
    def show_overlay(self):
        if not self.overlay:
            if not self.create_overlay():
                return False
        
        self.overlay.deiconify()
        self.overlay.lift()
        self.is_visible = True
        return True
    
    def hide_overlay(self):
        if self.overlay:
            self.overlay.withdraw()
            self.is_visible = False
    
    def toggle_overlay(self):
        if self.is_visible:
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def add_message(self, message):
        if not self.overlay:
            return
        
        self.messages.append(message)
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
        
        self._update_display()
    
    def _update_display(self):
        try:
            self.messages_text.configure(state=tk.NORMAL)
            self.messages_text.delete(1.0, tk.END)
            
            for msg in self.messages[-5:]:
                timestamp = msg.timestamp.strftime("%H:%M")
                speaker = "You" if msg.is_outgoing else "Teammate"
                
                line = f"[{timestamp}] {speaker}: {msg.text}\n"
                if msg.translation:
                    line += f"         → {msg.translation}\n"
                
                self.messages_text.insert(tk.END, line)
            
            self.messages_text.configure(state=tk.DISABLED)
            self.messages_text.see(tk.END)
            
        except Exception as e:
            logger.error(f"Error updating overlay: {e}")
    
    def _send_response(self, event=None):
        text = self.response_entry.get().strip()
        if text and hasattr(self.parent_app, 'translate_and_speak_from_overlay'):
            self.response_entry.delete(0, tk.END)
            self.parent_app.translate_and_speak_from_overlay(text)
    
    def _speak_response(self):
        text = self.response_entry.get().strip()
        if text and hasattr(self.parent_app, 'speak_response_from_overlay'):
            self.parent_app.speak_response_from_overlay(text)

class GamingVoiceTranslatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(700, 500)  # Set minimum window size
        
        # Set application icon if available
        try:
            self.root.iconbitmap("app_icon.ico")
        except:
            pass
        
        # Apply theme settings to ttk widgets
        self.apply_theme()
        
        # Core components
        self.voice_recognizer = VoiceRecognizer()
        self.translator = VoiceTranslator()
        self.voice_synthesizer = VoiceSynthesizer()
        self.overlay = GamingOverlay(self)
        
        # State
        self.is_listening = False
        self.my_language = "en"
        self.target_language = "es"
        self.auto_detect = True
        self.selected_device = None
        self.conversation_history = []
        
        # Setup UI and events
        self.setup_ui()
        self.refresh_audio_devices()
        self.setup_hotkeys()
        
        # Check for dependencies
        self.check_dependencies()
        
        # Show help dialog on first run
        self.show_first_run_help()
        
        self.update_status("Ready - Select microphone and start listening")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def apply_theme(self):
        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that we can customize
        
        # Configure Combobox style
        style.configure('TCombobox', 
                        fieldbackground=BG_COLOR,
                        background=BG_COLOR,
                        foreground=TEXT_COLOR,
                        arrowcolor=ACCENT_COLOR,
                        padding=5)
        
        # Configure other ttk widgets as needed
        style.configure('TButton', 
                        background=ACCENT_COLOR,
                        foreground="white",
                        padding=5)

    def check_dependencies(self):
        """Check for required dependencies and show warnings if needed"""
        missing = []
        
        if not AUDIO_AVAILABLE:
            missing.append("Audio libraries (pyaudio, speech_recognition)")
        
        if not TRANSLATE_AVAILABLE:
            missing.append("Translation library (googletrans==4.0.0-rc1)")
        
        if not TTS_AVAILABLE and not GTTS_AVAILABLE:
            missing.append("Text-to-Speech libraries (pyttsx3 or gtts)")
        
        if missing:
            message = "Missing dependencies:\n"
            for m in missing:
                message += f"- {m}\n"
            message += "\nInstall with pip:\npip install pyaudio speechrecognition googletrans==4.0.0-rc1 pyttsx3 gtts pygame"
            
            messagebox.warning(self.root, "Missing Dependencies", message)

    def setup_ui(self):
        # Create menu bar
        self.create_menu_bar()
        
        # Create main container
        main_container = tk.Frame(self.root, bg=BG_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(main_container, text=f"🎮 {APP_TITLE}",
                              bg=BG_COLOR, fg=TEXT_COLOR,
                              font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create sections
        self.create_device_section(main_container)
        self.create_language_section(main_container)
        self.create_control_section(main_container)
        self.create_conversation_section(main_container)
        self.create_status_section(main_container)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Conversation", command=self.save_conversation, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close, accelerator="Alt+F4")
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Options menu
        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(label="Toggle Listening", command=self.toggle_listening, accelerator="Ctrl+L")
        options_menu.add_command(label="Toggle Overlay", command=self.overlay.toggle_overlay, accelerator="Ctrl+O")
        menu_bar.add_cascade(label="Options", menu=options_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Check Dependencies", command=self.check_dependencies)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def show_first_run_help(self):
        """Show help dialog on first run"""
        # Check if first run (could use a config file in real implementation)
        try:
            config_file = os.path.join(os.path.expanduser("~"), ".gaming_translator_config")
            if os.path.exists(config_file):
                return
            
            # Create empty config file for next time
            with open(config_file, "w") as f:
                f.write("first_run=false")
        except:
            pass  # Ignore errors with config file
        
        # Show welcome message
        messagebox.showinfo(
            "Welcome to Gaming Voice Chat Translator",
            "Welcome to the Gaming Voice Chat Translator!\n\n"
            "Quick Start Guide:\n"
            "1. Select your microphone from the dropdown\n"
            "2. Choose your language and your teammate's language\n"
            "3. Click 'Start Listening' to begin voice recognition\n"
            "4. Use the overlay during games with Ctrl+O\n\n"
            "For more help, check the Help menu."
        )
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "Ctrl+L: Toggle Listening\n"
            "Ctrl+O: Toggle Game Overlay\n"
            "Ctrl+S: Save Conversation\n"
            "Ctrl+T: Translate and Speak Text\n"
            "Escape: Hide Overlay\n"
            "Enter: Send Text in Text Box"
        )
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            f"About {APP_TITLE}",
            f"{APP_TITLE} v{APP_VERSION}\n\n"
            "A real-time voice translator for gaming.\n\n"
            "Allows gamers to communicate across language barriers "
            "by automatically translating voice chat."
        )
    
    def create_device_section(self, parent):
        device_frame = tk.LabelFrame(parent, text="🎤 Audio Device",
                                    bg=CARD_BG, fg=TEXT_COLOR,
                                    font=("Segoe UI", 12, "bold"),
                                    bd=2, relief=tk.GROOVE)
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        device_grid = tk.Frame(device_frame, bg=CARD_BG)
        device_grid.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(device_grid, text="Select Microphone:", bg=CARD_BG, fg=TEXT_COLOR,
                font=("Segoe UI", 11)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_grid, textvariable=self.device_var,
                                        state="readonly", width=50)
        self.device_combo.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        self.device_combo.bind('<<ComboboxSelected>>', self.on_device_selected)
        
        refresh_btn = tk.Button(device_grid, text="🔄 Refresh",
                               command=self.refresh_audio_devices,
                               bg=ACCENT_COLOR, fg="white",
                               font=("Segoe UI", 10, "bold"), bd=0, padx=10, pady=5)
        refresh_btn.grid(row=0, column=2)
        
        device_grid.columnconfigure(1, weight=1)
    
    def create_language_section(self, parent):
        lang_frame = tk.LabelFrame(parent, text="🌍 Languages",
                                  bg=CARD_BG, fg=TEXT_COLOR,
                                  font=("Segoe UI", 12, "bold"),
                                  bd=2, relief=tk.GROOVE)
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        
        lang_grid = tk.Frame(lang_frame, bg=CARD_BG)
        lang_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Your language
        tk.Label(lang_grid, text="Your Language:", bg=CARD_BG, fg=TEXT_COLOR,
                font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        my_lang_options = [f"{info['flag']} {info['name']}" for code, info in GAMING_LANGUAGES.items()]
        self.my_lang_var = tk.StringVar(value="🇺🇸 English")
        my_lang_combo = ttk.Combobox(lang_grid, textvariable=self.my_lang_var,
                                    values=my_lang_options, state="readonly", width=25)
        my_lang_combo.grid(row=0, column=1, padx=(0, 20), pady=5)
        my_lang_combo.bind('<<ComboboxSelected>>', self.on_my_language_changed)
        
        # Target language
        tk.Label(lang_grid, text="Teammate's Language:", bg=CARD_BG, fg=TEXT_COLOR,
                font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.target_lang_var = tk.StringVar(value="🇪🇸 Spanish")
        target_lang_combo = ttk.Combobox(lang_grid, textvariable=self.target_lang_var,
                                        values=my_lang_options, state="readonly", width=25)
        target_lang_combo.grid(row=0, column=3, pady=5)
        target_lang_combo.bind('<<ComboboxSelected>>', self.on_target_language_changed)
        
        # Auto-detect
        auto_frame = tk.Frame(lang_frame, bg=CARD_BG)
        auto_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.auto_detect_var = tk.BooleanVar(value=True)
        auto_cb = tk.Checkbutton(auto_frame, text="🔍 Auto-detect teammate's language",
                                variable=self.auto_detect_var, bg=CARD_BG, fg=TEXT_COLOR,
                                selectcolor=BG_COLOR, font=("Segoe UI", 10))
        auto_cb.pack(side=tk.LEFT)
    
    def create_control_section(self, parent):
        control_frame = tk.Frame(parent, bg=BG_COLOR)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Main controls
        main_controls = tk.Frame(control_frame, bg=BG_COLOR)
        main_controls.pack()
        
        self.listen_btn = tk.Button(main_controls, text="🎤 Start Listening",
                                   command=self.toggle_listening,
                                   bg=SUCCESS_COLOR, fg="white",
                                   font=("Segoe UI", 14, "bold"), bd=0,
                                   padx=25, pady=12, width=18)
        self.listen_btn.pack(side=tk.LEFT, padx=10)
        
        self.overlay_btn = tk.Button(main_controls, text="🎮 Show Overlay",
                                    command=self.overlay.toggle_overlay,
                                    bg=ACCENT_COLOR, fg="white",
                                    font=("Segoe UI", 14, "bold"), bd=0,
                                    padx=25, pady=12, width=18)
        self.overlay_btn.pack(side=tk.LEFT, padx=10)
        
        # Recording indicator
        self.recording_var = tk.StringVar(value="")
        recording_label = tk.Label(control_frame, textvariable=self.recording_var,
                                  bg=BG_COLOR, fg=ERROR_COLOR,
                                  font=("Segoe UI", 12, "bold"))
        recording_label.pack(pady=(10, 0))
    
    def create_conversation_section(self, parent):
        conv_frame = tk.LabelFrame(parent, text="💬 Conversation",
                                  bg=CARD_BG, fg=TEXT_COLOR,
                                  font=("Segoe UI", 12, "bold"),
                                  bd=2, relief=tk.GROOVE)
        conv_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Conversation display
        conv_display = tk.Frame(conv_frame, bg=CARD_BG)
        conv_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.conversation_text = tk.Text(conv_display, bg=BG_COLOR, fg=TEXT_COLOR,
                                        font=("Consolas", 10), wrap=tk.WORD,
                                        state=tk.DISABLED, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(conv_display, command=self.conversation_text.yview)
        self.conversation_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Response input
        response_frame = tk.Frame(conv_frame, bg=CARD_BG)
        response_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(response_frame, text="💬 Your Response:", bg=CARD_BG, fg=TEXT_COLOR,
                font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        input_area = tk.Frame(response_frame, bg=CARD_BG)
        input_area.pack(fill=tk.X)
        
        self.response_entry = tk.Entry(input_area, bg=BG_COLOR, fg=TEXT_COLOR,
                                      font=("Segoe UI", 12), relief=tk.FLAT, bd=5)
        self.response_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        self.response_entry.bind('<Return>', self.translate_and_speak)
        
        speak_btn = tk.Button(input_area, text="🔊", command=self.speak_response_text,
                             bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 12, "bold"),
                             bd=0, width=3, height=1)
        speak_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        translate_btn = tk.Button(input_area, text="🌐", command=self.translate_and_speak,
                                 bg=SUCCESS_COLOR, fg="white", font=("Segoe UI", 12, "bold"),
                                 bd=0, width=3, height=1)
        translate_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_status_section(self, parent):
        status_frame = tk.Frame(parent, bg=BG_COLOR)
        status_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar()
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 10),
                               anchor=tk.W, padx=10, pady=5, relief=tk.SUNKEN)
        status_label.pack(fill=tk.X)
    
    def setup_hotkeys(self):
        try:
            self.root.bind('<Control-l>', lambda e: self.toggle_listening())
            self.root.bind('<Control-o>', lambda e: self.overlay.toggle_overlay())
            self.root.bind('<Control-t>', lambda e: self.translate_and_speak())
            self.root.bind('<Escape>', lambda e: self.overlay.hide_overlay())
            # Add additional hotkey for saving conversation
            self.root.bind('<Control-s>', lambda e: self.save_conversation())