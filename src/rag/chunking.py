#pip install semantic_chunkers

import os
from semantic_chunkers.chunkers.regex import RegexChunker
from pprint import pprint
import uuid
from tokenization import *
regex_chunker = RegexChunker()

def read_md(path):
  with open(path, 'r', encoding='utf-8') as f:
    return f.read()

def process_file(path): 
  ##Code
  return None

def process_data(path, chunker=regex_chunker):
  """
  Path chứa các corpus (public1,..., public N). Mình sẽ chunk theo từng đống đó
  Path là file .md
  """
  objs=[]
  for file in os.listdir(path):
    file_path = os.path.join(path,file)
    if os.path.isfile(file_path): 
      raw_data = read_md(file_path)
      chunks = chunker([raw_data])[0]
      for chunk in chunks: 
        content = tokenize(" ".join(chunk.splits)).strip().lower()
        objs.append({
          "source": file,
          "metadata": '<UNK>',
          "chunk_id": str(uuid.uuid4()),
          "content" : content
        })
  pprint(objs[0])
  print(len(objs))
  return objs

# process_data('D:\Folder F\phamtuananh@23020010\My Study\ViettelAIRace\corpus')
