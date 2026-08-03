"""Verify the native Windows Python development environment."""

from __future__ import annotations

import importlib
import importlib.metadata
import platform
import sys
from pathlib import Path

REQUIRED_PACKAGES = {
    "torch": "PyTorch",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "qdrant-client": "Qdrant client",
    "sentence-transformers": "Sentence Transformers",
    "transformers": "Transformers",
    "accelerate": "Accelerate",
    "peft": "PEFT",
    "trl": "TRL",
    "bitsandbytes": "bitsandbytes",
    "fastapi": "FastAPI",
    "pydantic": "Pydantic",
}

IMPORT_NAMES = {
    "qdrant-client": "qdrant_client",
    "sentence-transformers": "sentence_transformers",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def package_version(package_name: str) -> str:
    return importlib.metadata.version(package_name)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    venv_root = project_root / ".venv"
    executable = Path(sys.executable).resolve()

    print("Environment report")
    print("==================")
    print(f"Operating system: {platform.platform()}")
    print(f"Python executable: {executable}")
    print(f"Python version: {platform.python_version()}")
    print(f"Python architecture: {platform.architecture()[0]}")

    if sys.version_info[:2] != (3, 11):
        fail("Python must be 3.11.")
    if platform.architecture()[0] != "64bit":
        fail("Python must be 64-bit.")
    if venv_root.resolve() not in executable.parents:
        fail(f"Interpreter is not inside project .venv: {venv_root}")

    print()
    print("Package versions")
    print("----------------")
    for package_name, label in REQUIRED_PACKAGES.items():
        import_name = IMPORT_NAMES.get(package_name, package_name.replace("-", "_"))
        try:
            importlib.import_module(import_name)
            version = package_version(package_name)
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            fail(f"Could not import {label} ({package_name}): {exc}")
        print(f"{label}: {version}")

    import torch

    print()
    print("CUDA report")
    print("-----------")
    print(f"PyTorch CUDA build: {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print("CUDA is unavailable; CPU-only PyTorch mode is active.")
        print()
        print("Qdrant local mode")
        print("-----------------")
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(":memory:")
            collections = client.get_collections()
        except (ImportError, RuntimeError, ValueError) as exc:
            fail(f"Qdrant local in-memory mode failed: {exc}")
        print(f"Qdrant local mode: passed ({len(collections.collections)} collections)")
        print()
        print("Environment verification passed.")
        return

    gpu_count = torch.cuda.device_count()
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory_gib = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"GPU count: {gpu_count}")
    print(f"GPU name: {gpu_name}")
    print(f"GPU memory: {gpu_memory_gib:.2f} GiB")

    try:
        a = torch.tensor([1.0, 2.0, 3.0], device="cuda")
        b = torch.tensor([4.0, 5.0, 6.0], device="cuda")
        c = a + b
        torch.cuda.synchronize()
    except RuntimeError as exc:
        fail(f"GPU tensor calculation failed: {exc}")
    if c.device.type != "cuda" or c.tolist() != [5.0, 7.0, 9.0]:
        fail("GPU tensor calculation returned an unexpected result.")
    print(f"GPU tensor test: passed on {c.device}")

    print()
    print("Qdrant local mode")
    print("-----------------")
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        collections = client.get_collections()
    except (ImportError, RuntimeError, ValueError) as exc:
        fail(f"Qdrant local in-memory mode failed: {exc}")
    print(f"Qdrant local mode: passed ({len(collections.collections)} collections)")

    print()
    print("Environment verification passed.")


if __name__ == "__main__":
    main()

