SAMPLE = """
Retrieval-augmented generation combines an information retrieval system with a
generative model. In a RAG pipeline, documents are first split into smaller
chunks. Each chunk is embedded into a vector space so that semantically similar
texts are close together. At query time, the user's question is embedded and
used to find the most similar chunks. These retrieved chunks are then passed to
a language model, which writes a grounded answer using only the provided
context.

The main benefits of RAG are reduced hallucination, up-to-date knowledge, and
the ability to ground answers in private or proprietary documents without
fine-tuning the underlying model.
"""


def test_full_rag_flow(client, auth_headers):
    # Ingest a document
    r = client.post(
        "/api/v1/documents",
        json={"title": "RAG Guide", "content": SAMPLE, "source": "docs/rag.txt"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "RAG Guide"
    assert body["chunk_count"] >= 1
    doc_id = body["id"]

    # List documents
    r = client.get("/api/v1/documents", headers=auth_headers)
    assert r.status_code == 200
    ids = [d["id"] for d in r.json()]
    assert doc_id in ids

    # Query that should retrieve the RAG chunk
    r = client.post(
        "/api/v1/documents/query",
        json={"question": "What is retrieval-augmented generation?", "top_k": 3},
        headers=auth_headers,
    )
    assert r.status_code == 200
    qb = r.json()
    assert qb["question"]
    assert qb["answer"]
    assert len(qb["sources"]) >= 1
    assert qb["sources"][0]["document_id"] == doc_id

    # Delete
    r = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert r.status_code == 204
    r = client.get("/api/v1/documents", headers=auth_headers)
    assert doc_id not in [d["id"] for d in r.json()]


def test_requires_auth(client):
    resp = client.get("/api/v1/documents")
    assert resp.status_code == 401
    resp = client.post("/api/v1/documents/query", json={"question": "hi"})
    assert resp.status_code == 401


def test_tenant_isolation(client, auth_headers):
    # First user ingests a doc
    client.post(
        "/api/v1/documents",
        json={"title": "Private", "content": "secret project plan for alpha"},
        headers=auth_headers,
    )
    # Second user registers + queries; must not see first user's chunks
    client.post(
        "/api/v1/auth/register",
        json={"email": "b@example.com", "password": "secret123"},
    )
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "b@example.com", "password": "secret123"},
    )
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    resp = client.post(
        "/api/v1/documents/query",
        json={"question": "secret project plan"},
        headers=headers,
    )
    assert resp.json()["sources"] == []