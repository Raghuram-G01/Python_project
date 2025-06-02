#!/usr/bin/env python3
"""
Test MongoDB connection script
"""
import pymongo
from pymongo import MongoClient

def test_mongodb_connection():
    """Test if MongoDB is running and accessible"""
    try:
        # Try to connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        print("✅ MongoDB is running and accessible!")
        
        # List databases
        databases = client.list_database_names()
        print(f"📁 Available databases: {databases}")
        
        # Test our blog database
        db = client['blogwebsite']
        print(f"🗄️  Connected to 'blogwebsite' database")
        
        # List collections (if any)
        collections = db.list_collection_names()
        if collections:
            print(f"📋 Collections in blogwebsite: {collections}")
        else:
            print("📋 No collections found in blogwebsite database (this is normal for a new database)")
        
        client.close()
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ MongoDB is not running or not accessible on localhost:27017")
        print("💡 Please make sure MongoDB is installed and running:")
        print("   - Windows: Start MongoDB service or run 'mongod' command")
        print("   - macOS: brew services start mongodb-community")
        print("   - Linux: sudo systemctl start mongod")
        return False
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing MongoDB connection...")
    test_mongodb_connection()
