"""
AutoHotkey integration for sending translated text to in-game chat
"""

import os
import time
import logging
import subprocess
import tempfile
import threading
from pathlib import Path

class AutoHotkeyBridge:
    """Bridge to AutoHotkey for sending keystrokes to games"""
    
    def __init__(self, config):
        """Initialize the AutoHotkey bridge"""
        self.logger = logging.getLogger("gaming_translator.utils.autohotkey_bridge")
        self.config = config
        
        # Check if AutoHotkey is installed
        self.ahk_path = None
        self._find_autohotkey()
        
        # Default key settings
        self.chat_key = config.get("autohotkey", "chat_key", "Enter")
        self.team_chat_key = config.get("autohotkey", "team_chat_key", "y")
        self.all_chat_key = config.get("autohotkey", "all_chat_key", "t")
        self.send_key = config.get("autohotkey", "send_key", "Enter")
        
        # Delay settings
        self.pre_type_delay = config.get_float("autohotkey", "pre_type_delay", 0.1)
        self.post_type_delay = config.get_float("autohotkey", "post_type_delay", 0.1)
        
        self.logger.info(f"AutoHotkey bridge initialized, AHK found: {self.ahk_path is not None}")
    
    def _find_autohotkey(self):
        """Find the AutoHotkey executable"""
        # Common paths for AutoHotkey
        paths_to_check = [
            # Windows program files
            r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
            r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
            # User downloads (common portable location)
            os.path.expanduser("~/Downloads/AutoHotkey/AutoHotkey.exe"),
        ]
        
        # Check if AHK is in PATH
        try:
            result = subprocess.run(["where", "AutoHotkey"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  text=True)
            if result.returncode == 0:
                paths_to_check.insert(0, result.stdout.strip())
        except:
            pass
        
        # Check each path
        for path in paths_to_check:
            if os.path.exists(path):
                self.ahk_path = path
                self.logger.info(f"Found AutoHotkey at: {path}")
                return
        
        self.logger.warning("AutoHotkey not found, functionality will be limited")
    
    def is_available(self):
        """Check if AutoHotkey is available"""
        return self.ahk_path is not None
    
    def send_text_to_chat(self, text, chat_type="team"):
        """
        Send text to in-game chat
        
        Args:
            text (str): Text to send
            chat_type (str): Type of chat ('team', 'all', or 'custom')
        """
        if not self.is_available():
            self.logger.warning("AutoHotkey not available, cannot send text to chat")
            return False
        
        # Don't send empty text
        if not text or not text.strip():
            return False
        
        # Create and run AHK script in a separate thread
        threading.Thread(
            target=self._run_send_text_script,
            args=(text, chat_type),
            daemon=True
        ).start()
        
        return True
    
    def _run_send_text_script(self, text, chat_type):
        """Run AutoHotkey script to send text to chat"""
        try:
            # Create temporary AHK script
            script_content = self._create_send_text_script(text, chat_type)
            
            with tempfile.NamedTemporaryFile(suffix='.ahk', delete=False, mode='w') as temp_file:
                temp_filename = temp_file.name
                temp_file.write(script_content)
            
            # Run the script
            subprocess.run([self.ahk_path, temp_filename], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            
            # Clean up
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            self.logger.info(f"Sent text to {chat_type} chat: {text[:30]}...")
            
        except Exception as e:
            self.logger.error(f"Error sending text to chat: {e}")
    
    def _create_send_text_script(self, text, chat_type):
        """Create AutoHotkey script for sending text to chat"""
        # Set chat key based on type
        if chat_type == "team":
            chat_key = self.team_chat_key
        elif chat_type == "all":
            chat_key = self.all_chat_key
        else:  # custom or unknown
            chat_key = self.chat_key
        
        # Create script
        script = f"""
; Gaming Voice Chat Translator - AutoHotkey Script
; Generated automatically - DO NOT EDIT

#NoEnv
#SingleInstance force
SendMode Input
SetWorkingDir %A_ScriptDir%

; Wait for a moment to ensure the game is in focus
Sleep 200

; Press chat key
Send, {{{chat_key}}}

; Wait for chat to open
Sleep {int(self.pre_type_delay * 1000)}

; Type the text
SendRaw, {text}

; Wait before sending
Sleep {int(self.post_type_delay * 1000)}

; Press send key
Send, {{{self.send_key}}}

ExitApp
"""
        return script
    
    def simulate_hotkey(self, key_combination):
        """
        Simulate pressing a hotkey combination
        
        Args:
            key_combination (str): Key combination, e.g. "Alt+F4", "Ctrl+Shift+A"
        """
        if not self.is_available():
            self.logger.warning("AutoHotkey not available, cannot simulate hotkey")
            return False
        
        try:
            # Create temporary AHK script
            script = f"""
; Gaming Voice Chat Translator - AutoHotkey Script
; Generated automatically - DO NOT EDIT

#NoEnv
#SingleInstance force
SendMode Input

; Wait for a moment
Sleep 200

; Send hotkey
Send, {key_combination}

ExitApp
"""
            
            with tempfile.NamedTemporaryFile(suffix='.ahk', delete=False, mode='w') as temp_file:
                temp_filename = temp_file.name
                temp_file.write(script)
            
            # Run the script
            subprocess.run([self.ahk_path, temp_filename], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            
            # Clean up
            try:
                os.unlink(temp_filename)
            except:
                pass
            
            self.logger.info(f"Simulated hotkey: {key_combination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error simulating hotkey: {e}")
            return False
    
    def update_settings(self, chat_key=None, team_chat_key=None, all_chat_key=None,
                      send_key=None, pre_type_delay=None, post_type_delay=None):
        """Update AutoHotkey settings"""
        if chat_key:
            self.chat_key = chat_key
            self.config.set("autohotkey", "chat_key", chat_key)
        
        if team_chat_key:
            self.team_chat_key = team_chat_key
            self.config.set("autohotkey", "team_chat_key", team_chat_key)
        
        if all_chat_key:
            self.all_chat_key = all_chat_key
            self.config.set("autohotkey", "all_chat_key", all_chat_key)
        
        if send_key:
            self.send_key = send_key
            self.config.set("autohotkey", "send_key", send_key)
        
        if pre_type_delay is not None:
            self.pre_type_delay = float(pre_type_delay)
            self.config.set("autohotkey", "pre_type_delay", str(pre_type_delay))
        
        if post_type_delay is not None:
            self.post_type_delay = float(post_type_delay)
            self.config.set("autohotkey", "post_type_delay", str(post_type_delay))
        
        # Save settings
        self.config.save()
        
        self.logger.info("AutoHotkey settings updated")
    
    def suggest_game_settings(self, game_name):
        """
        Suggest keyboard settings for common games
        
        Args:
            game_name (str): Name of the game
        
        Returns:
            dict: Suggested settings for the game
        """
        game_name = game_name.lower()
        
        # Common game settings
        game_settings = {
            "valorant": {
                "team_chat_key": "y",
                "all_chat_key": "shift+y",
                "send_key": "Enter",
                "pre_type_delay": 0.1,
                "post_type_delay": 0.1
            },
            "league of legends": {
                "team_chat_key": "Enter",
                "all_chat_key": "shift+Enter",
                "send_key": "Enter",
                "pre_type_delay": 0.1,
                "post_type_delay": 0.1
            },
            "counter-strike": {
                "team_chat_key": "u",
                "all_chat_key": "y",
                "send_key": "Enter",
                "pre_type_delay": 0.15,
                "post_type_delay": 0.1
            },
            "fortnite": {
                "team_chat_key": "Enter",
                "all_chat_key": "Enter",
                "send_key": "Enter",
                "pre_type_delay": 0.2,
                "post_type_delay": 0.1
            },
            "minecraft": {
                "team_chat_key": "t",
                "all_chat_key": "t",
                "send_key": "Enter",
                "pre_type_delay": 0.1,
                "post_type_delay": 0.1
            },
            "dota 2": {
                "team_chat_key": "Enter",
                "all_chat_key": "shift+Enter",
                "send_key": "Enter",
                "pre_type_delay": 0.15,
                "post_type_delay": 0.1
            },
            "apex legends": {
                "team_chat_key": "Enter",
                "all_chat_key": "Enter",
                "send_key": "Enter",
                "pre_type_delay": 0.2,
                "post_type_delay": 0.1
            },
            "overwatch": {
                "team_chat_key": "Enter",
                "all_chat_key": "shift+Enter",
                "send_key": "Enter",
                "pre_type_delay": 0.15,
                "post_type_delay": 0.1
            }
        }
        
        # Try to find the game in our database
        for game_key, settings in game_settings.items():
            if game_key in game_name:
                return settings
        
        # Default settings if game not found
        return {
            "team_chat_key": "Enter",
            "all_chat_key": "t",
            "send_key": "Enter",
            "pre_type_delay": 0.15,
            "post_type_delay": 0.1
        }
    
    @staticmethod
    def install_info():
        """
        Get information about installing AutoHotkey
        
        Returns:
            dict: Installation information
        """
        return {
            "name": "AutoHotkey",
            "description": "Automation scripting language for Windows",
            "download_url": "https://www.autohotkey.com/download/",
            "instruction": """
1. Visit https://www.autohotkey.com/download/
2. Download the latest version of AutoHotkey
3. Run the installer and follow the instructions
4. Restart the Gaming Voice Chat Translator application
""",
            "docs_url": "https://www.autohotkey.com/docs/",
        }