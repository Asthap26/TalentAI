import os
import chromadb
from chromadb.utils import embedding_functions

# Use the exact embedding model specified in the technical requirements
# sentence-transformers/all-MiniLM-L6-v2 is lightweight and fast for this purpose
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

class VectorStore:
    def __init__(self, data_path: str = "./data/chroma_db"):
        self.data_path = data_path
        self._client = None
        self._skills_collection = None

    def _init_client(self):
        if self._client is None:
            os.makedirs(self.data_path, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.data_path)
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBED_MODEL_NAME
            )
            self._skills_collection = self._client.get_or_create_collection(
                name="skill_taxonomy",
                embedding_function=self.embedding_fn
            )

    @property
    def skills_collection(self):
        self._init_client()
        return self._skills_collection

    def add_skills(self, skills: list[dict]):
        """
        Expects a list of dictionaries like:
        [ {"id": "uuid-str", "name": "Python", "category": "Programming Languages"} ]
        """
        if not skills:
            return
            
        documents = [s["name"] for s in skills]
        ids = [str(s["id"]) for s in skills]
        metadatas = [{"category": s.get("category", "")} for s in skills]
        
        self.skills_collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Upserted {len(skills)} skills into ChromaDB.")

    def search_canonical_skill(self, raw_skill: str, top_k: int = 1) -> list[dict]:
        """
        Takes an un-normalized raw skill from a resume (e.g., 'PyTorch framework')
        and finds the closest match in the taxonomy.
        """
        results = self.skills_collection.query(
            query_texts=[raw_skill],
            n_results=top_k
        )
        
        matches = []
        if results['ids'] and results['ids'][0]:
            for doc_id, name, dist in zip(results['ids'][0], results['documents'][0], results['distances'][0]):
                matches.append({
                    "id": doc_id,
                    "name": name,
                    "distance": dist  # Lower distance means closer match via L2/Cosine
                })
        return matches

vector_db = VectorStore()
