# RAG Integration Package

**Unified interface combining RAG engine with technical analysis**

## 📁 Package Structure

```
integration/
├── __init__.py              # Package exports
├── integrated_agent.py      # Main unified agent
├── query_processor.py       # Query handling & data fetching
├── synthesis_engine.py      # Multi-source synthesis
├── chat_handler.py          # Conversational interface
└── README.md                # This file
```

---

## 🎯 Architecture

### **Module Responsibilities:**

| Module | Responsibility | Lines |
|--------|---------------|-------|
| `integrated_agent.py` | Main orchestrator, public API | ~170 |
| `query_processor.py` | Query classification, data fetching | ~150 |
| `synthesis_engine.py` | Document + technical synthesis | ~180 |
| `chat_handler.py` | Conversation memory management | ~140 |

**Total:** ~640 lines (vs original 269 lines, better organized with more features)

---

## 🚀 Quick Start

### **Basic Usage:**

```python
from src.ai_agent.integration import IntegratedRAGAgent

# Initialize agent
agent = IntegratedRAGAgent(rag_storage_path="./data/rag_storage")

# Ingest document
result = agent.ingest_document(
    "annual_report.pdf",
    metadata={"ticker": "AAPL", "year": 2024}
)

# Query with both document and market context
response = agent.query(
    "What are the revenue growth risks and how does the current technical setup look?",
    ticker="AAPL",
    include_technical_analysis=True
)

print(response['integrated_answer'])
```

### **Conversational Interface:**

```python
# Start conversation
conversation_history = None

# First message
response1 = agent.chat(
    "Tell me about AAPL's financial health",
    ticker="AAPL",
    conversation_history=conversation_history
)
conversation_history = response1['conversation_history']

# Follow-up with context
response2 = agent.chat(
    "What about the technical indicators?",
    ticker="AAPL",
    conversation_history=conversation_history
)
conversation_history = response2['conversation_history']

# Get conversation summary
summary = agent.get_conversation_summary(conversation_history)
print(f"Topics discussed: {summary['topics']}")
```

### **Document Management:**

```python
# List all documents
documents = agent.get_document_list()
for doc in documents:
    print(f"{doc['doc_id']}: {doc['doc_type']} - {doc['metadata']}")

# Get statistics
stats = agent.get_statistics()
print(f"Total documents: {stats['total_documents']}")
print(f"Total chunks: {stats['total_chunks']}")

# Delete document
agent.delete_document("doc_12345")
```

---

## 📊 Component Details

### **1. IntegratedRAGAgent (Main Orchestrator)**

**Purpose:** Unified interface for document + technical analysis

**Key Methods:**
- `ingest_document(file_path, metadata, doc_type)` - Upload documents
- `query(question, ticker, include_technical_analysis, period)` - Main query
- `chat(message, ticker, conversation_history)` - Conversational interface
- `get_document_list()` - List uploaded documents
- `get_statistics()` - System statistics
- `delete_document(doc_id)` - Remove document

**Example:**
```python
agent = IntegratedRAGAgent()

# Upload document
agent.ingest_document("earnings_call.pdf", {"ticker": "AAPL", "quarter": "Q4 2024"})

# Query
result = agent.query(
    "What did management say about AI investments?",
    ticker="AAPL"
)

# Result structure
{
    "question": "What did management say...",
    "timestamp": "2026-01-10T...",
    "document_insights": {
        "answer": "Management highlighted...",
        "sources": [...],
        "retrieved_count": 5
    },
    "technical_analysis": {
        "AAPL": {
            "analysis": "Technical indicators show...",
            "current_price": 182.30,
            "rsi": 58.5,
            "signal": "BUY"
        }
    },
    "integrated_answer": "## Summary\n...",
    "query_classification": {...}
}
```

---

### **2. QueryProcessor**

**Purpose:** Handle query classification and data fetching

**Responsibilities:**
- Extract tickers from questions
- Classify query types
- Fetch technical data
- Calculate indicators
- Query document database

**Key Methods:**
- `classify_query(question)` - Classify and extract info
- `extract_tickers(question, provided_ticker)` - Get ticker symbols
- `fetch_technical_data(ticker, period)` - Fetch OHLCV + indicators
- `get_document_insights(question)` - Query RAG engine
- `analyze_technical_indicators(df)` - Extract indicator values

**Example:**
```python
from src.ai_agent.integration import QueryProcessor
from src.ai_agent.rag import RAGEngine

rag = RAGEngine()
processor = QueryProcessor(rag)

# Extract tickers
tickers = processor.extract_tickers(
    "Compare AAPL and GOOGL technical setups",
    provided_ticker="MSFT"
)
# Returns: ['AAPL', 'GOOGL', 'MSFT']

# Fetch technical data
df = processor.fetch_technical_data('AAPL', period='3mo')

# Analyze indicators
indicators = processor.analyze_technical_indicators(df)
# Returns: {'current_price': 182.30, 'rsi': 58.5, 'signal': 'BUY', ...}
```

