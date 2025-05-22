"""
In-game overlay for the Gaming Voice Chat Translator
"""

import logging
import tkinter as tk

from gaming_translator.utils.constants import UI_COLORS

class GamingOverlay:
    """Floating overlay for in-game translation"""
    
    def __init__(self, parent_app, config):
        """Initialize the overlay with parent application and configuration"""
        self.logger = logging.getLogger("gaming_translator.ui.overlay")
        self.parent_app = parent_app
        self.config = config
        self.overlay = None
        self.is_visible = False
        self.messages = []
        
        # Load overlay settings
        self.opacity = config.get_float("overlay", "opacity", 0.9)
        self.width = config.get_int("overlay", "width", 400)
        self.height = config.get_int("overlay", "height", 250)
        self.position_x = config.get_int("overlay", "position_x", 100)
        self.position_y = config.get_int("overlay", "position_y", 100)
        self.font_size = config.get_int("overlay", "font_size", 10)
        self.max_messages = config.get_int("overlay", "max_messages", 5)
        
        self.logger.info("Overlay initialized")
    
    def create_overlay(self):
        """Create the overlay window"""
        try:
            self.overlay = tk.Toplevel()
            self.overlay.title("Gaming Translator")
            self.overlay.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
            self.overlay.configure(bg=UI_COLORS["BG_COLOR"])
            
            # Set overlay properties
            self.overlay.attributes('-alpha', self.opacity)
            self.overlay.attributes('-topmost', True)
            self.overlay.overrideredirect(True)  # Remove window decorations
            
            # Setup UI
            self._setup_ui()
            self._make_draggable()
            
            # Update display with existing messages
            self._update_display()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create overlay: {e}")
            return False
    
    def _setup_ui(self):
        """Setup overlay UI"""
        main_frame = tk.Frame(self.overlay, bg=UI_COLORS["BG_COLOR"], bd=2, relief=tk.RAISED)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Header
        header = tk.Frame(main_frame, bg=UI_COLORS["CARD_BG"], height=25)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header, 
            text="🎮 Voice Translator", 
            bg=UI_COLORS["CARD_BG"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT, padx=5, pady=2)
        
        # Add minimize button
        min_btn = tk.Button(
            header, 
            text="_", 
            bg=UI_COLORS["ACCENT_COLOR"], 
            fg="white",
            font=("Arial", 8, "bold"), 
            bd=0, 
            width=2,
            command=self.minimize_overlay
        )
        min_btn.pack(side=tk.RIGHT, padx=2)
        
        # Add close button
        close_btn = tk.Button(
            header, 
            text="✕", 
            bg=UI_COLORS["ERROR_COLOR"], 
            fg="white",
            font=("Arial", 8, "bold"), 
            bd=0, 
            width=2,
            command=self.hide_overlay
        )
        close_btn.pack(side=tk.RIGHT, padx=2)
        
        # Messages area
        self.messages_text = tk.Text(
            main_frame, 
            bg=UI_COLORS["BG_COLOR"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Consolas", self.font_size), 
            wrap=tk.WORD, 
            bd=0,
            padx=5, 
            pady=5, 
            state=tk.DISABLED, 
            height=8
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input area
        input_frame = tk.Frame(main_frame, bg=UI_COLORS["CARD_BG"], height=35)
        input_frame.pack(fill=tk.X)
        input_frame.pack_propagate(False)
        
        self.response_entry = tk.Entry(
            input_frame, 
            bg=UI_COLORS["BG_COLOR"], 
            fg=UI_COLORS["TEXT_COLOR"],
            font=("Segoe UI", 10), 
            relief=tk.FLAT, 
            bd=3
        )
        self.response_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.response_entry.bind('<Return>', self._send_response)
        
        speak_btn = tk.Button(
            input_frame, 
            text="🔊", 
            bg=UI_COLORS["ACCENT_COLOR"], 
            fg="white",
            font=("Arial", 10, "bold"), 
            bd=0, 
            width=3,
            command=self._speak_response
        )
        speak_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.header = header
    
    def _make_draggable(self):
        """Make the overlay window draggable"""
        def start_drag(event):
            self.overlay.x = event.x
            self.overlay.y = event.y
        
        def on_drag(event):
            try:
                x = self.overlay.winfo_pointerx() - self.overlay.x
                y = self.overlay.winfo_pointery() - self.overlay.y
                self.overlay.geometry(f"+{x}+{y}")
                
                # Save position for next time
                self.position_x = x
                self.position_y = y
                self.config.set("overlay", "position_x", str(x))
                self.config.set("overlay", "position_y", str(y))
                self.config.save()
            except tk.TclError:
                pass
        
        self.header.bind("<Button-1>", start_drag)
        self.header.bind("<B1-Motion>", on_drag)
    
    def show_overlay(self):
        """Show the overlay window"""
        if not self.overlay:
            if not self.create_overlay():
                return False
        
        self.overlay.deiconify()
        self.overlay.lift()
        self.is_visible = True
        
        self.logger.info("Overlay shown")
        return True
    
    def hide_overlay(self):
        """Hide the overlay window"""
        if self.overlay:
            self.overlay.withdraw()
            self.is_visible = False
            self.logger.info("Overlay hidden")
    
    def minimize_overlay(self):
        """Minimize the overlay to a small floating button"""
        if not self.overlay:
            return
        
        # Hide the main overlay
        self.overlay.withdraw()
        
        # Create a small floating button
        self.mini_button = tk.Toplevel()
        self.mini_button.geometry(f"30x30+{self.position_x}+{self.position_y}")
        self.mini_button.overrideredirect(True)
        self.mini_button.attributes('-topmost', True)
        self.mini_button.attributes('-alpha', self.opacity)
        
        button = tk.Button(
            self.mini_button,
            text="🎮",
            bg=UI_COLORS["ACCENT_COLOR"],
            fg="white",
            font=("Arial", 10, "bold"),
            command=self._restore_from_mini,
            bd=0
        )
        button.pack(fill=tk.BOTH, expand=True)
        
        # Make mini button draggable
        def start_mini_drag(event):
            self.mini_button.x = event.x
            self.mini_button.y = event.y
        
        def on_mini_drag(event):
            try:
                x = self.mini_button.winfo_pointerx() - self.mini_button.x
                y = self.mini_button.winfo_pointery() - self.mini_button.y
                self.mini_button.geometry(f"+{x}+{y}")
                
                # Save position for both overlay and mini button
                self.position_x = x
                self.position_y = y
            except tk.TclError:
                pass
        
        button.bind("<Button-1>", start_mini_drag)
        button.bind("<B1-Motion>", on_mini_drag)
        
        self.is_visible = False
        self.is_minimized = True
        
        self.logger.info("Overlay minimized")
    
    def _restore_from_mini(self):
        """Restore overlay from minimized state"""
        if hasattr(self, 'mini_button'):
            # Get position from mini button
            try:
                x = self.mini_button.winfo_x()
                y = self.mini_button.winfo_y()
                self.position_x = x
                self.position_y = y
            except:
                pass
            
            # Destroy mini button
            self.mini_button.destroy()
            delattr(self, 'mini_button')
        
        # Show overlay in the same position
        if not self.overlay:
            self.create_overlay()
        else:
            self.overlay.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
            self.overlay.deiconify()
        
        self.is_visible = True
        self.is_minimized = False
        
        self.logger.info("Overlay restored from minimized state")
    
    def toggle_overlay(self):
        """Toggle visibility of the overlay window"""
        if hasattr(self, 'is_minimized') and self.is_minimized:
            self._restore_from_mini()
        elif self.is_visible:
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def add_message(self, message):
        """Add a message to the overlay display"""
        if not self.overlay and not self.show_overlay():
            return
        
        self.messages.append(message)
        if len(self.messages) > 10:  # Keep last 10 messages max
            self.messages = self.messages[-10:]
        
        self._update_display()
    
    def clear_messages(self):
        """Clear all messages from the overlay"""
        self.messages = []
        self._update_display()
    
    def _update_display(self):
        """Update the messages display"""
        if not self.overlay:
            return
            
        try:
            self.messages_text.configure(state=tk.NORMAL)
            self.messages_text.delete(1.0, tk.END)
            
            # Display only the last few messages based on config
            display_messages = self.messages[-self.max_messages:] if len(self.messages) > self.max_messages else self.messages
            
            for msg in display_messages:
                timestamp = msg.timestamp.strftime("%H:%M")
                speaker = "You" if msg.is_outgoing else "Teammate"
                
                # Format with colors using tags
                self.messages_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
                self.messages_text.insert(tk.END, f"{speaker}: ", "speaker")
                self.messages_text.insert(tk.END, f"{msg.text}\n", "original")
                
                if msg.translation:
                    self.messages_text.insert(tk.END, f"         → ", "arrow")
                    self.messages_text.insert(tk.END, f"{msg.translation}\n", "translation")
            
            # Configure tags for styling
            self.messages_text.tag_configure("timestamp", foreground="#888888")
            self.messages_text.tag_configure("speaker", foreground=UI_COLORS["ACCENT_COLOR"], font=("Consolas", self.font_size, "bold"))
            self.messages_text.tag_configure("original", foreground=UI_COLORS["TEXT_COLOR"])
            self.messages_text.tag_configure("arrow", foreground="#888888")
            self.messages_text.tag_configure("translation", foreground=UI_COLORS["SUCCESS_COLOR"])
            
            self.messages_text.configure(state=tk.DISABLED)
            self.messages_text.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Error updating overlay: {e}")
    
    def _send_response(self, event=None):
        """Send response text to parent application for translation"""
        text = self.response_entry.get().strip()
        if text and hasattr(self.parent_app, '_translate_and_speak_from_overlay'):
            self.response_entry.delete(0, tk.END)
            self.parent_app._translate_and_speak_from_overlay(text)
    
    def _speak_response(self):
        """Send response text to parent application for speaking"""
        text = self.response_entry.get().strip()
        if text and hasattr(self.parent_app, '_speak_response_from_overlay'):
            self.parent_app._speak_response_from_overlay(text)
    
    def set_opacity(self, opacity):
        """Set the opacity of the overlay"""
        self.opacity = float(opacity)
        if self.overlay:
            self.overlay.attributes('-alpha', self.opacity)
        
        # Save to config
        self.config.set("overlay", "opacity", str(self.opacity))
        self.config.save()
    
    def set_size(self, width, height):
        """Set the size of the overlay"""
        self.width = int(width)
        self.height = int(height)
        
        if self.overlay:
            self.overlay.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
        
        # Save to config
        self.config.set("overlay", "width", str(self.width))
        self.config.set("overlay", "height", str(self.height))
        self.config.save()
    
    def set_font_size(self, size):
        """Set the font size for the messages"""
        self.font_size = int(size)
        
        if self.overlay and hasattr(self, 'messages_text'):
            self.messages_text.configure(font=("Consolas", self.font_size))
            self._update_display()  # Refresh display to apply new font
        
        # Save to config
        self.config.set("overlay", "font_size", str(self.font_size))
        self.config.save()
    
    def set_max_messages(self, count):
        """Set the maximum number of messages to display"""
        self.max_messages = int(count)
        self._update_display()  # Refresh to apply new limit
        
        # Save to config
        self.config.set("overlay", "max_messages", str(self.max_messages))
        self.config.save()