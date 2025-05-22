#!/usr/bin/env python3
"""
Simple build script to create Gaming Voice Chat Translator .exe
Just run: python build.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """Build the executable"""
    print("🚀 Building Gaming Voice Chat Translator executable...")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")
    
    # Install PyInstaller if needed
    print("📦 Installing PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to install PyInstaller")
        return False
    
    # Build the executable
    print("🏗️  Building executable...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "gaming_translator.spec"], check=True)
        print("✅ Build completed!")
        
        # Show location
        exe_path = Path("dist/GamingTranslator/GamingTranslator.exe")
        if exe_path.exists():
            print(f"📍 Your executable is ready: {exe_path.absolute()}")
            print(f"📂 Full folder: {exe_path.parent.absolute()}")
            return True
        else:
            print("❌ Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    success = build_exe()
    if success:
        input("\n🎉 Build successful! Press Enter to exit...")
    else:
        input("\n💥 Build failed! Press Enter to exit...")
    sys.exit(0 if success else 1)