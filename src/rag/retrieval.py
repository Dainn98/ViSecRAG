from config import *
from tokenization import *
import numpy as np
# from sklearn.preprocessing import MinMaxScaler

def hybrid_score_fusion(bi_scores, cross_scores, alpha):
    def normalize_bi_encoder(scores):
        return ((np.array(scores) + 1) / 2)
    def normalize_cross_encoder(scores):
        return 1 / (1 + np.exp(-np.array(scores)))

    bi_norm = normalize_bi_encoder(bi_scores)
    cross_norm = normalize_cross_encoder(cross_scores)
    return alpha * bi_norm + (1 - alpha) * cross_norm


class Retrieval: 
    def __init__(self, config, client):
        self.cfg = config
        self.cluster = client.get_cluster(config.cluster_name)
        self.client = client
        # self.collection_name = self.cfg.REGEXs
        self.top_k = self.cfg.TOP_K
        self.hybrid_factor = self.cfg.HYBRID_FACTOR
        self.alpha = self.cfg.ALPHA
        
    def keyword_retrieval(self, query, top_k):
      response = self.cluster.query.bm25(
        query=tokenize(query),
        limit=top_k,
        return_metadata=["score"]
      )
      if response.objects is None:
        print(f"⚠️ Error retrieval() return None")
        return []
      return response.objects

    def hybrid_retrieval(self, query, top_k, alpha=0.5):
        query_segmented = tokenize(query)
        query_embed = self.cfg.gen_embedding(query_segmented)
        # cluster = client.get_cluster(collection_name)
        # client.get_cluster(config.REGEXs)
        
        response = self.cluster.query.hybrid(
            query=query_segmented,
            vector=query_embed,
            alpha=alpha,
            limit=top_k * 2,
            return_metadata=["score"],
        )
         # Loại bỏ kết quả trùng text
        seen = set()
        results = []
        for obj in response.objects:
            text = obj.properties.get("content", "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            results.append(obj)
            if len(results) == top_k:
                break
        
        return results
    
    def rerankce_retrieval(self, query,top_k, alpha=0.4, hybrid_factor=2):
        # query_segmented = 
        import heapq
        retrieved_docs = self.hybrid_retrieval(query, top_k * hybrid_factor)
        if not retrieved_docs:
            return [], [], [], []
        # pprint((retrieved_docs))

        bi_encoder_scores = np.array([doc.metadata.score for doc in retrieved_docs])
        
        query_segmented = tokenize(query)
        passage_pairs = [(query_segmented, doc.properties['content']) for doc in retrieved_docs]
        cross_encoder_scores = np.array(self.config.reranking_model.predict(passage_pairs))
        
        fused_scores = hybrid_score_fusion(bi_encoder_scores, cross_encoder_scores, alpha)
        
        top_indices = heapq.nlargest(top_k, range(len(fused_scores)), key=fused_scores.__getitem__)
        
        # Chuẩn bị kết quả
        indices = [idx+1 for idx in top_indices]
        docs = [retrieved_docs[idx] for idx in top_indices]
        cross_scores = [float(cross_encoder_scores[idx]) for idx in top_indices]
        fused_scores = [float(fused_scores[idx]) for idx in top_indices]

        # return indices, cross_scores, fused_scores, docs
        return docs
    