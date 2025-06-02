#!/usr/bin/env python3
"""
Clean MongoDB database script
"""
import pymongo
from pymongo import MongoClient

def clean_mongodb():
    """Clean the blogwebsite database"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Get the database
        db = client['blogwebsite']
        
        print("🗄️  Connected to 'blogwebsite' database")
        
        # List current collections
        collections = db.list_collection_names()
        print(f"📋 Current collections: {collections}")
        
        if collections:
            print("🧹 Cleaning database...")
            
            # Drop all collections
            for collection_name in collections:
                db.drop_collection(collection_name)
                print(f"   ✅ Dropped collection: {collection_name}")
            
            print("✨ Database cleaned successfully!")
        else:
            print("📋 Database is already clean (no collections found)")
        
        # Verify cleanup
        remaining_collections = db.list_collection_names()
        if remaining_collections:
            print(f"⚠️  Some collections remain: {remaining_collections}")
        else:
            print("✅ All collections removed successfully")
        
        client.close()
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ MongoDB is not running or not accessible on localhost:27017")
        return False
        
    except Exception as e:
        print(f"❌ Error cleaning MongoDB: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Cleaning MongoDB database...")
    if clean_mongodb():
        print("\n✅ Database cleanup completed!")
        print("💡 You can now run 'python manage.py migrate' to set up fresh tables")
    else:
        print("\n❌ Database cleanup failed!")
