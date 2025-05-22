"""
Session management for conversation history and export
"""

import os
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

class VoiceMessage:
    """Class representing a voice message with translation"""
    
    def __init__(self, text, language, is_outgoing=False, translation=None):
        """Initialize a voice message"""
        self.text = text
        self.language = language
        self.is_outgoing = is_outgoing
        self.translation = translation
        self.timestamp = datetime.now()
    
    def to_dict(self):
        """Convert the message to a dictionary for serialization"""
        return {
            "text": self.text,
            "language": self.language,
            "is_outgoing": self.is_outgoing,
            "translation": self.translation,
            "timestamp": self.timestamp.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        """Create a message from a dictionary"""
        message = VoiceMessage(
            text=data.get("text", ""),
            language=data.get("language", "en"),
            is_outgoing=data.get("is_outgoing", False),
            translation=data.get("translation")
        )
        
        # Parse timestamp if provided
        if "timestamp" in data:
            try:
                message.timestamp = datetime.fromisoformat(data["timestamp"])
            except ValueError:
                pass
        
        return message


class SessionManager:
    """Manages the conversation session, including history and export"""
    
    def __init__(self, config):
        """Initialize the session manager"""
        self.logger = logging.getLogger("gaming_translator.session_manager")
        self.config = config
        
        # Conversation history
        self.messages = []
        
        # Session metadata
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        self.user_languages = {}  # Maps user ID to language
        
        # Session statistics
        self.stats = {
            "total_messages": 0,
            "outgoing_messages": 0,
            "incoming_messages": 0,
            "languages": {},
            "word_count": 0
        }
        
        # Auto-save settings
        self.auto_save = config.get_bool("session", "auto_save", True)
        self.auto_save_interval = config.get_int("session", "auto_save_interval", 300)  # 5 minutes
        
        if self.auto_save:
            self._start_auto_save()
        
        self.logger.info(f"Session manager initialized with ID: {self.session_id}")
    
    def add_message(self, message):
        """Add a message to the conversation history"""
        self.messages.append(message)
        
        # Update statistics
        self.stats["total_messages"] += 1
        if message.is_outgoing:
            self.stats["outgoing_messages"] += 1
        else:
            self.stats["incoming_messages"] += 1
        
        # Update language statistics
        if message.language not in self.stats["languages"]:
            self.stats["languages"][message.language] = 0
        self.stats["languages"][message.language] += 1
        
        # Update word count
        self.stats["word_count"] += len(message.text.split())
        
        # Log message
        self.logger.debug(f"Added message: {message.text[:30]}...")
        
        # Return the message for chaining
        return message
    
    def _start_auto_save(self):
        """Start auto-save timer thread"""
        if not self.auto_save:
            return
        
        def auto_save_worker():
            self.save_session()
            
            # Schedule next auto-save
            self.auto_save_timer = threading.Timer(
                self.auto_save_interval,
                auto_save_worker
            )
            self.auto_save_timer.daemon = True
            self.auto_save_timer.start()
        
        # Start initial timer
        self.auto_save_timer = threading.Timer(
            self.auto_save_interval,
            auto_save_worker
        )
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()
        
        self.logger.info(f"Auto-save enabled with {self.auto_save_interval}s interval")
    
    def stop_auto_save(self):
        """Stop auto-save timer"""
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.cancel()
            self.logger.info("Auto-save stopped")
    
    def save_session(self, path=None):
        """Save the current session to file"""
        if not self.messages:
            self.logger.info("No messages to save")
            return False
        
        try:
            # Determine save path
            if path is None:
                sessions_dir = Path(self.config.get("session", "save_dir", 
                                                   str(Path.home() / ".gaming_translator" / "sessions")))
                sessions_dir.mkdir(exist_ok=True, parents=True)
                path = sessions_dir / f"session_{self.session_id}.json"
            
            # Prepare data
            session_data = {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "stats": self.stats,
                "user_languages": self.user_languages,
                "messages": [msg.to_dict() for msg in self.messages]
            }
            
            # Save to file
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Session saved to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            return False
    
    def load_session(self, path):
        """Load session from file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Clear current session
            self.messages = []
            
            # Load metadata
            self.session_id = session_data.get("session_id", self.session_id)
            
            try:
                self.start_time = datetime.fromisoformat(session_data.get("start_time", 
                                                                        self.start_time.isoformat()))
            except ValueError:
                pass
            
            self.user_languages = session_data.get("user_languages", {})
            self.stats = session_data.get("stats", self.stats)
            
            # Load messages
            for msg_data in session_data.get("messages", []):
                self.messages.append(VoiceMessage.from_dict(msg_data))
            
            self.logger.info(f"Session loaded from {path} with {len(self.messages)} messages")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            return False
    
    def export_session(self, format_type, path=None):
        """Export the session in various formats"""
        if not self.messages:
            self.logger.info("No messages to export")
            return False
        
        # Determine export path
        if path is None:
            export_dir = Path(self.config.get("session", "export_dir", 
                                             str(Path.home() / ".gaming_translator" / "exports")))
            export_dir.mkdir(exist_ok=True, parents=True)
            
            # Use appropriate extension
            if format_type == "txt":
                ext = ".txt"
            elif format_type == "html":
                ext = ".html"
            elif format_type == "json":
                ext = ".json"
            elif format_type == "pdf":
                ext = ".pdf"
            elif format_type == "csv":
                ext = ".csv"
            else:
                ext = ".txt"  # Default to text
            
            path = export_dir / f"export_{self.session_id}{ext}"
        
        # Call appropriate export method
        try:
            if format_type == "txt":
                return self._export_text(path)
            elif format_type == "html":
                return self._export_html(path)
            elif format_type == "json":
                return self._export_json(path)
            elif format_type == "pdf":
                return self._export_pdf(path)
            elif format_type == "csv":
                return self._export_csv(path)
            else:
                self.logger.warning(f"Unknown export format: {format_type}, using text")
                return self._export_text(path)
        
        except Exception as e:
            self.logger.error(f"Error exporting session as {format_type}: {e}")
            return False
    
    def _export_text(self, path):
        """Export session as plain text"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"=== Gaming Voice Chat Translator - Conversation Log ===\n")
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total messages: {self.stats['total_messages']}\n")
                f.write("\n")
                
                for msg in self.messages:
                    timestamp = msg.timestamp.strftime("%H:%M:%S")
                    speaker = "You" if msg.is_outgoing else "Teammate"
                    lang_code = msg.language
                    
                    f.write(f"[{timestamp}] {speaker} ({lang_code}): {msg.text}\n")
                    if msg.translation:
                        f.write(f"   → {msg.translation}\n")
            
            self.logger.info(f"Session exported as text to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting as text: {e}")
            return False
    
    def _export_html(self, path):
        """Export session as HTML document"""
        try:
            from gaming_translator.utils.constants import GAMING_LANGUAGES, UI_COLORS
            
            with open(path, 'w', encoding='utf-8') as f:
                # HTML header
                f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaming Voice Chat Translator - Conversation Log</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0a0e27;
            color: #e1e5f2;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #1a1f3a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        header {
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #4c9eff;
        }
        h1 {
            color: #4c9eff;
            margin-bottom: 5px;
        }
        .meta {
            color: #888;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .stats {
            background-color: #21295c;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }
        .outgoing {
            background-color: #17384e;
            border-left: 3px solid #00d26a;
        }
        .incoming {
            background-color: #321d47;
            border-left: 3px solid #ff9500;
        }
        .timestamp {
            color: #888;
            font-size: 12px;
        }
        .speaker {
            font-weight: bold;
            color: #4c9eff;
        }
        .language {
            font-size: 12px;
            color: #888;
        }
        .translation {
            margin-top: 5px;
            padding-left: 15px;
            font-style: italic;
            color: #4c9eff;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 Gaming Voice Chat Translator</h1>
            <div class="meta">Conversation Log</div>
        </header>
""")
                
                # Session info
                f.write(f"""
        <div class="stats">
            <p><strong>Session ID:</strong> {self.session_id}</p>
            <p><strong>Start time:</strong> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>End time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total messages:</strong> {self.stats['total_messages']} 
               (Outgoing: {self.stats['outgoing_messages']}, 
               Incoming: {self.stats['incoming_messages']})</p>
            <p><strong>Languages used:</strong> {', '.join(self.stats['languages'].keys())}</p>
        </div>
        
        <div class="messages">
""")
                
                # Messages
                for msg in self.messages:
                    timestamp = msg.timestamp.strftime("%H:%M:%S")
                    speaker = "You" if msg.is_outgoing else "Teammate"
                    msg_class = "outgoing" if msg.is_outgoing else "incoming"
                    lang_code = msg.language
                    lang_name = GAMING_LANGUAGES.get(lang_code, {}).get('name', lang_code)
                    lang_flag = GAMING_LANGUAGES.get(lang_code, {}).get('flag', '🌐')
                    
                    f.write(f"""
            <div class="message {msg_class}">
                <div class="timestamp">{timestamp}</div>
                <div class="speaker">{speaker}:</div>
                <div class="content">{msg.text}</div>
                <div class="language">{lang_flag} {lang_name}</div>
""")
                    
                    if msg.translation:
                        f.write(f"""
                <div class="translation">→ {msg.translation}</div>
""")
                    
                    f.write("            </div>\n")
                
                # HTML footer
                f.write("""
        </div>
    </div>
</body>
</html>
""")
            
            self.logger.info(f"Session exported as HTML to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting as HTML: {e}")
            return False
    
    def _export_json(self, path):
        """Export session as JSON file"""
        try:
            session_data = {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "stats": self.stats,
                "user_languages": self.user_languages,
                "messages": [msg.to_dict() for msg in self.messages]
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Session exported as JSON to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting as JSON: {e}")
            return False
    
    def _export_pdf(self, path):
        """Export session as PDF document"""
        try:
            # Check if reportlab is available
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            except ImportError:
                self.logger.error("reportlab not installed, cannot export as PDF")
                return False
            
            from gaming_translator.utils.constants import GAMING_LANGUAGES
            
            # Create PDF document
            doc = SimpleDocTemplate(path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            styles.add(ParagraphStyle(
                name='Title',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=1,  # Center
                spaceAfter=12
            ))
            
            styles.add(ParagraphStyle(
                name='MessageOutgoing',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                borderPadding=5,
                borderWidth=1,
                borderColor=colors.green,
                backColor=colors.lightgreen,
                borderRadius=5
            ))
            
            styles.add(ParagraphStyle(
                name='MessageIncoming',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                borderPadding=5,
                borderWidth=1,
                borderColor=colors.blue,
                backColor=colors.lightblue,
                borderRadius=5
            ))
            
            styles.add(ParagraphStyle(
                name='Translation',
                parent=styles['Italic'],
                fontSize=9,
                leftIndent=40,
                textColor=colors.blue
            ))
            
            # Create content elements
            elements = []
            
            # Title
            elements.append(Paragraph("Gaming Voice Chat Translator", styles['Title']))
            elements.append(Paragraph("Conversation Log", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Session info
            elements.append(Paragraph(f"<b>Session ID:</b> {self.session_id}", styles['Normal']))
            elements.append(Paragraph(f"<b>Start time:</b> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Paragraph(f"<b>End time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Paragraph(f"<b>Total messages:</b> {self.stats['total_messages']}", styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Messages
            for msg in self.messages:
                timestamp = msg.timestamp.strftime("%H:%M:%S")
                speaker = "You" if msg.is_outgoing else "Teammate"
                style = styles['MessageOutgoing'] if msg.is_outgoing else styles['MessageIncoming']
                lang_code = msg.language
                lang_name = GAMING_LANGUAGES.get(lang_code, {}).get('name', lang_code)
                
                # Message paragraph
                message_text = f"[{timestamp}] <b>{speaker}</b> ({lang_name}): {msg.text}"
                elements.append(Paragraph(message_text, style))
                
                # Translation if available
                if msg.translation:
                    elements.append(Paragraph(f"→ {msg.translation}", styles['Translation']))
                
                elements.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(elements)
            
            self.logger.info(f"Session exported as PDF to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting as PDF: {e}")
            return False
    
    def _export_csv(self, path):
        """Export session as CSV file"""
        try:
            import csv
            
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(["Timestamp", "Speaker", "Language", "Text", "Translation"])
                
                # Write messages
                for msg in self.messages:
                    timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    speaker = "You" if msg.is_outgoing else "Teammate"
                    
                    writer.writerow([
                        timestamp,
                        speaker,
                        msg.language,
                        msg.text,
                        msg.translation or ""
                    ])
            
            self.logger.info(f"Session exported as CSV to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting as CSV: {e}")
            return False
    
    def get_stats(self):
        """Get session statistics"""
        # Update end time and duration
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).total_seconds()
        
        # Calculate messages per minute
        messages_per_minute = 0
        if duration_seconds > 0:
            messages_per_minute = (self.stats["total_messages"] / duration_seconds) * 60
        
        # Return comprehensive stats
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": end_time,
            "duration_seconds": duration_seconds,
            "duration_formatted": self._format_duration(duration_seconds),
            "total_messages": self.stats["total_messages"],
            "outgoing_messages": self.stats["outgoing_messages"],
            "incoming_messages": self.stats["incoming_messages"],
            "messages_per_minute": round(messages_per_minute, 2),
            "languages": self.stats["languages"],
            "word_count": self.stats["word_count"]
        }
    
    def _format_duration(self, seconds):
        """Format duration in seconds to human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def clear(self):
        """Clear the session"""
        self.messages = []
        self.stats = {
            "total_messages": 0,
            "outgoing_messages": 0,
            "incoming_messages": 0,
            "languages": {},
            "word_count": 0
        }
        
        # Reset session ID and start time
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        
        self.logger.info(f"Session cleared, new session ID: {self.session_id}")