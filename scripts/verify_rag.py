import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from backend.app.services.rag_service import RAGService
import os

# instantiate and verify that RAGService loads any on-disk FAISS index
s = RAGService(api_key=os.getenv('MISTRAL_API_KEY',''), data_folder=str(repo_root / 'python_RAG' / 'data'))
print('index loaded:', s.index is not None)
print('ntotal (faiss):', getattr(s.index, 'ntotal', None))
print('metadata count:', len(s.metadata_list))
print('all_chunks count:', len(s.all_chunks))
if getattr(s, '_loaded_index_path', None):
    print('loaded index path:', s._loaded_index_path)
    print('loaded mtime:', s._loaded_index_mtime)
if s.metadata_list:
    print('first metadata preview:', {k: s.metadata_list[0].get(k) for k in ['embedding_index','chunk_id','source_file']})
