import chromadb
import uuid
from agent_tools import Tools
from .utils.logging_utils import pretty_print, pretty_error, LogType

class AgentMemory:
    def __init__(self, collection_name="rawagent_memory"):
        '''Initialize the semantic memory for the agent.'''
        self._client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self._client.get_or_create_collection(name=collection_name)
        
    def add_memory(self, content: str, metadata: dict = None) -> str:
        '''Add a new memory to the agent's semantic storage. Returns the memory ID.'''
        id = str(uuid.uuid4())
        if metadata is None:
            metadata = {}
        
        self.collection.add(
            documents=[content], 
            metadatas=[{**metadata, "id": id, "type": metadata.get("type", "general")}],
            ids=[id]
        )
        pretty_print(LogType.MEMORY_SAVE, "Memory Saved", {
            "id": id, 
            "content": content[:100] + "..." if len(content) > 100 else content,
            "metadata": metadata
        })
        return id

    def get_memory(self, intent: str = None, id: str = None, memory_type: str = None):
        '''Retrieve a memory from the agent's semantic storage by intent, ID, or type.'''
        try:
            if id is not None:
                # Direct retrieval by ID
                result = self.collection.get(ids=[id])
                if result and result['documents'] and len(result['documents']) > 0:
                    pretty_print(LogType.MEMORY_RETRIEVE, f"Memory Retrieved (by ID)", {
                        "id": id,
                        "content": result['documents'][0],
                        "metadata": result['metadatas'][0] if result['metadatas'] else {}
                    })
                    return {"content": result['documents'][0], "metadata": result['metadatas'][0] if result['metadatas'] else {}}
                pretty_error("Memory Not Found", f"No memory found with ID: {id}")
                return f"Memory not found with ID: {id}"
            
            elif memory_type is not None:
                # Step 1: Get ALL memories to debug
                all_memories = self.collection.get()
                
                # Step 2: Manual filter - look for matching type
                matching = []
                if all_memories and all_memories['metadatas']:
                    for i, meta in enumerate(all_memories['metadatas']):
                        if isinstance(meta, dict):
                            # Check exact match
                            if meta.get("type") == memory_type:
                                matching.append({
                                    "id": all_memories['ids'][i],
                                    "content": all_memories['documents'][i],
                                    "metadata": meta
                                })
                            # Debug: log what we're comparing
                            pretty_print(LogType.MEMORY_RETRIEVE, f"Checking metadata", {
                                "stored_type": meta.get("type"),
                                "searching_for": memory_type,
                                "match": meta.get("type") == memory_type
                            })
                
                if matching:
                    pretty_print(LogType.MEMORY_RETRIEVE, f"Memory Retrieved (by type: {memory_type})", {
                        "results": len(matching),
                        "memories": matching
                    })
                    return matching
                
                pretty_error("Memory Not Found", f"No memories found with type: {memory_type}. Checked {len(all_memories['metadatas']) if all_memories and all_memories['metadatas'] else 0} memories.")
                return f"No memories found with type: {memory_type}"
            
            elif intent is not None:
                # Semantic search with query_texts
                results = self.collection.query(query_texts=[intent], n_results=5)
                
                if results and results['documents'] and len(results['documents']) > 0 and results['documents'][0]:
                    pretty_print(LogType.MEMORY_RETRIEVE, f"Memory Retrieved (semantic search)", {
                        "intent": intent,
                        "matches_found": len(results['documents'][0]),
                        "top_result": results['documents'][0][0] if results['documents'][0] else None
                    })
                    return {
                        "documents": results['documents'][0],
                        "metadatas": results['metadatas'][0] if results['metadatas'] else [],
                        "distances": results['distances'][0] if results.get('distances') else []
                    }
                
                pretty_error("Memory Not Found", f"No matching memories found for intent: {intent}")
                return f"No memories found matching: {intent}"
            
            else:
                return "Either 'id', 'memory_type', or 'intent' must be provided to retrieve memory."
        except Exception as e:
            pretty_error("Memory Retrieval Error", str(e))
            return f"Error retrieving memory: {e}"

    def delete_memory(self, id: str):
        '''Delete a memory from the agent's semantic storage by its ID.'''
        try:
            self.collection.delete(ids=[id])
            pretty_print(LogType.MEMORY_SAVE, "Memory Deleted", {"id": id})
            return f"Memory {id} deleted successfully."
        except Exception as e:
            pretty_error("Memory Deletion Error", str(e))
            return f"Error deleting memory: {e}"
    
    def list_all_memories(self):
        '''List all memories currently stored. Useful for debugging.'''
        try:
            all_docs = self.collection.get()
            if not all_docs or not all_docs['documents']:
                return "No memories stored yet."
            
            memories = []
            for i, doc in enumerate(all_docs['documents']):
                memories.append({
                    "id": all_docs['ids'][i],
                    "content": doc,
                    "metadata": all_docs['metadatas'][i] if all_docs['metadatas'] and i < len(all_docs['metadatas']) else {}
                })
            
            pretty_print(LogType.MEMORY_RETRIEVE, "All Memories", {
                "total": len(memories),
                "memories": memories
            })
            return memories
        except Exception as e:
            pretty_error("Memory List Error", str(e))
            return f"Error listing memories: {e}"
        
    def register_memory_tools(self, tools: Tools):
        '''Register the memory management functions as tools for the agent.'''
        tools.add_tool(self.add_memory)
        tools.add_tool(self.get_memory)
        tools.add_tool(self.delete_memory)
        
    

