#!/usr/bin/env python3
"""
Quick test to verify OpenAI API key is working
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OpenAI API key found in .env file")
        return False
    
    if api_key == 'your_openai_api_key_here':
        print("❌ Please replace the placeholder API key with your actual key")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Create OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple request
        print("🧪 Testing API connection...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello, API test successful!'"}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        return True
        
    except openai.AuthenticationError:
        print("❌ Authentication failed - Invalid API key")
        print("Please check your API key at https://platform.openai.com/api-keys")
        return False
        
    except openai.RateLimitError:
        print("❌ Rate limit exceeded - Your API key may be out of credits")
        return False
        
    except openai.APIError as e:
        print(f"❌ OpenAI API error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("OpenAI API Connection Test")
    print("=" * 30)
    
    success = test_openai_connection()
    
    if success:
        print("\n🎉 OpenAI API is working correctly!")
        print("The issue might be elsewhere in the system.")
    else:
        print("\n🔧 Please fix the API key issue and try again.")
        print("\nSteps to fix:")
        print("1. Go to https://platform.openai.com/api-keys")
        print("2. Create a new API key")
        print("3. Copy the key to your .env file")
        print("4. Make sure you have credits in your OpenAI account")