---

### **3. SynthesisEngine**

**Purpose:** Combine document insights with technical analysis

**Responsibilities:**
- Format technical data for context
- Format source citations
- Generate LLM-based synthesis
- Create structured summaries

**Key Methods:**
- `generate_integrated_answer(...)` - Main synthesis
- `create_summary(...)` - Structured summary
- `_format_technical_context(...)` - Format tech data
- `_format_source_context(...)` - Format sources

**Example:**
```python
from src.ai_agent.integration import SynthesisEngine
from src.ai_agent.rag import RAGEngine

rag = RAGEngine()
synthesis = SynthesisEngine(rag)

# Generate integrated answer
integrated_answer = synthesis.generate_integrated_answer(
    question="What are AAPL's growth prospects?",
    rag_answer="Documents show 15% revenue growth...",
    technical_data={
        'AAPL': {
            'current_price': 182.30,
            'rsi': 58.5,
            'signal': 'BUY',
            'analysis': 'Technicals show strong momentum...'
        }
    },
    sources=[...]
)

# Result: Formatted markdown with sections:
# - Summary
# - Key Insights
# - Technical Outlook
# - Recommendation
# - Risk Factors
```

**Output Format:**
```markdown
## Summary
AAPL shows strong growth prospects with 15% revenue growth documented in recent filings.
Technical indicators support a bullish outlook.

## Key Insights
- Revenue growth accelerating in AI and services
- Strong technical momentum with RSI at 58.5
- Price above all major moving averages

## Technical Outlook
Current price: $182.30
Signal: BUY
Uptrend intact with bullish momentum

## Recommendation
Consider buying on pullbacks to $175 support.
Target: $195 resistance

## Risk Factors
- Market volatility increasing
- Watch $175 support level
```

---

### **4. ChatHandler**

**Purpose:** Manage conversational interactions with memory

**Responsibilities:**
- Maintain conversation history
- Build context from previous messages
- Generate conversation summaries
- Export conversations

**Key Methods:**
- `process_message(message, response, conversation_history)` - Update history
- `build_context_from_history(conversation_history)` - Context string
- `get_conversation_summary(conversation_history)` - Statistics
- `export_conversation(conversation_history, format)` - Export chat

**Example:**
```python
from src.ai_agent.integration import ChatHandler

handler = ChatHandler(max_history=10)

# Process message
history = []
response = {"integrated_answer": "AAPL shows bullish signals..."}

updated_response = handler.process_message(
    message="Analyze AAPL",
    response=response,
    conversation_history=history
)

history = updated_response['conversation_history']
# [
#   {"role": "user", "content": "Analyze AAPL", "timestamp": "..."},
#   {"role": "assistant", "content": "AAPL shows...", "timestamp": "..."}
# ]

# Get summary
summary = handler.get_conversation_summary(history)
# {
#   "total_messages": 2,
#   "user_messages": 1,
#   "assistant_messages": 1,
#   "topics": ['AAPL', 'analysis'],
#   "start_time": "...",
#   "last_time": "..."
# }

# Export
text_export = handler.export_conversation(history, format='text')
```

---

## 🔄 Data Flow

```
User Question
     ↓
IntegratedRAGAgent.query()
     ↓
┌────┴─────────────────┐
↓                      ↓
QueryProcessor    QueryProcessor
.get_document     .fetch_technical
_insights()       _data()
     ↓                 ↓
RAG Engine       Technical
Documents        Indicators
     ↓                 ↓
└────┬─────────────────┘
     ↓
SynthesisEngine
.generate_integrated_answer()
     ↓
LLM Synthesis
     ↓
Integrated Answer
```

**Chat Flow:**
```
User Message → IntegratedRAGAgent.chat()
                      ↓
                query() method
                      ↓
                ChatHandler
                      ↓
            Update conversation history
                      ↓
            Return with history
```

---

## 💡 Use Cases

### **1. Document + Market Analysis:**
```python
# Upload earnings call transcript
agent.ingest_document("earnings_q4.pdf", {"ticker": "AAPL", "quarter": "Q4"})

# Query combining both sources
result = agent.query(
    "What did management say about margins and how does the stock look technically?",
    ticker="AAPL"
)
```

### **2. Multi-Source Research:**
```python
# Upload multiple documents
agent.ingest_document("10k_2024.pdf", {"ticker": "AAPL", "doc_type": "10-K"})
agent.ingest_document("analyst_report.pdf", {"ticker": "AAPL", "doc_type": "research"})

# Query across all documents + technical
result = agent.query("What's the consensus on AAPL's growth?", ticker="AAPL")
```

