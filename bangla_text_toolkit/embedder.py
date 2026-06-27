"""
bangla_text_toolkit/embedder.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Character n-gram hashing embedder for Bangla tokens.

Produces fixed-length dense vectors for any pre-tokenised Bangla token by:

1. Extracting all character n-grams in a configurable size range.
2. Hashing each n-gram to a bucket in ``[0, dim)`` using a stable polynomial
   hash (no Python hash-randomisation involved).
3. Incrementing the corresponding bucket.
4. Optionally L2-normalising the resulting vector.

This is the same subword representation strategy used by fastText, adapted for
zero-dependency pure Python with native Bangla Unicode support.

Example::

    from bangla_text_toolkit.tokenizer import BanglaTokenizer
    from bangla_text_toolkit.embedder import BanglaEmbedder

    tok = BanglaTokenizer()
    tokens = tok.tokenize("আমি বাংলায় গান গাই")

    emb = BanglaEmbedder(dim=32)
    doc_vec = emb.embed_document(tokens)
    print(len(doc_vec))   # 32
    print(round(sum(x*x for x in doc_vec) ** 0.5, 6))  # ~1.0 (normalised)
"""

from __future__ import annotations

import math


class BanglaEmbedder:
    """Character n-gram hashing embedder for pre-tokenised Bangla text.

    Parameters
    ----------
    dim:
        Embedding vector length.  Must be >= 1.
    ngram_range:
        ``(min_n, max_n)`` — inclusive range of character n-gram sizes to
        extract from each token.  Must satisfy ``1 <= min_n <= max_n``.
    normalize:
        If ``True`` (default), L2-normalise each output vector so its
        Euclidean norm equals 1.  Zero vectors are returned as-is.
    """

    def __init__(
        self,
        dim: int = 64,
        ngram_range: tuple[int, int] = (2, 4),
        normalize: bool = True,
    ) -> None:
        if dim < 1:
            raise ValueError(f"dim must be >= 1, got {dim!r}")
        min_n, max_n = ngram_range
        if min_n < 1 or max_n < min_n:
            raise ValueError(
                f"ngram_range must satisfy 1 <= min_n <= max_n, got {ngram_range!r}"
            )
        self.dim = dim
        self.ngram_range = ngram_range
        self.normalize = normalize

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_token(self, token: str) -> list[float]:
        """Return a ``dim``-length embedding vector for *token*.

        Returns a zero vector for tokens that produce no n-grams (e.g. tokens
        shorter than ``min_n``).
        """
        vec = [0.0] * self.dim
        ngrams = self._extract_ngrams(token)
        if not ngrams:
            return vec
        for ng in ngrams:
            vec[self._hash_ngram(ng)] += 1.0
        if self.normalize:
            vec = _l2_normalize(vec)
        return vec

    def embed_tokens(self, tokens: list[str]) -> list[list[float]]:
        """Embed each token in *tokens* independently.

        Returns a list of ``dim``-length vectors in the same order.
        """
        return [self.embed_token(tok) for tok in tokens]

    def embed_document(self, tokens: list[str]) -> list[float]:
        """Return the mean token embedding for *tokens*.

        The mean is computed over individual token vectors (each already
        normalised when ``normalize=True``), then optionally re-normalised.

        Returns a zero vector for empty *tokens*.
        """
        if not tokens:
            return [0.0] * self.dim
        vecs = self.embed_tokens(tokens)
        n = len(vecs)
        mean = [sum(vecs[i][j] for i in range(n)) / n for j in range(self.dim)]
        if self.normalize:
            mean = _l2_normalize(mean)
        return mean

    def embed_corpus(
        self,
        corpus: list[list[str]],
    ) -> list[list[float]]:
        """Return one document embedding per entry in *corpus*.

        Parameters
        ----------
        corpus:
            List of pre-tokenised documents.

        Returns
        -------
        List of ``dim``-length vectors, one per document.
        """
        return [self.embed_document(doc) for doc in corpus]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_ngrams(self, token: str) -> list[str]:
        """Return all character n-grams of sizes in *ngram_range* from *token*."""
        min_n, max_n = self.ngram_range
        length = len(token)
        ngrams: list[str] = []
        for size in range(min_n, max_n + 1):
            for start in range(length - size + 1):
                ngrams.append(token[start : start + size])
        return ngrams

    def _hash_ngram(self, ngram: str) -> int:
        """Stable polynomial hash of *ngram* into ``[0, dim)``.

        Uses a simple Bernstein-style hash so results are identical across
        Python sessions regardless of hash-randomisation settings.
        """
        h = 0
        for ch in ngram:
            h = (h * 31 + ord(ch)) % self.dim
        return h


# ------------------------------------------------------------------
# Module-level helper (not part of public API)
# ------------------------------------------------------------------

def _l2_normalize(vec: list[float]) -> list[float]:
    """Return a new L2-normalised copy of *vec*.  Returns *vec* if norm == 0."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec[:]
    return [x / norm for x in vec]
