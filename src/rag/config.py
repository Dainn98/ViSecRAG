import os
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from dotenv import load_dotenv

load_dotenv()  # load environment variables from a .env file (if present)
embedding_model_path = os.getenv('PRETRAINED_EMBEDDING_MODEL_PATH')
reranking_model_path = os.getenv('PRETRAINED_RERANKING_MODEL_PATH')

class Config:
    """
    Configuration holder that loads the pretrained embedding model path from the environment.

    Expected env var:
      PRETRAINED_EMBEDDING_MODEL_PATH - path or name of a sentence-transformers model
    """
    def __init__(self):
        self.embedding_model = SentenceTransformer(embedding_model_path)
        self.reranking_model = CrossEncoder(reranking_model_path)
        self.cluster_name = 'regex'
        
    def gen_embedding(self, contents):
        return self.embedding_model.encode(contents).tolist()
    
    def get_model_from_env(path):
        model_path = os.getenv(path)
        if not model_path: 
            raise RuntimeError(f'Environment variable {path} is not set. '
                'Please set it in your environment or in a .env file.')
            