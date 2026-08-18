from app.services.pdf_extraction_service import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.chunk_service import create_chunks


PDF_PATH = r"..\..\data\uploads\rag_document_ai_project_report (2).pdf"


pages = extract_text_from_pdf(PDF_PATH)

cleaned_pages = [
    {
        "page_number": page["page_number"],
        "text": clean_text(page["text"]),
    }
    for page in pages
]

chunks = create_chunks(cleaned_pages)

print(f"Pages: {len(pages)}")
print(f"Chunks: {len(chunks)}")

for chunk in chunks:
    print(
        f"\n--- Chunk {chunk['chunk_index']} "
        f"| Page {chunk['page_number']} ---"
    )
    print(chunk["text"][:200])