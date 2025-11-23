#!/usr/bin/env python3
"""
Quick validation script for Gemini API configuration.
"""
import os
import sys

def main():
    print("🔍 Validating Gemini API Configuration...\n")
    
    # Check .env file exists
    env_path = ".env"
    if not os.path.exists(env_path):
        print(f"❌ {env_path} file not found!")
        print(f"   Run: cp .env.example .env")
        return False
    
    print(f"✅ {env_path} file exists")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check GEMINI_API_KEY
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY not set in .env file")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    if gemini_key == "your-gemini-api-key-here":
        print("⚠️  GEMINI_API_KEY still set to placeholder value")
        print("   Replace with your actual API key from: https://makersuite.google.com/app/apikey")
        return False
    
    # Mask key for display
    masked_key = gemini_key[:8] + "..." if len(gemini_key) > 8 else "***"
    print(f"✅ GEMINI_API_KEY configured (key: {masked_key})")
    
    # Check GOOGLE_API_KEY is set (by config.py)
    google_key = os.getenv("GOOGLE_API_KEY", "")
    
    # Import settings to trigger model_post_init
    from app.config import settings
    
    google_key_after = os.getenv("GOOGLE_API_KEY", "")
    
    if google_key_after:
        masked_google = google_key_after[:8] + "..." if len(google_key_after) > 8 else "***"
        print(f"✅ GOOGLE_API_KEY auto-configured for LangChain (key: {masked_google})")
    else:
        print("⚠️  GOOGLE_API_KEY not set (may be set during runtime)")
    
    print(f"✅ Default model: {settings.GEMINI_MODEL_DEFAULT}")
    
    print("\n🎉 Configuration looks good!")
    print("\nNext steps:")
    print("  1. Start the backend: uvicorn app.main:app --reload")
    print("  2. Check logs for: '✅ Gemini API key configured'")
    print("  3. Upload a test PDF to verify RAG pipeline")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
