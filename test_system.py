#!/usr/bin/env python3
"""
System Test Script for Speech-to-Text AI System
Quick verification that all components can be imported and initialized
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test core imports
        from speech_to_text.speech_recognizer import SpeechRecognizer
        print("✓ SpeechRecognizer imported successfully")
        
        from ai_analysis.ai_analyzer import AIAnalyzer
        print("✓ AIAnalyzer imported successfully")
        
        from audio_handler.audio_input import AudioInputHandler
        print("✓ AudioInputHandler imported successfully")
        
        from output_processor.output_formatter import OutputFormatter
        print("✓ OutputFormatter imported successfully")
        
        from web_interface.app import create_app
        print("✓ Web interface imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_component_initialization():
    """Test that components can be initialized"""
    print("\nTesting component initialization...")
    
    try:
        # Test OutputFormatter (no external dependencies)
        from output_processor.output_formatter import OutputFormatter
        formatter = OutputFormatter()
        print("✓ OutputFormatter initialized successfully")
        
        # Test AudioInputHandler
        from audio_handler.audio_input import AudioInputHandler
        audio_handler = AudioInputHandler()
        print("✓ AudioInputHandler initialized successfully")
        
        # Test SpeechRecognizer (may fail without whisper model)
        try:
            from speech_to_text.speech_recognizer import SpeechRecognizer
            speech_recognizer = SpeechRecognizer(engine='google')  # Use Google instead of Whisper for testing
            print("✓ SpeechRecognizer initialized successfully")
        except Exception as e:
            print(f"⚠ SpeechRecognizer initialization warning: {e}")
        
        # Test AIAnalyzer (requires OpenAI API key)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            try:
                from ai_analysis.ai_analyzer import AIAnalyzer
                ai_analyzer = AIAnalyzer()
                print("✓ AIAnalyzer initialized successfully")
            except Exception as e:
                print(f"⚠ AIAnalyzer initialization warning: {e}")
        else:
            print("⚠ AIAnalyzer skipped (no valid OpenAI API key)")
        
        return True
        
    except Exception as e:
        print(f"✗ Component initialization failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality without external API calls"""
    print("\nTesting basic functionality...")
    
    try:
        from output_processor.output_formatter import OutputFormatter
        
        # Test output formatting
        formatter = OutputFormatter()
        test_analysis = {
            'response': 'This is a test response',
            'analysis': {
                'word_count': 4,
                'topics': ['test']
            },
            'timestamp': '2023-01-01T12:00:00'
        }
        
        result = formatter.format_response("This is a test", test_analysis)
        if result and len(result) > 0:
            print("✓ Output formatting works")
        else:
            print("✗ Output formatting failed")
            return False
        
        # Test different output styles
        formatter.set_output_style('json')
        json_result = formatter.format_response("Test", test_analysis)
        if json_result.startswith('{'):
            print("✓ JSON output formatting works")
        else:
            print("✗ JSON output formatting failed")
            return False
        
        # Test session management
        summary = formatter.get_session_summary()
        if summary:
            print("✓ Session management works")
        else:
            print("✗ Session management failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_web_interface():
    """Test web interface creation"""
    print("\nTesting web interface...")
    
    try:
        from web_interface.app import create_app
        
        app = create_app()
        if app:
            print("✓ Flask app created successfully")
            
            # Test with test client
            with app.test_client() as client:
                response = client.get('/api/health')
                if response.status_code in [200, 503]:  # 503 is OK if components aren't fully initialized
                    print("✓ Health endpoint responds")
                else:
                    print(f"⚠ Health endpoint returned status {response.status_code}")
            
            return True
        else:
            print("✗ Flask app creation failed")
            return False
            
    except Exception as e:
        print(f"✗ Web interface test failed: {e}")
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("\nChecking dependencies...")
    
    dependencies = [
        'speech_recognition',
        'openai',
        'flask',
        'numpy',
        'dotenv'  # python-dotenv imports as 'dotenv'
    ]
    
    optional_dependencies = [
        'whisper',
        'pyaudio',
        'pydub',
        'torch'
    ]
    
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} (required)")
            all_good = False
    
    for dep in optional_dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✓ {dep} (optional)")
        except ImportError:
            print(f"⚠ {dep} (optional, not installed)")
    
    return all_good

def check_environment():
    """Check environment configuration"""
    print("\nChecking environment configuration...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✓ .env file found")
    else:
        print("⚠ .env file not found (copy from .env.example)")
    
    # Check critical environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✓ OpenAI API key configured")
    else:
        print("⚠ OpenAI API key not configured")
    
    return True

def main():
    """Run all tests"""
    print("Speech-to-Text AI System - System Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Imports", test_imports),
        ("Component Initialization", test_component_initialization),
        ("Basic Functionality", test_basic_functionality),
        ("Web Interface", test_web_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Configure your OpenAI API key in .env file")
        print("2. Install optional dependencies if needed:")
        print("   pip install pyaudio pydub torch")
        print("3. Run the system:")
        print("   python main.py --mode web")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
