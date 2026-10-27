from app.services.chunker import chunk_text


def test_paragraph_split():
    # Three 300-char paragraphs, each hard-split into 2 chunks at size=200
    text = "A" * 300 + "\n\n" + "B" * 300 + "\n\n" + "C" * 300
    chunks = chunk_text(text, size=200, overlap=0)
    assert len(chunks) == 6
    # Every chunk respects the size bound
    assert all(len(c) <= 200 for c in chunks)


def test_hard_split_long_block():
    text = "a" * 1000
    chunks = chunk_text(text, size=100, overlap=10)
    assert all(len(c) <= 100 for c in chunks)
    assert len(chunks) > 1
