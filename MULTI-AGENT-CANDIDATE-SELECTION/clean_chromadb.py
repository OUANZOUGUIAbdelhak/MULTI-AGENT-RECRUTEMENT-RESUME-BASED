"""
Script to clean ChromaDB vector store
Removes all collections and resets the database
"""

import chromadb
from pathlib import Path

def clean_chromadb(vectorstore_dir: str = "./DATA/vectorstore"):
    """
    Clean ChromaDB by deleting all collections.
    
    Args:
        vectorstore_dir: Path to ChromaDB storage directory
    """
    vectorstore_path = Path(vectorstore_dir)
    
    if not vectorstore_path.exists():
        print(f"❌ Vector store directory not found: {vectorstore_path}")
        return
    
    print(f"🧹 Cleaning ChromaDB at: {vectorstore_path}")
    
    try:
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=str(vectorstore_path))
        
        # List all collections
        collections = client.list_collections()
        print(f"📋 Found {len(collections)} collection(s):")
        
        for collection in collections:
            collection_name = collection.name
            count = collection.count()
            print(f"   - {collection_name}: {count} documents")
            
            # Delete collection
            try:
                client.delete_collection(name=collection_name)
                print(f"   ✅ Deleted collection '{collection_name}'")
            except Exception as e:
                print(f"   ❌ Error deleting collection '{collection_name}': {e}")
        
        print(f"\n✅ ChromaDB cleaned successfully!")
        print(f"💡 You can now rebuild the index to start fresh.")
        
    except Exception as e:
        print(f"❌ Error cleaning ChromaDB: {e}")

if __name__ == "__main__":
    import sys
    
    # Allow custom path
    if len(sys.argv) > 1:
        vectorstore_dir = sys.argv[1]
    else:
        vectorstore_dir = "./DATA/vectorstore"
    
    print("="*60)
    print("ChromaDB Cleaner")
    print("="*60)
    print()
    
    response = input("⚠️  This will delete ALL collections in ChromaDB. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y', 'oui', 'o']:
        clean_chromadb(vectorstore_dir)
    else:
        print("❌ Operation cancelled.")

