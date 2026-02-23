from transformers import AutoTokenizer, BertJapaneseTokenizer
import os

model_id = "hotchpotch/japanese-splade-base-v1"

def check_tokenizer(name, tok):
    print(f"--- {name} ---")
    print(f"Type: {type(tok)}")
    print(f"Vocab size: {len(tok) if hasattr(tok, '__len__') else 'N/A'}")
    tokens = ["こんにちは", "スクラップボックス", "RAG"]
    for t in tokens:
        ids = tok.encode(t, add_special_tokens=False)
        decoded = [tok.decode([i]) for i in ids]
        print(f"Text: {t} -> IDs: {ids} -> Decoded: {decoded}")
    
    # Check specific IDs from previous run
    sample_ids = [465, 12509, 14054]
    print(f"Sample IDs {sample_ids} -> {[tok.decode([i]) for i in sample_ids]}")
    print(f"Sample IDs {sample_ids} -> {tok.convert_ids_to_tokens(sample_ids)}")

print("Attempting to load tokenizers...")

try:
    check_tokenizer("AutoTokenizer", AutoTokenizer.from_pretrained(model_id))
except Exception as e:
    print(f"AutoTokenizer Error: {e}")

try:
    # Explicitly try BertJapaneseTokenizer
    check_tokenizer("BertJapaneseTokenizer", BertJapaneseTokenizer.from_pretrained(model_id))
except Exception as e:
    print(f"BertJapaneseTokenizer Error: {e}")

try:
    # Try Tohoku BERT v3
    check_tokenizer("cl-tohoku/bert-base-japanese-v3", AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese-v3"))
except Exception as e:
    print(f"Tohoku v3 Error: {e}")