### **3. Conversational Analysis:**
```python
history = None

# Initial question
r1 = agent.chat("Tell me about TSLA's deliveries", ticker="TSLA", conversation_history=history)
history = r1['conversation_history']

# Follow-up with context
r2 = agent.chat("How does that compare to estimates?", conversation_history=history)
history = r2['conversation_history']

# Another follow-up
r3 = agent.chat("What do technicals show?", ticker="TSLA", conversation_history=history)
```

### **4. Document Management:**
```python
# List and filter documents
docs = agent.get_document_list()
aapl_docs = [d for d in docs if d['metadata'].get('ticker') == 'AAPL']

# Get system stats
stats = agent.get_statistics()
print(f"Capacity used: {stats['total_chunks']} chunks")
```

---

## 🧪 Testing

### **Unit Testing:**

```python
import pytest
from src.ai_agent.integration import QueryProcessor, SynthesisEngine

def test_ticker_extraction():
    processor = QueryProcessor(mock_rag_engine)
    tickers = processor.extract_tickers("Compare AAPL and GOOGL")
    assert 'AAPL' in tickers
    assert 'GOOGL' in tickers

def test_synthesis():
    engine = SynthesisEngine(mock_rag_engine)
    answer = engine.generate_integrated_answer(
        question="Test",
        rag_answer="Doc insights...",
        technical_data={'AAPL': {...}},
        sources=[...]
    )
    assert '## Summary' in answer
    assert '## Key Insights' in answer
```

### **Integration Testing:**

```python
def test_full_integration():
    agent = IntegratedRAGAgent()
    
    # Ingest document
    result = agent.ingest_document("test.pdf", {"ticker": "TEST"})
    assert result['status'] == 'success'
    
    # Query
    response = agent.query("Test question", ticker="TEST")
    assert 'integrated_answer' in response
    assert 'document_insights' in response
```

---

## 📚 Integration Points

### **With RAG Engine:**
```python
# Uses rag_engine for:
- Document ingestion
- Vector search
- Document querying
- LLM access
```

### **With LLM Analyzers:**
```python
# Uses market_analyzer for:
- Technical analysis generation
- Indicator explanations
```

### **With Autonomous Agents:**
```python
# Can integrate autonomous_agent for:
- Tool-based actions
- LangGraph workflows
```

---

## ⚙️ Configuration

### **Initialization Options:**

```python
agent = IntegratedRAGAgent(
    rag_storage_path="./custom/path"  # Custom storage location
)

# Configure chat handler
agent.chat_handler = ChatHandler(max_history=20)  # Longer history
```

### **Query Options:**

```python
result = agent.query(
    question="...",
    ticker="AAPL",               # Explicit ticker
    include_technical_analysis=True,  # Include technical
    period="6mo"                 # Data period
)
```

---

## 🎯 Benefits of Modular Structure

| Aspect | Before | After |
|--------|--------|-------|
| **Organization** | 1 file (269 lines) | 4 modules (~640 lines) |
| **Separation** | Mixed concerns | Clear responsibilities |
| **Testing** | Test entire system | Test individual components |
| **Extensibility** | Modify 269-line file | Add new module |
| **Reusability** | Tightly coupled | Independent modules |
| **Maintainability** | All in one place | Focused modules |

---

## 📊 API Summary

### **IntegratedRAGAgent**
```python
ingest_document(file_path, metadata, doc_type) -> Dict
query(question, ticker, include_technical_analysis, period) -> Dict
chat(message, ticker, conversation_history) -> Dict
get_document_list() -> List[Dict]
get_statistics() -> Dict
delete_document(doc_id) -> Dict
get_conversation_summary(conversation_history) -> Dict
clear_conversation() -> Dict
```

### **QueryProcessor**
```python
classify_query(question) -> Dict
extract_tickers(question, provided_ticker) -> List[str]
fetch_technical_data(ticker, period) -> pd.DataFrame
get_document_insights(question) -> Dict
analyze_technical_indicators(df) -> Dict
```

### **SynthesisEngine**
```python
generate_integrated_answer(question, rag_answer, technical_data, sources) -> str
create_summary(question, integrated_answer, technical_data, sources) -> Dict
```

### **ChatHandler**
```python
process_message(message, response, conversation_history) -> Dict
build_context_from_history(conversation_history, max_messages) -> str
get_conversation_summary(conversation_history) -> Dict
export_conversation(conversation_history, format) -> Any
```

---

**Created:** January 2026  
**Status:** ✅ Production Ready  
**Maintainer:** Technical Analyst Agent Team
