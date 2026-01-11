# RAG Module - Modular Architecture

A clean, modular implementation of Retrieval-Augmented Generation (RAG) for document-based question answering in the Technical Analyst Agent.

## 📁 Module Structure

```
rag/
├── __init__.py                 # Package initialization
├── rag_engine.py              # Main orchestrator
├── document_types.py          # Document type definitions
├── prompts.py                 # All system prompts
├── document_loader.py         # File loading (PDF, DOCX, TXT, MD)
├── document_processor.py      # Chunking, classification, metadata
├── embeddings_manager.py      # Google AI embeddings
├── vector_store.py            # FAISS vector storage
├── query_processor.py         # Query classification
└── answer_generator.py        # Answer generation with LLM
```

## 🏗️ Architecture Overview

### Component Responsibilities

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **RAGEngine** | Main orchestrator | `ingest_document()`, `query()`, `chat()` |
| **DocumentLoader** | Load files | `load_document()`, `get_supported_extensions()` |
| **DocumentProcessor** | Process docs | `split_documents()`, `classify_document_type()` |
| **EmbeddingsManager** | Create embeddings | `get_embeddings()`, `embed_query()` |
| **VectorStoreManager** | Store & search | `add_documents()`, `similarity_search()` |
| **QueryProcessor** | Classify queries | `classify_query()`, `extract_tickers()` |
| **AnswerGenerator** | Generate answers | `generate_answer()`, `format_sources()` |
| **DocumentType** | Type definitions | Classification constants |
| **RAGPrompts** | System prompts | All prompt templates |

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DOCUMENT INGESTION                       │
└─────────────────────────────────────────────────────────────┘
  Upload PDF/DOCX/TXT/MD
         ↓
  [DocumentLoader] ─→ Load file content
         ↓
  [DocumentProcessor] ─→ Classify type, split into chunks
         ↓
  [EmbeddingsManager] ─→ Create embeddings
         ↓
  [VectorStoreManager] ─→ Store in FAISS


┌─────────────────────────────────────────────────────────────┐
│                         QUERY FLOW                           │
└─────────────────────────────────────────────────────────────┘
  User Question
         ↓
  [QueryProcessor] ─→ Classify intent, extract tickers
         ↓
  [VectorStoreManager] ─→ Similarity search
         ↓
  [AnswerGenerator] ─→ Generate answer with citations
         ↓
  Return answer + sources + scores
```

## 🚀 Usage Examples

### Basic Usage

```python
from ta_agent.src.ai_agent.rag import RAGEngine

# Initialize
engine = RAGEngine()

# Ingest document
result = engine.ingest_document(
    "apple_earnings_q4_2024.pdf",
    metadata={
        "ticker": "AAPL",
        "doc_type": "financial_report",
        "description": "Q4 2024 Earnings Report"
    }
)

# Query
result = engine.query("What was Apple's revenue in Q4 2024?")
print(result["answer"])
print(f"Sources: {len(result['sources'])}")
```

### Advanced Usage

```python
# Query with filters
result = engine.query(
    "Tell me about iPhone sales",
    k=10,  # Get top 10 documents
    score_threshold=0.5,  # Minimum relevance
    doc_type_filter="financial_report",
    ticker_filter="AAPL"
)

# Chat interface
history = []
result = engine.chat(
    "What was the revenue?",
    history=history,
    k=5
)
history = result["history"]

# Get statistics
stats = engine.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Embeddings: {stats['embeddings_model']['model']}")

# List all documents
docs = engine.get_document_list()
for doc in docs:
    print(f"{doc['filename']} - {doc['doc_type']}")
```

## 🔧 Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

### Customization

```python
from pathlib import Path

engine = RAGEngine(
    storage_path=Path("custom/storage/path"),
    google_api_key="your_key",
    groq_api_key="your_key"
)
```

### Chunk Settings

Edit in `document_processor.py`:
```python
chunk_size=1000,      # Characters per chunk
chunk_overlap=200     # Overlap between chunks
```

## 📝 Prompt Management

All prompts are centralized in `prompts.py`:

- **DOCUMENT_CLASSIFIER** - Classifies document types
- **QUERY_CLASSIFIER** - Extracts query intent
- **ANSWER_GENERATOR_SYSTEM** - System prompt for answers
- **ANSWER_GENERATOR_USER** - User prompt template
- **HYBRID_INTEGRATION_SYSTEM** - Combines docs + market data
- **HYBRID_INTEGRATION_USER** - Hybrid query template

To modify prompts:
```python
from ta_agent.src.ai_agent.rag.prompts import RAGPrompts

