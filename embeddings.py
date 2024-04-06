import ollama 


def get_embeddings(filename: str) -> list[float]:

    with open('./pages/' + file, 'r') as f:
        text = f.read()

    embeddings = ollama.embeddings(
        model='mxbai-embed-large',
        prompt=text
    )

    if not embeddings:
        return None

    response = {
        'embedding': embeddings['embedding'],
        'text': text,
        'filename': filename
    }

    return response


if __name__ == "__main__":
    import os
    import pickle
    from tqdm import tqdm

    all_embeddings = []
    for file in tqdm(os.listdir('./pages')):
        response = get_embeddings(file)
        if response:
            all_embeddings.append(response)

    with open('embeddings.pkl', 'wb') as f:
        pickle.dump(all_embeddings, f)
            