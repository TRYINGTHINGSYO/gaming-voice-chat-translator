# Gaming Voice Chat Translator

A real-time voice translation tool for gaming communication, allowing gamers to communicate across language barriers.

![Gaming Voice Chat Translator Screenshot](gaming_translator/assets/screenshot.png)

## Features

- **Real-time voice recognition** with support for multiple engines (Google Speech Recognition, WhisperX)
- **Automatic language detection** so you don't need to know what language your teammates are speaking
- **Fast translation** between 25+ languages common in gaming communities
- **In-game overlay** that stays on top of your game with minimal screen space
- **WhisperX integration** for improved accuracy with gaming-specific terminology
- **GPU acceleration** for WhisperX when available
- **AutoHotkey integration** to send translated messages directly to in-game chat
- **Multiple export formats** (JSON, HTML, PDF, CSV, TXT) for saving conversations
- **Customizable hotkeys** to control the application even while gaming

## Installation

### Quick Install (Windows, macOS, Linux)

```bash
# Install from pip
pip install gaming-translator

# Run the application
gaming-translator
```

### Install with WhisperX Support (Recommended)

```bash
# Install with WhisperX support
pip install gaming-translator[whisperx]

# Run the application
gaming-translator
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/example/gaming-translator.git
cd gaming-translator

# Install the package
pip install -e .

# For developers
pip install -e ".[dev]"

# For WhisperX support
pip install -e ".[whisperx]"

# Run the application
python -m gaming_translator
```

### Standalone Executable (Windows)

Download the latest standalone executable from the [Releases](https://github.com/example/gaming-translator/releases) page.

## Usage

### Basic Setup

1. Start the application
2. Select your microphone from the dropdown
3. Choose your language and your teammate's language
4. Click "Start Listening" to begin voice recognition
5. Use the overlay during games with Ctrl+O

### In-Game Integration

For sending translated messages directly to in-game chat:

1. Install [AutoHotkey](https://www.autohotkey.com/)
2. Configure game-specific chat keys in the settings
3. Use the "Send to Chat" button or hotkey (default: Ctrl+Enter)

### Keyboard Shortcuts

- **Ctrl+L**: Toggle listening
- **Ctrl+O**: Toggle game overlay
- **Ctrl+T**: Translate and speak text
- **Ctrl+S**: Save conversation
- **Escape**: Hide overlay
- **Ctrl+Enter**: Send translation to in-game chat (requires AutoHotkey)

## Advanced Features

### WhisperX Integration

WhisperX provides significantly better accuracy for gaming terminology and can run on your GPU for faster processing:

1. Install the WhisperX dependencies: `pip install gaming-translator[whisperx]`
2. Enable WhisperX in Settings → Recognition → Backend

### GPU Acceleration

If you have a compatible NVIDIA GPU:

1. Install CUDA and cuDNN (see [PyTorch installation](https://pytorch.org/get-started/locally/))
2. Enable GPU acceleration in Settings → Recognition → Use GPU

### Export Options

Your conversations can be exported in multiple formats:

- **HTML**: Styled chat log with formatting
- **PDF**: Portable document format
- **JSON**: Data format for further processing
- **CSV**: Spreadsheet compatible format
- **TXT**: Plain text format

## Game-Specific Setup

The application includes optimized presets for popular games:

- Valorant
- League of Legends
- Counter-Strike
- Fortnite
- Minecraft
- Dota 2
- Apex Legends
- Overwatch

Select your game in Settings → AutoHotkey → Game Presets to automatically configure the correct chat keys.

## Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux
- Microphone
- For WhisperX: CUDA-compatible GPU (optional but recommended)
- For AutoHotkey integration: Windows with AutoHotkey installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The [WhisperX](https://github.com/m-bain/whisperx) project for improved speech recognition
- The [googletrans](https://github.com/ssut/py-googletrans) library for translation
- All the gamers who provided feedback during development