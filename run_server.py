#!/usr/bin/env python3
"""
AI Campus Admin Agent - Server Startup Script
"""

import uvicorn
import logging
import sys
from backend.config import Config
from backend.db import db_manager

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_requirements():
    """Check if all requirements are met"""
    logger.info("🔍 Checking requirements...")
    
    # Check database connection
    if not db_manager.is_connected():
        logger.error("❌ Database connection failed!")
        logger.error("Please check your DB_URI in .env file")
        return False
    
    # Check API keys
    if not Config.OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY not found!")
        logger.error("Please set OPENAI_API_KEY in your .env file")
        return False
    
    logger.info("✅ All requirements met!")
    return True

def main():
    """Main startup function"""
    logger.info("🚀 Starting AI Campus Admin Agent...")
    
    # Check requirements
    if not check_requirements():
        logger.error("❌ Requirements check failed. Exiting...")
        sys.exit(1)
    
    # Start server
    logger.info(f"🌐 Starting server on {Config.HOST}:{Config.PORT}")
    logger.info(f"📚 API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    logger.info(f"🔧 Health Check: http://{Config.HOST}:{Config.PORT}/health")
    
    try:
        uvicorn.run(
            "backend.main:app",
            host=Config.HOST,
            port=Config.PORT,
            reload=Config.DEBUG,
            log_level=Config.LOG_LEVEL.lower()
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        db_manager.disconnect()
        logger.info("🧹 Cleanup completed")

if __name__ == "__main__":
    main()
