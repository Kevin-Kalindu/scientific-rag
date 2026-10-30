import ollama
from .config import ASSET_DIR, LLM_MODEL, MAX_IMAGES, LLM_CONTEXT

SYSTEM = (
    'You answer questions about scientific papers using ONLY the numbered sources provided. '
    'Cite every claim with its source number, like [1] or [2][3]. '
    'If the sources do not contain the answer, say so instead of guessing. '
    'Some sources come with an image of a figure or table: read it carefully '
    'when the question depends on it.'
)

def build_prompt(question, hits, max_images=MAX_IMAGES):
    text, images, notes = '', [], []
    for i, hit in enumerate(hits, start=1):
        pl = hit.payload
        label = pl['label'] or pl['kind']
        text += f"[{i}] {pl['title']} | {label} | page {pl['page']}\n{pl['text']}\n\n"
        if pl['image_path'] and len(images) < max_images:
            images.append(str(ASSET_DIR / pl['image_path']))
            notes.append(f'Attached image {len(images)} shows source [{i}] ({label}).')
    prompt = text + '\n'.join(notes) + f'\n\nQuestion: {question}'
    return prompt, images

def answer(question, hits):
    prompt, images = build_prompt(question, hits)
    try:
        reply = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM},
                {'role': 'user', 'content': prompt, 'images': images},
            ],
            options={'temperature': 0.1, 'num_ctx': LLM_CONTEXT},
        )
    except Exception as e:
        raise RuntimeError('Could not get an answer from Ollama. Is the app running, and did you '
                           f'run "ollama pull {LLM_MODEL}"? Original error: {e}') from e
    return reply['message']['content']