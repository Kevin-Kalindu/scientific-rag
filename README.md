# Scientific Paper RAG (multimodal, fully local)

Ask questions about scientific papers and get answers with numbered citations, plus the exact figure or table image the answer came from. The system reads PDFs from arXiv, extracts **body text, tables and figures**, indexes them in a vector database, and answers with a local vision-language model.

Everything runs on your own machine. There are **no API keys, no accounts and no cost**, and nothing is sent to an outside service after the one-time model downloads.


## What it does

- Downloads papers from arXiv and parses each PDF into three kinds of chunks: text windows, tables (as Markdown plus a cropped image) and figures (caption plus a cropped image).
- Embeds text with `bge-small-en-v1.5` and images with CLIP, and stores both in two Qdrant collections.
- Retrieves with hybrid search: a text search and an image search are merged with Reciprocal Rank Fusion (RRF).
- Generates a grounded answer with a local vision model through Ollama, citing sources as `[1]`, `[2]`, and saying so when the sources do not contain the answer.

## Architecture

```
INGEST (once per paper)
PDF --> extract.py --> Chunks: text | table | figure
                            |
              +-------------+--------------+
              v                            v
   text embeddings (bge-small)    image embeddings (CLIP)
              |                            |
              v                            v
   Qdrant: paper_text            Qdrant: paper_images
   (text, tables, captions)      (figure + table crops)

ANSWER (every question)
question --> embed --> search both collections --> fuse ranks (RRF) --> top chunks
         --> local vision LLM (Ollama) sees text + images --> answer with [1] [2] citations
```

**Design choices worth knowing**

- **Figures are indexed twice**, by caption (text embedding) and by pixels (CLIP), under the same ID. When both searches return the same figure, rank fusion boosts it.
- **Deterministic chunk IDs** (a hash of paper, kind, page, label and text) make ingestion idempotent: re-running it never creates duplicates.
- **RRF uses ranks, not scores**, because text and CLIP similarity scores are not comparable.
- **Images are labelled in the prompt.** Ollama attaches images separately from the text, so each image is tied to its source number to keep citations accurate.

## Tech stack

PyMuPDF, arXiv API, sentence-transformers (bge-small, CLIP), Qdrant (embedded), Ollama, Streamlit, pytest.

