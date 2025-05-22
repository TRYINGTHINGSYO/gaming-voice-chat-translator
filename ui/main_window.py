"""
Main application window for the Gaming Voice Chat Translator
Updated with enhanced audio controls integration
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime

from gaming_translator.utils.constants import (
    APP_NAME, APP_VERSION, UI_COLORS, GAMING_LANGUAGES, EXPORT_FORMATS
)
from gaming_translator.core.voice_recognizer import VoiceRecognizer, list_audio_devices
from gaming_translator.core.translator import Translator, CachedTranslator
from gaming_translator.core.synthesizer import VoiceSynthesizer, MultiLanguageVoiceSynthesizer
from gaming_translator.core.session_manager import SessionManager, VoiceMessage
from gaming_translator.ui.overlay import GamingOverlay

class GamingTranslatorApp:
    """Main application class for the Gaming Voice Chat Translator"""
    
    def __init__(self, config):
        """Initialize the application with configuration"""
        self.logger = logging.getLogger("gaming_translator.ui.main_window")
        self.config = config
        self.root = None
        
        # Core components (initialized in start method)
        self.voice_recognizer = None
        self.translator = None
        self.voice_synthesizer = None
        self.session_manager = None
        self.overlay = None
        self.audio_section = None
        
        # State
        self.is_listening = False
        self.selected_device = None
        self.input_volume = 0.8
        self.output_volume = 0.7
        
        self.logger.info("Application initialized")
    
    def start(self):
        """Start the application"""
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(
            self.config.get("ui", "window_size", "900x700")
        )
        self.root.minsize(800, 600)
        
        # Apply theme
        self._apply_theme()
        
        # Set icon if available
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "app_icon.ico"
        )
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass
        
        # Initialize core components
        self._init_components()
        
        # Setup UI and events
        self._setup_ui()
        self._setup_hotkeys()
        
        # Check for first run
        if self.config.is_first_run():
            self._show_first_run_help()
            self.config.mark_first_run_complete()
        
        # Update status
        self._update_status("Ready - Select microphone and start listening")
        
        # Set up cleanup
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start main loop
        self.logger.info("Starting main application loop")
        self.root.mainloop()
    
    def _init_components(self):
        """Initialize core components"""
        try:
            # Create session manager first
            self.session_manager = SessionManager(self.config)
            
            # Create voice recognizer using the factory method
            self.voice_recognizer = VoiceRecognizer.create_recognizer(self.config)
            
            # Create translator with caching
            base_translator = Translator.create_translator(self.config)
            self.translator = CachedTranslator(self.config, base_translator)
            
            # Create voice synthesizer
            base_synthesizer = VoiceSynthesizer.create_synthesizer(self.config)
            self.voice_synthesizer = MultiLanguageVoiceSynthesizer(self.config)
            
            # Create overlay
            self.overlay = GamingOverlay(self, self.config)
            
            self.logger.info("Core components initialized")
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize application components:\n{str(e)}"
            )
    
    def _apply_theme(self):
        """Apply theme to the application"""
        # Configure root window
        self.root.configure(bg=UI_COLORS["BG_COLOR"])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Combobox style
        style.configure('TCombobox', 
                        fieldbackground=UI_COLORS["BG_COLOR"],
                        background=UI_COLORS["BG_COLOR"],
                        foreground=UI_COLORS["TEXT_COLOR"],
                        arrowcolor=UI_COLORS["ACCENT_COLOR"],
                        padding=5)
        
        # Configure other ttk widgets
        style.configure('TButton', 
                        background=UI_COLORS["ACCENT_COLOR"],
                        foreground="white",
                        padding=5)
        
        style.configure('TLabel',
                       background=UI_COLORS["CARD_BG"],
                       foreground=UI_COLORS["TEXT_COLOR"])
        
        style.configure('TFrame',
                       background=UI_COLORS["BG_COLOR"])
    
    def _setup_ui(self):
        """Setup the main application UI"""
        # Create menu bar
        self._create_menu_bar()
        
        # Create main container
        main_container = tk.Frame(self.root, bg=UI_COLORS["BG_COLOR"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(
            main_container, 
            text=f"🎮 {APP_NAME}",
            bg=UI_COLORS["BG_COLOR"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create sections
        self._create_enhanced_audio_section(main_container)
        self._create_language_section(main_container)
        self._create_enhanced_control_section(main_container)
        self._create_conversation_section(main_container)
        self._create_status_section(main_container)
    
    def _create_enhanced_audio_section(self, parent):
        """Create enhanced audio device section with level meter and volume controls"""
        
        # Import the new audio controls
        from gaming_translator.ui.audio_controls import EnhancedAudioSection
        
        def on_device_change(device_index):
            """Handle device selection change"""
            self.selected_device = device_index
            
            # Save to config
            self.config.set("recognition", "device_index", str(device_index))
            self.config.save()
            
            self._update_status(f"Selected audio device: {device_index}")
            
            # If currently listening, restart with new device
            if self.is_listening:
                self._stop_listening()
                # Small delay to ensure cleanup
                self.root.after(500, lambda: self._start_listening())
        
        def on_input_volume_change(volume):
            """Handle input volume change"""
            self.input_volume = volume
            
            # Update voice recognizer sensitivity if it supports it
            if hasattr(self.voice_recognizer, 'set_sensitivity'):
                self.voice_recognizer.set_sensitivity(volume)
            
            # Save to config
            self.config.set("audio", "input_volume", str(volume))
            self.config.save()
            
            self._update_status(f"Input sensitivity: {int(volume * 100)}%")
        
        def on_output_volume_change(volume):
            """Handle output volume change"""
            self.output_volume = volume
            
            # Update TTS volume if it supports it
            if hasattr(self.voice_synthesizer, 'set_volume'):
                self.voice_synthesizer.set_volume(volume)
            
            # Save to config
            self.config.set("audio", "output_volume", str(volume))
            self.config.save()
            
            self._update_status(f"Output volume: {int(volume * 100)}%")
        
        # Load initial volumes from config
        initial_input_volume = self.config.get_float("audio", "input_volume", 0.8)
        initial_output_volume = self.config.get_float("audio", "output_volume", 0.7)
        
        # Create enhanced audio section
        self.audio_section = EnhancedAudioSection(
            parent, 
            device_change_callback=on_device_change,
            input_volume_callback=on_input_volume_change,
            output_volume_callback=on_output_volume_change
        )
        self.audio_section.pack(fill=tk.X, pady=(0, 15))
        
        # Set initial volumes
        self.audio_section.set_input_volume(initial_input_volume)
        self.audio_section.set_output_volume(initial_output_volume)
        
        # Get initial device selection
        initial_device = self.audio_section.get_selected_device_index()
        if initial_device is not None:
            self.selected_device = initial_device
        
        return self.audio_section
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="New Session", 
            command=self._new_session,
            accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="Save Session", 
            command=self._save_session,
            accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="Load Session", 
            command=self._load_session,
            accelerator="Ctrl+O"
        )
        
        # Export submenu
        export_menu = tk.Menu(file_menu, tearoff=0)
        for format_code, format_info in EXPORT_FORMATS.items():
            export_menu.add_command(
                label=f"Export as {format_info['name']}",
                command=lambda fmt=format_code: self._export_session(fmt)
            )
        
        file_menu.add_cascade(label="Export", menu=export_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Alt+F4")
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Options menu
        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(
            label="Toggle Listening", 
            command=self._toggle_listening, 
            accelerator="Ctrl+L"
        )
        options_menu.add_command(
            label="Toggle Overlay", 
            command=self.overlay.toggle_overlay, 
            accelerator="Ctrl+O"
        )
        options_menu.add_separator()
        options_menu.add_command(
            label="Settings", 
            command=self._show_settings
        )
        menu_bar.add_cascade(label="Options", menu=options_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="Keyboard Shortcuts", 
            command=self._show_shortcuts
        )
        help_menu.add_command(
            label="Check Dependencies", 
            command=self._check_dependencies
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="About", 
            command=self._show_about
        )
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Set menu bar
        self.root.config(menu=menu_bar)
    
    def _create_language_section(self, parent):
        """Create language selection section"""
        lang_frame = tk.LabelFrame(
            parent, 
            text="🌍 Languages",
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 12, "bold"),
            bd=2, 
            relief=tk.GROOVE
        )
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        
        lang_grid = tk.Frame(lang_frame, bg=UI_COLORS["CARD_BG"])
        lang_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Your language
        tk.Label(
            lang_grid, 
            text="Your Language:", 
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        my_lang_options = [
            f"{info['flag']} {info['name']}" 
            for code, info in GAMING_LANGUAGES.items()
        ]
        
        my_lang_code = self.config.get("translation", "my_language", "en")
        my_lang_info = GAMING_LANGUAGES.get(my_lang_code, {"name": "English", "flag": "🇺🇸"})
        my_lang_display = f"{my_lang_info['flag']} {my_lang_info['name']}"
        
        self.my_lang_var = tk.StringVar(value=my_lang_display)
        my_lang_combo = ttk.Combobox(
            lang_grid, 
            textvariable=self.my_lang_var,
            values=my_lang_options, 
            state="readonly", 
            width=25
        )
        my_lang_combo.grid(row=0, column=1, padx=(0, 20), pady=5)
        my_lang_combo.bind('<<ComboboxSelected>>', self._on_my_language_changed)
        
        # Target language
        tk.Label(
            lang_grid, 
            text="Teammate's Language:", 
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        target_lang_code = self.config.get("translation", "target_language", "es")
        target_lang_info = GAMING_LANGUAGES.get(target_lang_code, {"name": "Spanish", "flag": "🇪🇸"})
        target_lang_display = f"{target_lang_info['flag']} {target_lang_info['name']}"
        
        self.target_lang_var = tk.StringVar(value=target_lang_display)
        target_lang_combo = ttk.Combobox(
            lang_grid, 
            textvariable=self.target_lang_var,
            values=my_lang_options, 
            state="readonly", 
            width=25
        )
        target_lang_combo.grid(row=0, column=3, pady=5)
        target_lang_combo.bind('<<ComboboxSelected>>', self._on_target_language_changed)
        
        # Auto-detect
        auto_frame = tk.Frame(lang_frame, bg=UI_COLORS["CARD_BG"])
        auto_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.auto_detect_var = tk.BooleanVar(
            value=self.config.get_bool("translation", "auto_detect", True)
        )
        auto_cb = tk.Checkbutton(
            auto_frame, 
            text="🔍 Auto-detect teammate's language",
            variable=self.auto_detect_var, 
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            selectcolor=UI_COLORS["BG_COLOR"], 
            font=("Segoe UI", 10),
            command=self._on_auto_detect_changed
        )
        auto_cb.pack(side=tk.LEFT)
    
    def _create_enhanced_control_section(self, parent):
        """Create enhanced control section with volume-aware controls"""
        control_frame = tk.Frame(parent, bg=UI_COLORS["BG_COLOR"])
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Main controls
        main_controls = tk.Frame(control_frame, bg=UI_COLORS["BG_COLOR"])
        main_controls.pack()
        
        self.listen_btn = tk.Button(
            main_controls, 
            text="🎤 Start Listening",
            command=self._toggle_listening,
            bg=UI_COLORS["SUCCESS_COLOR"], 
            fg="white",
            font=("Segoe UI", 14, "bold"), 
            bd=0,
            padx=25, 
            pady=12, 
            width=18
        )
        self.listen_btn.pack(side=tk.LEFT, padx=10)
        
        self.overlay_btn = tk.Button(
            main_controls, 
            text="🎮 Show Overlay",
            command=self.overlay.toggle_overlay,
            bg=UI_COLORS["ACCENT_COLOR"], 
            fg="white",
            font=("Segoe UI", 14, "bold"), 
            bd=0,
            padx=25, 
            pady=12, 
            width=18
        )
        self.overlay_btn.pack(side=tk.LEFT, padx=10)
        
        # Add volume test button
        volume_test_btn = tk.Button(
            main_controls,
            text="🔊 Test Output",
            command=self._test_output_volume,
            bg=UI_COLORS["WARNING_COLOR"],
            fg="white",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=15,
            pady=12
        )
        volume_test_btn.pack(side=tk.LEFT, padx=10)
        
        # Recording indicator with level display
        indicator_frame = tk.Frame(control_frame, bg=UI_COLORS["BG_COLOR"])
        indicator_frame.pack(pady=(10, 0))
        
        self.recording_var = tk.StringVar(value="")
        recording_label = tk.Label(
            indicator_frame, 
            textvariable=self.recording_var,
            bg=UI_COLORS["BG_COLOR"], 
            fg=UI_COLORS["ERROR_COLOR"],
            font=("Segoe UI", 12, "bold")
        )
        recording_label.pack()
        
        # Live audio level display when listening
        self.live_level_var = tk.StringVar(value="")
        live_level_label = tk.Label(
            indicator_frame,
            textvariable=self.live_level_var,
            bg=UI_COLORS["BG_COLOR"],
            fg=UI_COLORS["ACCENT_COLOR"],
            font=("Segoe UI", 10)
        )
        live_level_label.pack()
    
    def _test_output_volume(self):
        """Test output volume with a sample sound"""
        try:
            # Get current output volume
            if self.audio_section:
                output_volume = self.audio_section.get_output_volume()
                
                if output_volume == 0:
                    self._update_status("Output is muted - unmute to test volume")
                    return
                
                # Test with text-to-speech
                test_text = f"Output volume test at {int(output_volume * 100)} percent"
                
                if self.voice_synthesizer:
                    # Temporarily set TTS volume
                    if hasattr(self.voice_synthesizer, 'set_volume'):
                        self.voice_synthesizer.set_volume(output_volume)
                    
                    self.voice_synthesizer.speak_text(test_text, "en")
                
                self._update_status(f"Output volume test: {int(output_volume * 100)}%")
            else:
                # Fallback: system beep
                import winsound
                winsound.Beep(440, 500)
                self._update_status("Output volume test (system beep)")
                
        except Exception as e:
            self.logger.error(f"Error testing output volume: {e}")
            self._update_status("Output volume test failed")
    
    def _create_conversation_section(self, parent):
        """Create conversation display section"""
        conv_frame = tk.LabelFrame(
            parent, 
            text="💬 Conversation",
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 12, "bold"),
            bd=2, 
            relief=tk.GROOVE
        )
        conv_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Conversation display
        conv_display = tk.Frame(conv_frame, bg=UI_COLORS["CARD_BG"])
        conv_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.conversation_text = tk.Text(
            conv_display, 
            bg=UI_COLORS["BG_COLOR"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Consolas", 10), 
            wrap=tk.WORD,
            state=tk.DISABLED, 
            padx=10, 
            pady=10
        )
        
        scrollbar = tk.Scrollbar(conv_display, command=self.conversation_text.yview)
        self.conversation_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Response input
        response_frame = tk.Frame(conv_frame, bg=UI_COLORS["CARD_BG"])
        response_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            response_frame, 
            text="💬 Your Response:", 
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        
        input_area = tk.Frame(response_frame, bg=UI_COLORS["CARD_BG"])
        input_area.pack(fill=tk.X)
        
        self.response_entry = tk.Entry(
            input_area, 
            bg=UI_COLORS["BG_COLOR"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 12), 
            relief=tk.FLAT, 
            bd=5
        )
        self.response_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        self.response_entry.bind('<Return>', self._translate_and_speak)
        
        speak_btn = tk.Button(
            input_area, 
            text="🔊", 
            command=self._speak_response_text,
            bg=UI_COLORS["ACCENT_COLOR"], 
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            bd=0, 
            width=3, 
            height=1
        )
        speak_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        translate_btn = tk.Button(
            input_area, 
            text="🌐", 
            command=self._translate_and_speak,
            bg=UI_COLORS["SUCCESS_COLOR"], 
            fg="white", 
            font=("Segoe UI", 12, "bold"),
            bd=0, 
            width=3, 
            height=1
        )
        translate_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_status_section(self, parent):
        """Create status bar"""
        status_frame = tk.Frame(parent, bg=UI_COLORS["BG_COLOR"])
        status_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar()
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var,
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"], 
            font=("Segoe UI", 10),
            anchor=tk.W, 
            padx=10, 
            pady=5, 
            relief=tk.SUNKEN
        )
        status_label.pack(fill=tk.X)
    
    def _setup_hotkeys(self):
        """Setup keyboard shortcuts"""
        try:
            # Basic hotkeys (simplified to avoid the complex config issues)
            self.root.bind('<Control-l>', lambda e: self._toggle_listening())
            self.root.bind('<Control-o>', lambda e: self.overlay.toggle_overlay())
            self.root.bind('<Control-t>', lambda e: self._translate_and_speak())
            self.root.bind('<Escape>', lambda e: self.overlay.hide_overlay())
            self.root.bind('<Control-s>', lambda e: self._save_session())
            self.root.bind('<Control-n>', lambda e: self._new_session())
            
            self.logger.info("Hotkeys configured")
        except Exception as e:
            self.logger.error(f"Error setting up hotkeys: {e}")
    
    def _toggle_listening(self):
        """Toggle voice recognition on/off"""
        if self.is_listening:
            self._stop_listening()
        else:
            self._start_listening()
    
    def _start_listening(self):
        """Enhanced start listening with volume monitoring"""
        if self.selected_device is None:
            self._update_status("Please select a microphone device first")
            return
        
        # Get input sensitivity setting
        if self.audio_section:
            input_sensitivity = self.audio_section.get_input_volume()
            
            if input_sensitivity == 0:
                self._update_status("Input is muted - unmute to start listening")
                return
        else:
            input_sensitivity = self.input_volume
        
        success = self.voice_recognizer.start_listening(self.selected_device, self._on_voice_recognized)
        
        if success:
            self.is_listening = True
            self.listen_btn.config(text="🛑 Stop Listening", bg=UI_COLORS["ERROR_COLOR"])
            self.recording_var.set("● Recording")
            self.live_level_var.set("Monitoring audio levels...")
            sensitivity_text = f" with {int(input_sensitivity * 100)}% sensitivity"
            self._update_status(f"Listening{sensitivity_text}")
        else:
            self._update_status("Failed to start listening - check your microphone")
    
    def _stop_listening(self):
        """Enhanced stop listening"""
        if hasattr(self, 'voice_recognizer'):
            self.voice_recognizer.stop_listening()
        
        self.is_listening = False
        self.listen_btn.config(text="🎤 Start Listening", bg=UI_COLORS["SUCCESS_COLOR"])
        self.recording_var.set("")
        self.live_level_var.set("")
        self._update_status("Listening stopped")
    
    def _on_voice_recognized(self, text):
        """Callback when voice is recognized"""
        if not text:
            return
        
        # Get language settings from config
        my_language = None
        for code, info in GAMING_LANGUAGES.items():
            if f"{info['flag']} {info['name']}" == self.my_lang_var.get():
                my_language = code
                break
        
        target_language = None
        for code, info in GAMING_LANGUAGES.items():
            if f"{info['flag']} {info['name']}" == self.target_lang_var.get():
                target_language = code
                break
        
        # Detect language if auto-detect is enabled
        detected_lang = my_language
        if self.auto_detect_var.get():
            detected_lang = self.translator.detect_language(text)
        
        # Translate text to target language
        translation = None
        if detected_lang != target_language:
            translation = self.translator.translate_text(text, target_language, detected_lang)
        
        # Create voice message
        message = VoiceMessage(text, detected_lang, is_outgoing=True, translation=translation)
        
        # Add to session
        self.session_manager.add_message(message)
        
        # Update conversation display
        self._add_conversation_message(message)
        
        # Update overlay
        self.overlay.add_message(message)
        
        # Speak translated text with current output volume
        if translation and self.voice_synthesizer:
            # Apply current output volume
            if hasattr(self.voice_synthesizer, 'set_volume'):
                output_volume = self.audio_section.get_output_volume() if self.audio_section else self.output_volume
                self.voice_synthesizer.set_volume(output_volume)
            
            self.voice_synthesizer.speak_text(translation, target_language)
    
    def _translate_and_speak(self, event=None):
        """Translate and speak text from main window entry"""
        text = self.response_entry.get().strip()
        if not text:
            return
        
        self._translate_and_speak_text(text)
        self.response_entry.delete(0, tk.END)
    
    def _translate_and_speak_from_overlay(self, text):
        """Translate and speak text from overlay entry"""
        self._translate_and_speak_text(text)
    
    def _translate_and_speak_text(self, text):
        """Common method for translating and speaking text"""
        # Get language settings
        my_language = None
        for code, info in GAMING_LANGUAGES.items():
            if f"{info['flag']} {info['name']}" == self.my_lang_var.get():
                my_language = code
                break
        
        target_language = None
        for code, info in GAMING_LANGUAGES.items():
            if f"{info['flag']} {info['name']}" == self.target_lang_var.get():
                target_language = code
                break
        
        # Translate text to target language
        translation = self.translator.translate_text(text, target_language, my_language)
        
        # Create voice message
        message = VoiceMessage(text, my_language, is_outgoing=True, translation=translation)
        
        # Add to session
        self.session_manager.add_message(message)
        
        # Update conversation display
        self._add_conversation_message(message)
        
        # Update overlay
        self.overlay.add_message(message)
        
        # Speak translated text with current output volume
        if translation and self.voice_synthesizer:
            # Apply current output volume
            if hasattr(self.voice_synthesizer, 'set_volume'):
                output_volume = self.audio_section.get_output_volume() if self.audio_section else self.output_volume
                self.voice_synthesizer.set_volume(output_volume)
            
            self.voice_synthesizer.speak_text(translation, target_language)
    
    def _speak_response_text(self, event=None):
        """Speak response text without translation"""
        text = self.response_entry.get().strip()
        if text:
            # Get language settings
            my_language = None
            for code, info in GAMING_LANGUAGES.items():
                if f"{info['flag']} {info['name']}" == self.my_lang_var.get():
                    my_language = code
                    break
            
            # Apply current output volume
            if hasattr(self.voice_synthesizer, 'set_volume'):
                output_volume = self.audio_section.get_output_volume() if self.audio_section else self.output_volume
                self.voice_synthesizer.set_volume(output_volume)
            
            self.voice_synthesizer.speak_text(text, my_language)
    
    def _speak_response_from_overlay(self, text):
        """Speak response text from overlay without translation"""
        if text:
            # Get language settings
            my_language = None
            for code, info in GAMING_LANGUAGES.items():
                if f"{info['flag']} {info['name']}" == self.my_lang_var.get():
                    my_language = code
                    break
            
            # Apply current output volume
            if hasattr(self.voice_synthesizer, 'set_volume'):
                output_volume = self.audio_section.get_output_volume() if self.audio_section else self.output_volume
                self.voice_synthesizer.set_volume(output_volume)
            
            self.voice_synthesizer.speak_text(text, my_language)
    
    def _add_conversation_message(self, message):
        """Add message to the conversation display"""
        try:
            self.conversation_text.config(state=tk.NORMAL)
            
            # Format timestamp
            timestamp = message.timestamp.strftime("%H:%M:%S")
            
            # Determine speaker and colors
            if message.is_outgoing:
                speaker = "You"
                speaker_color = UI_COLORS["SUCCESS_COLOR"]
            else:
                speaker = "Teammate"
                speaker_color = UI_COLORS["ACCENT_COLOR"]
            
            # Insert timestamp and speaker
            self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.conversation_text.insert(tk.END, f"{speaker}: ", "speaker")
            
            # Insert original text
            lang_code = message.language
            lang_name = GAMING_LANGUAGES.get(lang_code, {}).get('name', lang_code)
            lang_flag = GAMING_LANGUAGES.get(lang_code, {}).get('flag', '🌐')
            
            self.conversation_text.insert(tk.END, f"{message.text} ")
            self.conversation_text.insert(tk.END, f"({lang_flag} {lang_name})\n", "language")
            
            # Insert translation if available
            if message.translation:
                self.conversation_text.insert(tk.END, f"   → {message.translation}\n", "translation")
            else:
                self.conversation_text.insert(tk.END, "\n")
            
            # Configure tags
            self.conversation_text.tag_configure("timestamp", foreground="#888888")
            self.conversation_text.tag_configure("speaker", foreground=speaker_color, font=("Segoe UI", 10, "bold"))
            self.conversation_text.tag_configure("language", foreground="#888888", font=("Segoe UI", 8))
            self.conversation_text.tag_configure("translation", foreground=UI_COLORS["ACCENT_COLOR"])
            
            # Scroll to bottom
            self.conversation_text.see(tk.END)
            self.conversation_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error adding conversation message: {e}")
    
    def _update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.logger.info(message)
    
    def _on_my_language_changed(self, event=None):
        """Handle my language selection change"""
        selection = self.my_lang_var.get()
        for code, info in GAMING_LANGUAGES.items():
            if f"{info['flag']} {info['name']}" == selection:
                # Save to config
                self.config.set("translation", "my_language", code)
                self.config.save()
                
                self._update_status(f"Your language set to: {selection}")
                break
    
    def _on_target_language_changed(self, event=None):
        """Handle target language selection change"""
        selection = self.target_lang_var.get()
        for code, info in GAMING_LANGUAGES.items():
            if f"{info['flag']} {info['name']}" == selection:
                # Save to config
                self.config.set("translation", "target_language", code)
                self.config.save()
                
                self._update_status(f"Teammate's language set to: {selection}")
                break
    
    def _on_auto_detect_changed(self):
        """Handle auto-detect checkbox change"""
        auto_detect = self.auto_detect_var.get()
        
        # Save to config
        self.config.set("translation", "auto_detect", str(auto_detect))
        self.config.save()
        
        self._update_status(f"Auto language detection: {'enabled' if auto_detect else 'disabled'}")
    
    def _new_session(self, event=None):
        """Start a new session"""
        if self.session_manager.messages and messagebox.askyesno(
            "Save Current Session", 
            "Do you want to save the current session before starting a new one?"
        ):
            self._save_session()
        
        # Clear session
        self.session_manager.clear()
        
        # Clear conversation display
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.delete(1.0, tk.END)
        self.conversation_text.config(state=tk.DISABLED)
        
        # Clear overlay
        self.overlay.clear_messages()
        
        self._update_status("New session started")
    
    def _save_session(self, event=None):
        """Save current session to file"""
        if not self.session_manager.messages:
            messagebox.showinfo("No Conversation", "There's no conversation to save.")
            return
        
        try:
            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"), 
                    ("All files", "*.*")
                ],
                title="Save Session"
            )
            
            if not filename:
                return
            
            # Save session
            success = self.session_manager.save_session(filename)
            
            if success:
                self._update_status(f"Session saved to {filename}")
                messagebox.showinfo("Success", f"Session saved successfully to:\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to save session")
            
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            messagebox.showerror("Error", f"Failed to save session: {str(e)}")
    
    def _load_session(self, event=None):
        """Load session from file"""
        try:
            # Check if current session should be saved
            if self.session_manager.messages and messagebox.askyesno(
                "Save Current Session", 
                "Do you want to save the current session before loading a new one?"
            ):
                self._save_session()
            
            # Ask for file location
            filename = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"), 
                    ("All files", "*.*")
                ],
                title="Load Session"
            )
            
            if not filename:
                return
            
            # Load session
            success = self.session_manager.load_session(filename)
            
            if success:
                # Clear display
                self.conversation_text.config(state=tk.NORMAL)
                self.conversation_text.delete(1.0, tk.END)
                self.conversation_text.config(state=tk.DISABLED)
                
                # Display loaded messages
                for message in self.session_manager.messages:
                    self._add_conversation_message(message)
                
                # Update overlay
                self.overlay.clear_messages()
                for message in self.session_manager.messages[-5:]:  # Only show last 5 messages
                    self.overlay.add_message(message)
                
                self._update_status(f"Session loaded from {filename}")
            else:
                messagebox.showerror("Error", "Failed to load session")
            
        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")
    
    def _export_session(self, format_type):
        """Export session in specified format"""
        if not self.session_manager.messages:
            messagebox.showinfo("No Conversation", "There's no conversation to export.")
            return
        
        try:
            # Ask for file location
            default_ext = EXPORT_FORMATS.get(format_type, {}).get("extension", ".txt")
            filename = filedialog.asksaveasfilename(
                defaultextension=default_ext,
                filetypes=[
                    (f"{EXPORT_FORMATS.get(format_type, {}).get('name', 'Text')} files", f"*{default_ext}"),
                    ("All files", "*.*")
                ],
                title=f"Export as {EXPORT_FORMATS.get(format_type, {}).get('name', 'Text')}"
            )
            
            if not filename:
                return
            
            # Export session
            success = self.session_manager.export_session(format_type, filename)
            
            if success:
                self._update_status(f"Session exported to {filename}")
                messagebox.showinfo("Success", f"Session exported successfully to:\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to export session")
            
        except Exception as e:
            self.logger.error(f"Error exporting session: {e}")
            messagebox.showerror("Error", f"Failed to export session: {str(e)}")
    
    def _show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog not implemented yet")
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "Toggle Listening: Ctrl+L\n"
            "Toggle Game Overlay: Ctrl+O\n"
            "Translate and Speak: Ctrl+T\n"
            "Save Conversation: Ctrl+S\n"
            "Hide Overlay: Escape\n"
            "New Session: Ctrl+N\n"
            "Load Session: Ctrl+O\n"
            "Enter: Send Text in Text Box"
        )
    
    def _check_dependencies(self):
        """Check for missing dependencies"""
        missing = []
        
        # Check for audio libraries
        try:
            import pyaudio
            import speech_recognition
        except ImportError:
            missing.append("Audio libraries (pyaudio, speech_recognition)")
        
        # Check for translation library
        try:
            from googletrans import Translator
        except ImportError:
            missing.append("Translation library (googletrans==4.0.0-rc1)")
        
        # Check for TTS libraries
        try:
            import pyttsx3
        except ImportError:
            try:
                from gtts import gTTS
                import pygame
            except ImportError:
                missing.append("Text-to-Speech libraries (pyttsx3 or gtts+pygame)")
        
        # Check for WhisperX
        try:
            import whisperx
        except ImportError:
            missing.append("WhisperX (optional for improved recognition)")
        
        # Check for reportlab (PDF export)
        try:
            from reportlab.lib.pagesizes import letter
        except ImportError:
            missing.append("reportlab (optional for PDF export)")
        
        # Display results
        if missing:
            message = "Missing dependencies:\n\n"
            for m in missing:
                message += f"- {m}\n"
            
            message += "\nInstallation commands:\n"
            message += "pip install pyaudio speechrecognition googletrans==4.0.0-rc1 pyttsx3\n"
            message += "pip install gtts pygame reportlab\n"
            message += "pip install git+https://github.com/m-bain/whisperx.git"
            
            messagebox.warning(self.root, "Missing Dependencies", message)
        else:
            messagebox.showinfo("Dependencies", "All required dependencies are installed.")
    
    def _show_first_run_help(self):
        """Show help dialog on first run"""
        messagebox.showinfo(
            f"Welcome to {APP_NAME}",
            f"Welcome to {APP_NAME} v{APP_VERSION}!\n\n"
            "Quick Start Guide:\n"
            "1. Select your microphone and test the audio levels\n"
            "2. Adjust input/output volume as needed\n"
            "3. Choose your language and your teammate's language\n"
            "4. Click 'Start Listening' to begin voice recognition\n"
            "5. Use the overlay during games with Ctrl+O\n\n"
            "For more help, check the Help menu."
        )
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            f"About {APP_NAME}",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "A real-time voice translator for gaming.\n\n"
            "Features:\n"
            "- Real-time voice recognition with WhisperX\n"
            "- Visual audio level monitoring\n"
            "- Volume controls for input/output\n"
            "- Automatic language detection\n"
            "- Fast translation with LibreTranslate support\n"
            "- In-game overlay\n"
            "- Session export to multiple formats"
        )
    
    def _on_close(self):
        """Handle application close"""
        # Stop listening if active
        if self.is_listening:
            self._stop_listening()
        
        # Clean up audio section if it exists
        if self.audio_section:
            self.audio_section.cleanup()
        
        # Ask to save session if there are messages
        if self.session_manager.messages and self.config.get_bool("session", "save_session_on_exit", True):
            if messagebox.askyesno(
                "Save Conversation", 
                "Do you want to save the conversation before exiting?"
            ):
                self._save_session()
        
        # Save window position and size
        geometry = self.root.geometry()
        self.config.set("ui", "window_size", geometry)
        self.config.save()
        
        # Destroy main window
        self.root.destroy()
        
        self.logger.info("Application closed")