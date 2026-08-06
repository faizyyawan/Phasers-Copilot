"""Load Markdown knowledge-base files into LangChain Document objects."""

from pathlib import Path

from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge-base"


def find_markdown_files() -> list[Path]:
    """Find support Markdown files directly inside the knowledge base."""
    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge-base folder not found: {KNOWLEDGE_BASE_DIR}"
        )

    if not KNOWLEDGE_BASE_DIR.is_dir():
        raise NotADirectoryError(
            f"Knowledge-base path is not a folder: {KNOWLEDGE_BASE_DIR}"
        )

    markdown_files = sorted(
        file_path
        for file_path in KNOWLEDGE_BASE_DIR.glob("*.md")
        if file_path.name.lower() != "readme.md"
    )

    return markdown_files


def read_markdown_file(file_path: Path) -> str:
    """Read a non-empty Markdown file as UTF-8 text."""
    if not file_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    if file_path.is_dir():
        raise IsADirectoryError(f"Expected a Markdown file, got directory: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError(f"Markdown file is empty: {file_path.name}")

    return content


def create_document(file_path: Path) -> Document:
    """Create a LangChain Document from one Markdown file."""
    content = read_markdown_file(file_path)
    metadata = {
        "source": file_path.name,
        "document_id": file_path.stem,
        "file_type": "markdown",
    }

    return Document(page_content=content, metadata=metadata)


def load_documents() -> list[Document]:
    """Load all support Markdown files into LangChain Documents."""
    markdown_files = find_markdown_files()
    return [create_document(file_path) for file_path in markdown_files]


if __name__ == "__main__":
    markdown_files = find_markdown_files()
    documents = load_documents()

    print(f"Current file: {Path(__file__).resolve()}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Knowledge base: {KNOWLEDGE_BASE_DIR}")
    print(f"Knowledge base exists: {KNOWLEDGE_BASE_DIR.exists()}")
    print("Markdown files:")
    for file_path in markdown_files:
        print(f"- {file_path.name}")
    print(f"Loaded documents: {len(documents)}")
    if documents:
        print(f"First document metadata: {documents[0].metadata}")
        print(f"First document characters: {len(documents[0].page_content)}")