# Access any prompt
classifier = RAGPrompts.DOCUMENT_CLASSIFIER
```

## 🎯 Supported Document Types

| Type | Description | Examples |
|------|-------------|----------|
| `financial_report` | Financial statements | 10-K, earnings reports |
| `research_paper` | Academic/market research | Analyst reports, whitepapers |
| `trading_strategy` | Strategy documents | Backtests, algo strategies |
| `market_news` | News articles | Press releases, market news |
| `personal_notes` | User notes | Trading journals, ideas |
| `general` | Any other type | Misc documents |

## 📄 Supported File Formats

- **PDF** (.pdf) - Adobe PDF documents
- **Word** (.docx) - Microsoft Word documents
- **Text** (.txt) - Plain text files
- **Markdown** (.md) - Markdown documents

## 🔍 Query Classification

The system automatically classifies queries into:

1. **document_search** - Answered from documents only
2. **market_data** - Requires real-time market data
3. **hybrid** - Needs both documents and market data

### Example Classifications

| Query | Type | Requires Docs | Requires Market |
|-------|------|---------------|-----------------|
| "What was revenue?" | document_search | ✅ | ❌ |
| "What's AAPL's current price?" | market_data | ❌ | ✅ |
| "Compare earnings to stock price" | hybrid | ✅ | ✅ |

## 🧪 Testing Each Component

### Test Document Loader
```python
from ta_agent.src.ai_agent.rag.document_loader import DocumentLoader

docs = DocumentLoader.load_document("test.pdf")
print(f"Loaded {len(docs)} pages")
```

### Test Embeddings
```python
from ta_agent.src.ai_agent.rag.embeddings_manager import EmbeddingsManager

manager = EmbeddingsManager()
vector = manager.embed_query("test query")
print(f"Vector dimensions: {len(vector)}")
```

### Test Document Processor
```python
from ta_agent.src.ai_agent.rag.document_processor import DocumentProcessor
from langchain_groq import ChatGroq

llm = ChatGroq(model="openai/gpt-oss-120b")
processor = DocumentProcessor(llm)

doc_type = processor.classify_document_type("Annual Report 2024...")
print(f"Type: {doc_type}")
```

### Test Vector Store
```python
from ta_agent.src.ai_agent.rag.vector_store import VectorStoreManager
from pathlib import Path

store = VectorStoreManager(Path("test_storage"), embeddings)
results = store.similarity_search("test query", k=5)
print(f"Found {len(results)} results")
```

## 🐛 Debugging

Enable detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Check component status:
```python
stats = engine.get_stats()
print(stats)
```

## ⚡ Performance Tips

1. **Batch ingestion**: Ingest multiple documents before querying
2. **Adjust k**: Lower k (3-5) for faster, focused results
3. **Use filters**: Apply doc_type and ticker filters to narrow search
4. **Score threshold**: Set score_threshold to filter low-relevance results
5. **Chunk size**: Smaller chunks (500-800) for precise results, larger (1000-1500) for context

## 🔒 Security Notes

- API keys should be in `.env` file, never in code
- FAISS index files are stored locally
- Document content is stored in vector form (embeddings)
- Original documents are not stored by default

## 📊 System Requirements

- Python 3.9+
- FAISS (CPU or GPU)
- Google Generative AI API access
- Groq API access
- Sufficient disk space for FAISS index

## 🆘 Common Issues

### "GOOGLE_API_KEY is required"
Set in `.env`: `GOOGLE_API_KEY=your_key`

### "No documents found"
Check: `engine.get_document_list()` to see ingested docs

### Low relevance scores
- Improve query wording
- Ensure relevant documents are ingested
- Lower score_threshold

### Memory issues
- Reduce chunk_size
- Lower k parameter
- Process fewer documents at once

## 🎓 Learning Path

1. **Start here**: `rag_engine.py` - Main orchestrator
2. **Understand flow**: Follow `ingest_document()` and `query()` methods
3. **Explore components**: Read each module's docstrings
4. **Customize prompts**: Edit `prompts.py`
5. **Extend functionality**: Add new document types, loaders, or processors

## 📚 API Reference

See individual module docstrings for detailed API documentation:
- Each class has comprehensive docstrings
- All methods include parameter descriptions
- Return types are documented

## 🤝 Contributing

When extending the system:
1. Keep Single Responsibility Principle
2. Add logging for debugging
3. Write docstrings
4. Handle errors gracefully
5. Update this README

## 📝 License

Part of the Technical Analyst Agent project.
