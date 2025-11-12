# !pip install -qU weaviate-client
import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import Auth
from chunking import *
from config import *


class Client: 
    def __init__(self, config, cluster_name = 'regex'):
        self.cfg = config
        
        self.client = weaviate.connect_to_weaviate_cloud(
          cluster_url=self.cfg.wvc_url,
          auth_credentials=Auth.api_key(self.cfg.wvc_api),
          headers={}
          #headers={'X-OpenAI-Api-key': OPENAI_API_KEY}
        )
        self.cluster_name = cluster_name
        
    def get_cluster(self, cluster_name):
        return self.client.collections.get(cluster_name)

    def connect(self):
        self.client.connect()
        
    def close(self):
        self.client.close()
    
    def is_ready(self):
        return self.client.is_ready()
    
    def reset_schema(self):
        """
        Xóa toàn bộ schema (collections) hiện tại trong Weaviate client.
        """
        self.client.connect()
        self.client.collections.delete_all()
        self.client.close()
        
    
    def create_schema(self, cluster_name):
        """
        Tạo mới các schema (collections) trong Weaviate với cấu hình cụ thể.
        
        Args:
            client: Weaviate client đã kết nối.
            collections: Danh sách tên các collections cần tạo.
        
        Mỗi collection được cấu hình với:
        - Vectorizer: OpenAI text embedding
        - Generator: Cohere LLM
        - Các thuộc tính: document_id, stock_id, metadata, text
        """
        self.client.connect()
        try:
            self.client.collections.create(
                name = cluster_name,
                vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
                generative_config=wvc.config.Configure.Generative.cohere(),
                properties=[
                    wvc.config.Property(name="source",data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="chunk_id",data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="metadata",data_type=wvc.config.DataType.TEXT_ARRAY),
                    wvc.config.Property(name="content",data_type=wvc.config.DataType.TEXT)]
            )
            print(f"Đã tạo {cluster_name} thành công")
        except Exception as e:
            print(f"❌ Lỗi khi tạo schema: {e}")
        self.client.close()
        
    def upload_data(self, config, corpus, cluster_name):
        objs=[]
        for obj in corpus:
            objs.append(
               wvc.data.DataObject(
                properties={
                    "source": obj.source,
                    "chunk_id": obj.chunk_id,
                    "metadata": obj.metadata,
                    "content": obj.content
                },
                vector=config.gen_embedding(obj.content)
                )
            )
        print(f"Total chunks: {len(objs)}")
        BATCH_SIZE = 256
        cluster = self.get_cluster(cluster_name)
        for i in range(0, len(objs), BATCH_SIZE):
            batch = objs[i:i + BATCH_SIZE]
            cluster.data.insert_many(batch)
            print(f"✅ Batch {i + 1} to {i + len(batch)} inserted successfully!")

        print(f"Data insertion into {cluster_name} completed!\n")
        
        return objs
            
# print(weaviate.__version__)        