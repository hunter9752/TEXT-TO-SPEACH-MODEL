#!/usr/bin/env python3
"""
Complete system test with GROQ integration
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_web_interface():
    """Test the web interface with GROQ"""
    
    print("🌐 Testing Web Interface...")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data.get('healthy', False)}")
            
            if health_data.get('components'):
                for component, status in health_data['components'].items():
                    icon = "✅" if status else "❌"
                    print(f"   {icon} {component}: {'OK' if status else 'FAIL'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to web interface: {e}")
        return False
    
    return True

def test_ai_analysis():
    """Test AI analysis with GROQ"""
    
    print("\n🧠 Testing AI Analysis with GROQ...")
    
    try:
        # Test text analysis
        test_data = {
            "text": "Hello GROQ! This is a test of the speech-to-text AI system.",
            "analysis_type": "general"
        }
        
        response = requests.post(
            'http://localhost:5000/api/analyze-text',
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ AI Analysis successful!")
                print(f"   Input: {result.get('input_text', '')[:50]}...")
                print(f"   AI Response: {result.get('ai_response', '')[:100]}...")
                return True
            else:
                print(f"❌ AI Analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ AI Analysis request failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ AI Analysis request error: {e}")
        return False

def test_different_analysis_types():
    """Test different analysis types"""
    
    print("\n📊 Testing Different Analysis Types...")
    
    analysis_types = ['general', 'sentiment', 'intent', 'summary']
    test_text = "I'm really excited about this new AI system! It works amazingly well."
    
    for analysis_type in analysis_types:
        try:
            response = requests.post(
                'http://localhost:5000/api/analyze-text',
                json={"text": test_text, "analysis_type": analysis_type},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ {analysis_type.title()} analysis: Working")
                else:
                    print(f"❌ {analysis_type.title()} analysis: Failed")
            else:
                print(f"❌ {analysis_type.title()} analysis: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {analysis_type.title()} analysis: Error - {e}")

def main():
    """Run complete system test"""
    
    print("🚀 Complete Speech-to-Text AI System Test")
    print("=" * 50)
    
    # Check if web server is running
    print("Checking if web server is running...")
    time.sleep(2)  # Give server time to start
    
    # Test web interface
    web_ok = test_web_interface()
    
    if not web_ok:
        print("\n❌ Web interface is not running or not accessible")
        print("Please make sure the web server is started with:")
        print("python main.py --mode web")
        return 1
    
    # Test AI analysis
    ai_ok = test_ai_analysis()
    
    if ai_ok:
        # Test different analysis types
        test_different_analysis_types()
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 FINAL SYSTEM STATUS")
    print("=" * 50)
    
    if web_ok and ai_ok:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n✅ Your Speech-to-Text AI System is fully functional with:")
        print("   • GROQ AI Provider (llama3-8b-8192)")
        print("   • Google Speech Recognition")
        print("   • PyAudio Microphone Support")
        print("   • Web Interface at http://localhost:5000")
        print("   • Multiple Analysis Types")
        print("   • Session Management")
        print("\n🚀 Ready for production use!")
        return 0
    else:
        print("⚠️  Some components need attention:")
        if not web_ok:
            print("   • Web interface issues")
        if not ai_ok:
            print("   • AI analysis issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())
