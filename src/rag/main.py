from config import *
from client import *
from chunking import *
    
path = "D:\Folder F\...\corpus" 

## Initialize Database
config = Config()
client = Client(config)
print(client.is_ready)
client.create_schema(config.cluster_name)

# Uploading database
chunks = process_data(path)
client.upload_data(config,chunks,config.cluster_name)

# Retrieval


