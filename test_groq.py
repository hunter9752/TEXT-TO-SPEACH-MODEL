#!/usr/bin/env python3
"""
Quick test to verify GROQ API key is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_connection():
    """Test GROQ API connection"""
    
    try:
        from groq import Groq
    except ImportError:
        print("❌ GROQ library not installed. Run: pip install groq")
        return False
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ No GROQ API key found in .env file")
        print("Add this line to your .env file:")
        print("GROQ_API_KEY=gsk_your_groq_api_key_here")
        return False
    
    if api_key == 'gsk_your_groq_api_key_here':
        print("❌ Please replace the placeholder API key with your actual GROQ key")
        return False
    
    print(f"✅ GROQ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Create GROQ client
        client = Groq(api_key=api_key)
        
        # Test with a simple request
        print("🧪 Testing GROQ API connection...")
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Say 'Hello from GROQ! API test successful!'"}],
            max_tokens=50,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print(f"✅ GROQ Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ GROQ API error: {e}")
        return False

if __name__ == '__main__':
    print("GROQ API Connection Test")
    print("=" * 30)
    
    success = test_groq_connection()
    
    if success:
        print("\n🎉 GROQ API is working correctly!")
        print("\nTo use GROQ in your system, add these lines to your .env file:")
        print("AI_PROVIDER=groq")
        print("AI_MODEL=llama3-8b-8192")
        print("GROQ_API_KEY=your_actual_groq_key")
    else:
        print("\n🔧 Please fix the GROQ API key issue and try again.")
        print("\nSteps to fix:")
        print("1. Go to https://console.groq.com/")
        print("2. Sign up for a free account")
        print("3. Go to API Keys section")
        print("4. Create a new API key")
        print("5. Copy the key to your .env file")
