"""Split loaded Markdown documents into smaller retrieval chunks."""

from collections import Counter

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

if __package__:
    from .load_documents import load_documents
else:
    # Allow this file to be run directly by VS Code Code Runner.
    from load_documents import load_documents

DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200

HEADERS_TO_SPLIT_ON = [
    ("#", "header_1"),
    ("##", "header_2"),
    ("###", "header_3"),
]


def validate_split_settings(chunk_size: int, chunk_overlap: int) -> None:
    """Validate character-based chunk size settings."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must not be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")


def validate_documents(documents: list[Document]) -> None:
    """Validate that the splitter received non-empty LangChain documents."""
    if not isinstance(documents, list):
        raise TypeError("documents must be a list of LangChain Document objects.")

    for index, document in enumerate(documents):
        if not isinstance(document, Document):
            raise TypeError(
                f"documents[{index}] must be a LangChain Document object."
            )

        if not document.page_content.strip():
            raise ValueError(
                f"documents[{index}] has empty page_content and cannot be split."
            )


def split_documents(
    documents: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Split loaded Markdown documents into smaller LangChain Documents.

    The baseline is character-based: chunk_size and chunk_overlap are measured
    in characters, not tokens. Empty input is valid and returns an empty list.
    Empty source documents are rejected because they cannot produce useful
    retrieval chunks.
    """
    validate_split_settings(chunk_size, chunk_overlap)
    validate_documents(documents)

    if not documents:
        return []

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Document] = []

    for document in documents:
        chunk_index = 0
        document_id = document.metadata["document_id"]
        markdown_sections = markdown_splitter.split_text(document.page_content)

        for section in markdown_sections:
            section_metadata = {
                **document.metadata,
                **section.metadata,
            }

            section_chunks = text_splitter.split_text(section.page_content)
            for chunk_text in section_chunks:
                cleaned_chunk_text = chunk_text.strip()
                if not cleaned_chunk_text:
                    continue

                chunk_metadata = dict(section_metadata)
                chunk_metadata["chunk_index"] = chunk_index
                chunk_metadata["chunk_id"] = (
                    f"{document_id}-chunk-{chunk_index:03d}"
                )

                chunks.append(
                    Document(
                        page_content=cleaned_chunk_text,
                        metadata=chunk_metadata,
                    )
                )
                chunk_index += 1

    return chunks


def _print_split_report(documents: list[Document], chunks: list[Document]) -> None:
    """Print a compact manual report for local inspection."""
    chunk_lengths = [len(chunk.page_content) for chunk in chunks]
    chunks_per_source = Counter(chunk.metadata["source"] for chunk in chunks)
    chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]

    print(f"Full documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print("Chunk count per source file:")
    for source, count in sorted(chunks_per_source.items()):
        print(f"- {source}: {count}")

    if chunks:
        first_chunk = chunks[0]
        preview = first_chunk.page_content[:300].replace("\n", " ")
        print(f"First chunk metadata: {first_chunk.metadata}")
        print(f"First chunk characters: {len(first_chunk.page_content)}")
        print(f"First chunk preview: {preview}")
        print(f"Minimum chunk length: {min(chunk_lengths)}")
        print(f"Maximum chunk length: {max(chunk_lengths)}")
        print(f"Average chunk length: {sum(chunk_lengths) / len(chunk_lengths):.1f}")

    original_metadata_preserved = all(
        chunk.metadata.get("source") == document.metadata.get("source")
        and chunk.metadata.get("document_id") == document.metadata.get("document_id")
        and chunk.metadata.get("file_type") == document.metadata.get("file_type")
        for document in documents
        for chunk in chunks
        if chunk.metadata.get("document_id") == document.metadata.get("document_id")
    )
    chunk_ids_unique = len(chunk_ids) == len(set(chunk_ids))

    print(f"Original metadata preserved: {original_metadata_preserved}")
    print(f"Chunk IDs unique: {chunk_ids_unique}")


if __name__ == "__main__":
    loaded_documents = load_documents()
    split_chunks = split_documents(loaded_documents)
    _print_split_report(loaded_documents, split_chunks)
