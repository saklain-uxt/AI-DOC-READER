from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Sample text
sentences = [
    "Customer satisfaction is important for businesses.",
    "Customer feedback helps improve product quality."
]

# Generate embeddings
embeddings = model.encode(
    sentences,
    normalize_embeddings=True
)

# Verify results
print("Model loaded successfully!")
print("Number of sentences:", len(embeddings))
print("Embedding dimensions:", embeddings.shape[1])
print("First embedding length:", len(embeddings[0]))
print("First 5 values:", embeddings[0][:5])