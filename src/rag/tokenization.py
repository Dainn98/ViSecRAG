# !pip install -q underthesea
from underthesea import word_tokenize
def tokenize(segment_text, format="text"):
    return word_tokenize(segment_text,
                        format).strip().lower()

# print(tokenize('Tuấn Anh là số 2'))