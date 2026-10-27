from app.services.embeddings import embedding_service


def test_embedding_norm():
    vec = embedding_service.embed("hello world")
    assert len(vec) == embedding_service.dim
    # normalized -> unit-ish norm
    import math
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 1e-3


def test_cosine_similar():
    a = embedding_service.embed("machine learning models")
    b = embedding_service.embed("machine learning model training")
    c = embedding_service.embed("banana smoothie recipe")
    assert embedding_service.cosine_similarity(a, b) > embedding_service.cosine_similarity(a, c)