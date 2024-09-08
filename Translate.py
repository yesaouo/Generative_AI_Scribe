from googletrans import Translator
import re

def split_text_by_hash(text, chunk_size):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        # 找到下一個 '\n' 的位置
        hash_index = text.find('\n', end)
        if hash_index == -1:
            chunks.append(text[start:])
            break
        # 將段落加入陣列並更新 start
        chunks.append(text[start:hash_index + 1])
        start = hash_index + 1
    return chunks

def zh_translate_en(text):
    if re.search(r'[\u4e00-\u9fff]', text):
        translator = Translator()
        translation = translator.translate(text, src="zh-TW")
        return translation.text
    else:
        return text

def long_zh_translate_en(text):
    if re.search(r'[\u4e00-\u9fff]', text):
        chunks = split_text_by_hash(text, 4096)
        text = ''

        for chunk in chunks:
            text += zh_translate_en(chunk) + '\n'

        return text
    else:
        return text
