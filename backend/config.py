import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    
    # Database
    DB_URI: str = os.getenv("DB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "campus_admin_agent")
    
    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        # Check if we have either OpenAI or Gemini API key
        has_openai = bool(cls.OPENAI_API_KEY)
        has_gemini = bool(cls.GEMINI_API_KEY)
        
        if not has_openai and not has_gemini:
            print("❌ Missing API key!")
            print("Please set either OPENAI_API_KEY or GEMINI_API_KEY in your .env file:")
            print("  OPENAI_API_KEY=your_openai_key_here")
            print("  GEMINI_API_KEY=your_gemini_key_here")
            return False
        
        if not cls.DB_URI:
            print("❌ Missing DB_URI!")
            print("Please set DB_URI in your .env file:")
            print("  DB_URI=mongodb://localhost:27017")
            return False
        
        print("✅ Configuration validated successfully")
        if has_gemini:
            print("🤖 Using Gemini API")
        if has_openai:
            print("🤖 Using OpenAI API")
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL"""
        return cls.DB_URI
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": "gpt-4o-mini"  # Using correct model name
        }
    
    @classmethod
    def get_gemini_config(cls) -> dict:
        """Get Gemini configuration"""
        return {
            "api_key": cls.GEMINI_API_KEY,
            "model": "gemini-1.5-flash"  # Using correct model name
        }

# Validate configuration on import
if not Config.validate():
    raise ValueError("Invalid configuration. Please check your environment variables.")
