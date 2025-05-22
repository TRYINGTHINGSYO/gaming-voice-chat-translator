"""
Enhanced audio controls with device selection, volume controls, and level monitoring
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Callable, Optional, List, Dict, Any


class EnhancedAudioSection(tk.Frame):
    """Enhanced audio section with device selection and volume controls"""
    
    def __init__(self, parent, device_change_callback: Callable = None,
                 input_volume_callback: Callable = None,
                 output_volume_callback: Callable = None):
        """Initialize the enhanced audio section
        
        Args:
            parent: Parent widget
            device_change_callback: Callback for device changes
            input_volume_callback: Callback for input volume changes
            output_volume_callback: Callback for output volume changes
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gaming_translator.ui.audio_controls")
        self.device_change_callback = device_change_callback
        self.input_volume_callback = input_volume_callback
        self.output_volume_callback = output_volume_callback
        
        # Audio devices
        self.audio_devices = []
        self.selected_device_index = None
        
        # Volume values
        self.input_volume = 0.8
        self.output_volume = 0.7
        
        # Setup UI
        self._setup_ui()
        
        # Load audio devices
        self._load_audio_devices()
        
        self.logger.info("Enhanced audio section initialized")
    
    def _setup_ui(self):
        """Setup the audio controls UI"""
        from gaming_translator.utils.constants import UI_COLORS
        
        self.configure(bg=UI_COLORS["BG_COLOR"])
        
        # Main audio frame
        audio_frame = tk.LabelFrame(
            self,
            text="🎧 Audio Settings",
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 12, "bold"),
            bd=2,
            relief=tk.GROOVE
        )
        audio_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Device selection section
        device_section = tk.Frame(audio_frame, bg=UI_COLORS["CARD_BG"])
        device_section.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            device_section,
            text="Microphone Device:",
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT)
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            device_section,
            textvariable=self.device_var,
            state="readonly",
            width=40
        )
        self.device_combo.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_change)
        
        # Refresh button
        refresh_btn = tk.Button(
            device_section,
            text="🔄",
            command=self._refresh_devices,
            bg=UI_COLORS["ACCENT_COLOR"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            width=3
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Volume controls section
        volume_section = tk.Frame(audio_frame, bg=UI_COLORS["CARD_BG"])
        volume_section.pack(fill=tk.X, padx=10, pady=5)
        
        # Input volume
        input_frame = tk.Frame(volume_section, bg=UI_COLORS["CARD_BG"])
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(
            input_frame,
            text="🎤 Input Sensitivity:",
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)
        
        self.input_scale = tk.Scale(
            input_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            highlightthickness=0,
            command=self._on_input_volume_change
        )
        self.input_scale.pack(fill=tk.X)
        self.input_scale.set(self.input_volume)
        
        # Output volume
        output_frame = tk.Frame(volume_section, bg=UI_COLORS["CARD_BG"])
        output_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(
            output_frame,
            text="🔊 Output Volume:",
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W)
        
        self.output_scale = tk.Scale(
            output_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            highlightthickness=0,
            command=self._on_output_volume_change
        )
        self.output_scale.pack(fill=tk.X)
        self.output_scale.set(self.output_volume)
        
        # Audio level display
        level_section = tk.Frame(audio_frame, bg=UI_COLORS["CARD_BG"])
        level_section.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            level_section,
            text="Audio Level:",
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT)
        
        # Audio level meter (simplified)
        self.level_var = tk.StringVar(value="■■■□□□□□□□ (No input)")
        level_label = tk.Label(
            level_section,
            textvariable=self.level_var,
            bg=UI_COLORS["CARD_BG"],
            fg=UI_COLORS["ACCENT_COLOR"],
            font=("Consolas", 10),
            anchor=tk.W
        )
        level_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def _load_audio_devices(self):
        """Load available audio devices"""
        try:
            from gaming_translator.core.voice_recognizer import list_audio_devices
            
            self.audio_devices = list_audio_devices()
            
            # Update combobox
            device_names = [f"{dev['index']}: {dev['name']}" for dev in self.audio_devices]
            self.device_combo['values'] = device_names
            
            # Select first device by default
            if self.audio_devices:
                self.device_combo.current(0)
                self.selected_device_index = self.audio_devices[0]['index']
            
            self.logger.info(f"Loaded {len(self.audio_devices)} audio devices")
            
        except Exception as e:
            self.logger.error(f"Error loading audio devices: {e}")
            # Provide fallback
            self.device_combo['values'] = ["0: Default Microphone"]
            self.device_combo.current(0)
            self.selected_device_index = 0
    
    def _refresh_devices(self):
        """Refresh the list of audio devices"""
        self._load_audio_devices()
        self.logger.info("Audio devices refreshed")
    
    def _on_device_change(self, event=None):
        """Handle device selection change"""
        try:
            selection = self.device_combo.current()
            if selection >= 0 and selection < len(self.audio_devices):
                self.selected_device_index = self.audio_devices[selection]['index']
                
                if self.device_change_callback:
                    self.device_change_callback(self.selected_device_index)
                
                self.logger.debug(f"Device changed to index {self.selected_device_index}")
                
        except Exception as e:
            self.logger.error(f"Error changing device: {e}")
    
    def _on_input_volume_change(self, value):
        """Handle input volume change"""
        try:
            self.input_volume = float(value)
            
            if self.input_volume_callback:
                self.input_volume_callback(self.input_volume)
                
        except Exception as e:
            self.logger.error(f"Error changing input volume: {e}")
    
    def _on_output_volume_change(self, value):
        """Handle output volume change"""
        try:
            self.output_volume = float(value)
            
            if self.output_volume_callback:
                self.output_volume_callback(self.output_volume)
                
        except Exception as e:
            self.logger.error(f"Error changing output volume: {e}")
    
    def set_input_volume(self, volume: float):
        """Set input volume programmatically"""
        self.input_volume = max(0.0, min(1.0, volume))
        self.input_scale.set(self.input_volume)
    
    def set_output_volume(self, volume: float):
        """Set output volume programmatically"""
        self.output_volume = max(0.0, min(1.0, volume))
        self.output_scale.set(self.output_volume)
    
    def get_input_volume(self) -> float:
        """Get current input volume"""
        return self.input_volume
    
    def get_output_volume(self) -> float:
        """Get current output volume"""
        return self.output_volume
    
    def get_selected_device_index(self) -> Optional[int]:
        """Get currently selected device index"""
        return self.selected_device_index
    
    def get_selected_device_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently selected device"""
        if self.selected_device_index is None:
            return None
        
        for device in self.audio_devices:
            if device['index'] == self.selected_device_index:
                return device
        
        return None
    
    def update_audio_level(self, level: float):
        """Update the audio level display
        
        Args:
            level: Audio level from 0.0 to 1.0
        """
        # Convert level to visual meter
        bars = int(level * 10)
        filled = "■" * bars
        empty = "□" * (10 - bars)
        
        if level > 0.1:
            status = "Recording"
        elif level > 0.05:
            status = "Input detected"
        else:
            status = "No input"
        
        meter = f"{filled}{empty} ({status})"
        self.level_var.set(meter)
    
    def cleanup(self):
        """Clean up audio resources"""
        # Stop any ongoing operations
        self.logger.info("Audio controls cleaned up")