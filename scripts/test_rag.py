from multi_tool_agent.rag import query_rag_embeddings

query = "What are the major humanitarian and economic impacts of regional conflicts?"
results = query_rag_embeddings(query, top_k=3)

print(f"Query: {query}\n")
for i, res in enumerate(results, 1):
    print(f"--- Match {i} (Distance: {res['distance']:.4f}) ---")
    print(f"Title: {res['document_title']}")
    print(f"Chunk: {res['content_chunk']}")
    print(f"Metadata: {res['metadata']}\n")