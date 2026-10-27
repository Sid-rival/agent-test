"""Embedding service.

Provides a pluggable interface. The default implementation is a
deterministic, dependency-free hashing embedder (bag-of-tokens hashed into a
fixed-dimension vector) so the service runs end-to-end with no external API
keys. Swap in a real model (e.g. sentence-transformers) by implementing the
same interface.
"""
import hashlib
import json
import math
import re

import numpy as np

from app.core.config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class EmbeddingService:
    def __init__(self, dim: int | None = None):
        self.dim = dim or settings.embedding_dim

    def embed(self, text: str) -> list[float]:
        """Return a normalized embedding vector for the given text."""
        tokens = _TOKEN_RE.findall(text.lower())
        vec = np.zeros(self.dim, dtype=np.float32)
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def encode_vector(self, vec: list[float]) -> str:
        return json.dumps(vec)

    def decode_vector(self, raw: str) -> list[float]:
        return json.loads(raw)

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        return float(np.dot(a, b))  # both normalized


embedding_service = EmbeddingService()