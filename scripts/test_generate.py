import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from backend.app.services.rag_service import RAGService
import os

s = RAGService(api_key=os.getenv('MISTRAL_API_KEY',''), data_folder=str(repo_root / 'python_RAG' / 'data'))
print('index:', s.index is not None, 'chunks:', len(s.all_chunks))
qs = s.generate_questions_from_chapter('Mensuration - Perimeter and Area', subject=None, num_questions=3)
print('returned', len(qs), 'questions')
for q in qs:
    print('-', q.get('question')[:200])
