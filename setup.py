#!/usr/bin/env python3
"""
Setup script for Speech-to-Text AI System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install core dependencies
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Core dependencies installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration"""
    print("\n🔧 Setting up environment...")
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'logs',
        'uploads',
        'exports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Run the system test
        result = subprocess.run([
            sys.executable, "test_system.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation test passed")
            return True
        else:
            print("❌ Installation test failed")
            print("Output:", result.stdout)
            print("Errors:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Configure your OpenAI API key:")
    print("   - Edit the .env file")
    print("   - Replace 'your_openai_api_key_here' with your actual API key")
    print("   - Get an API key from: https://platform.openai.com/api-keys")
    
    print("\n2. Run the system:")
    print("   Web Interface:  python main.py --mode web")
    print("   CLI Mode:       python main.py --mode cli")
    print("   Process File:   python main.py --mode file --file audio.wav")
    
    print("\n3. Optional: Install additional dependencies for better performance:")
    print("   pip install torch torchaudio  # For better Whisper performance")
    print("   pip install pyaudio           # For microphone input")
    
    print("\n📚 DOCUMENTATION:")
    print("   - README.md: Complete documentation")
    print("   - Web Interface: http://localhost:5000 (when running web mode)")
    
    print("\n🔧 TROUBLESHOOTING:")
    print("   - Run 'python test_system.py' to diagnose issues")
    print("   - Check logs/ directory for error logs")
    print("   - Ensure your OpenAI API key is valid and has credits")

def main():
    """Main setup function"""
    print("Speech-to-Text AI System Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        return 1
    
    # Set up environment
    if not setup_environment():
        print("\n❌ Setup failed during environment configuration")
        return 1
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed during directory creation")
        return 1
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Setup completed but tests failed")
        print("You may need to configure your API key and install optional dependencies")
    
    # Print usage instructions
    print_usage_instructions()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
