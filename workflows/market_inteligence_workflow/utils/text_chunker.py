def chunk_text(text, chunk_size=5000):

    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
