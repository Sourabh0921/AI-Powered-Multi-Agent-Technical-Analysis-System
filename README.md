# 🤖 AI-Powered Multi-Agent Technical Analysis System

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)

**An intelligent multi-agent system that combines traditional technical analysis with advanced AI capabilities to provide comprehensive stock market insights, real-time sentiment analysis, and personalized trading recommendations.**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Documentation](#-documentation)

</div>

---

## 📊 Overview

The **AI-Powered Multi-Agent Technical Analysis System** is a cutting-edge financial analysis platform that leverages artificial intelligence, multi-agent architectures, and traditional technical analysis to empower traders, investors, and financial analysts with data-driven insights.

### 🎯 Purpose

This system was built to bridge the gap between traditional technical analysis and modern AI capabilities, providing:

- **Automated Analysis**: Eliminate hours of manual chart analysis and indicator calculation
- **AI-Powered Insights**: Natural language market analysis powered by LLMs (GPT-4, Claude, Gemini)
- **Multi-Agent Intelligence**: Specialized agents for technical, sentiment, and risk analysis working in coordination
- **Real-Time Decision Support**: Instant analysis of market conditions with actionable recommendations
- **Document Intelligence**: RAG-powered analysis of financial reports, earnings statements, and research documents

---

## 🚀 Problem Statement

### The Challenges Traders Face

1. **Information Overload**: Traders are bombarded with data from multiple sources - price charts, news, social media, financial reports
2. **Time-Consuming Analysis**: Manual technical analysis of multiple stocks takes hours daily
3. **Emotional Decision Making**: Human biases and emotions lead to poor trading decisions
4. **Complex Pattern Recognition**: Identifying chart patterns and market trends requires expertise
5. **Fragmented Tools**: Using multiple platforms for charting, news, sentiment, and fundamental analysis
6. **Lack of Context**: Traditional indicators don't consider market sentiment, news, or macroeconomic factors
7. **Limited Scalability**: Impossible to analyze hundreds of stocks simultaneously with quality

### Our Solution

We've built an **intelligent, automated, and comprehensive** system that:

✅ **Automates Technical Analysis** - Calculate 20+ indicators instantly  
✅ **Provides AI Insights** - Natural language explanations of market conditions  
✅ **Aggregates Sentiment** - Real-time sentiment from news, social media, and SEC filings  
✅ **Offers Multi-Perspective Analysis** - Technical + Sentiment + Risk = Holistic view  
✅ **Enables Document Analysis** - Upload and query financial reports using RAG  
✅ **Scales Infinitely** - Analyze entire watchlists in seconds  
✅ **Removes Emotion** - Data-driven, unbiased recommendations  
✅ **Provides Context** - Combines multiple data sources for informed decisions  

---

## ✨ Features

### 🔧 Traditional Technical Analysis
- **30+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Fibonacci, Volume indicators, and more
- **Advanced Pattern Recognition**: Head & Shoulders, Double Top/Bottom, Triangles, Flags, Cup & Handle
- **Signal Generation**: Automated buy/sell/hold signals based on multi-indicator consensus
- **Multi-Timeframe Analysis**: Analyze stocks across multiple timeframes simultaneously
- **Support/Resistance Detection**: Automatic identification of key price levels
- **Trend Analysis**: Identify market trends and potential reversals

### 🤖 AI-Powered Features

#### 1. **Multi-Agent Coordinator**
- **Technical Agent**: Specialized in chart patterns and technical indicators
- **Sentiment Agent**: Analyzes market sentiment from multiple sources
- **Risk Agent**: Evaluates risk factors and position sizing
- **Recommendation Engine**: Synthesizes insights from all agents

#### 2. **LLM Market Analysis**
- Natural language explanations of market conditions
- Powered by GPT-4, Claude Sonnet, Google Gemini, or Groq
- Context-aware analysis considering market conditions
- Personalized insights based on user preferences

#### 3. **RAG Document Intelligence**
- Upload financial reports (PDF, DOCX, TXT)
- Query documents in natural language
- Extract insights from earnings reports, SEC filings, research papers
- FAISS vector store for efficient document retrieval
- Sentence transformers for semantic search

#### 4. **Real-Time Sentiment Analysis**
- **News Sentiment**: Aggregate sentiment from major financial news sources
- **Social Media**: Twitter/X, Reddit, StockTwits sentiment tracking
- **SEC Filings**: Analyze 10-K, 10-Q reports for sentiment shifts
- **Earnings Analysis**: Process earnings transcripts and guidance
- Weighted sentiment scoring with configurable weights

#### 5. **LangGraph Workflows**
- Multi-step analysis pipelines
- Conditional routing based on market conditions
- State management for complex analysis flows
- Error handling and recovery

### 🎨 Modern Web Interface
- **React + TypeScript** frontend with Material-UI
- **Real-time charts** powered by Recharts
- **Dark/Light theme** support
- **Responsive design** for mobile and desktop
- **Interactive dashboards** for portfolio tracking
- **Query history** with bookmarking
- **Document upload** interface for RAG

### 🔐 Enterprise-Grade Security
- **JWT Authentication** with refresh tokens
- **Role-based access control** (RBAC)
- **Password hashing** with Argon2
- **Secure API endpoints**
- **Rate limiting** and request validation

### 📊 Database & Data Management
- **PostgreSQL** for relational data (users, portfolios, watchlists)
- **SQLAlchemy ORM** with async support
- **Query history tracking**
- **Portfolio management**
- **Alert system** for price targets and signals

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │   React + TypeScript + Material-UI + Redux Toolkit       │  │
│  │   - Dashboard  - Charts  - RAG Query  - Auth  - Theme    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API (FastAPI)
┌────────────────────────▼────────────────────────────────────────┐
│                       Backend Layer (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints: /analysis, /sentiment, /rag, /auth       │  │
│  │  - JWT Auth  - Request Validation  - Rate Limiting       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────┬─────────────┬─────────────┬────────────────┬──────────────┘
     │             │             │                │
┌────▼─────┐  ┌───▼──────┐  ┌──▼─────────┐  ┌───▼──────────┐
│   AI     │  │  Data    │  │ Database   │  │  Sentiment   │
│  Agents  │  │ Ingestion│  │ PostgreSQL │  │  Analyzers   │
└────┬─────┘  └────┬─────┘  └────┬───────┘  └───┬──────────┘
     │             │             │               │
┌────▼─────────────▼─────────────▼───────────────▼──────────┐
│              Multi-Agent Coordinator                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Technical  │  │  Sentiment   │  │     Risk     │      │
│  │   Agent    │  │    Agent     │  │    Agent     │      │
│  └────────────┘  └──────────────┘  └──────────────┘      │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          Recommendation Engine                      │  │
│  │  Synthesizes insights & generates recommendations   │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Multi-Agent System Flow

```
User Query → Query Processor → Multi-Agent Coordinator
                                        ↓
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
            Technical Agent      Sentiment Agent      Risk Agent
                    ↓                   ↓                   ↓
            Technical Score      Sentiment Score      Risk Score
                    └───────────────────┼───────────────────┘
                                        ↓
                            Synthesis Engine
                                        ↓
                            Recommendation Engine
                                        ↓
                            Final Analysis Report
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** - Core programming language
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary relational database
- **Uvicorn** - ASGI server

### AI & Machine Learning
- **LangChain** - LLM orchestration framework
- **LangGraph** - Multi-agent workflow engine
- **OpenAI GPT-4** - Advanced language model
- **Anthropic Claude** - Alternative LLM
- **Google Gemini** - Google's LLM
- **Groq** - Ultra-fast inference
- **Sentence Transformers** - Embeddings for RAG
- **FAISS** - Vector similarity search
- **ChromaDB** - Vector database

### Data & Analysis
- **yfinance** - Yahoo Finance data fetching
- **pandas** - Data manipulation
- **NumPy** - Numerical computing
- **TA-Lib** - Technical analysis library
- **TextBlob** - Sentiment analysis
- **BeautifulSoup4** - Web scraping for news

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Material-UI (MUI)** - Component library
- **Redux Toolkit** - State management
- **Recharts** - Charting library
- **Axios** - HTTP client

### Document Processing (RAG)
- **PyPDF2** - PDF parsing
- **python-docx** - Word document processing
- **unstructured** - Document parsing
- **markdown** - Markdown processing

### Security & Auth
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **argon2-cffi** - Argon2 password hashing
- **python-multipart** - File upload handling

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Git** - Version control
- **GitHub** - Code hosting

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm
- PostgreSQL 12+ (or use SQLite for development)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Sourabh0921/AI-Powered-Multi-Agent-Technical-Analysis-System.git
cd AI-Powered-Multi-Agent-Technical-Analysis-System
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd ta_agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 3. Configure Environment Variables

Edit `ta_agent/.env`:

```env
# LLM API Keys (get from providers)
GROQ_API_KEY=gsk_your-groq-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ta_agent
# Or use SQLite for development:
# DATABASE_URL=sqlite:///./data/ta_agent.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Sentiment Analysis APIs (optional)
NEWSAPI_KEY=your-newsapi-key-here
ALPHA_VANTAGE_KEY=your-alpha-vantage-key-here
FINNHUB_KEY=your-finnhub-key-here
TWITTER_BEARER_TOKEN=your-twitter-bearer-token-here
```

### 4. Initialize Database

```bash
# Run database initialization script
python scripts/init_db.py
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd ../ta-agent-frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 6. Start Backend Server

```bash
# In ta_agent directory
cd ../ta_agent
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🎯 Usage

### Quick Start Example

```python
from src.ai_agent.integration.integrated_agent import IntegratedTAAgent

# Initialize the agent
agent = IntegratedTAAgent()

# Analyze a stock
result = agent.analyze_stock("AAPL")

print(f"Signal: {result['signal']}")
print(f"Technical Score: {result['technical_score']}")
print(f"Sentiment Score: {result['sentiment_score']}")
print(f"Risk Assessment: {result['risk_level']}")
print(f"Recommendation: {result['recommendation']}")
```

### RAG Document Query Example

```python
from src.ai_agent.rag.rag_engine import RAGEngine

# Initialize RAG engine
rag = RAGEngine()

# Upload document
rag.upload_document("earnings_report_Q4_2024.pdf")

# Query the document
answer = rag.query("What was the revenue growth in Q4 2024?")
print(answer)
```

### Multi-Agent Analysis Example

```python
from src.ai_agent.coordinator.multi_agent_coordinator import MultiAgentCoordinator

# Initialize coordinator
coordinator = MultiAgentCoordinator()

# Run comprehensive analysis
analysis = coordinator.analyze_comprehensive("TSLA")

print(f"Overall Score: {analysis['overall_score']}/100")
print(f"Technical Analysis: {analysis['technical_analysis']}")
print(f"Sentiment Analysis: {analysis['sentiment_analysis']}")
print(f"Risk Analysis: {analysis['risk_analysis']}")
print(f"Final Recommendation: {analysis['recommendation']}")
```

### API Usage Examples

#### Get Technical Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/technical" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"ticker": "AAPL", "timeframe": "1d"}'
```

#### Get Sentiment Analysis
```bash
curl -X GET "http://localhost:8000/api/v1/sentiment/AAPL" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### RAG Query
```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "What are the key risk factors mentioned in the annual report?"}'
```

---

## 📚 Project Structure

```
AI-Powered-Multi-Agent-Technical-Analysis-System/
├── ta_agent/                          # Backend application
│   ├── data/                          # Data storage
│   │   ├── databases/                 # SQLite databases
│   │   ├── cache/                     # Cache storage
│   │   ├── rag_storage/               # RAG vector stores
│   │   └── uploaded_documents/        # User uploads
│   ├── src/
│   │   ├── ai_agent/                  # AI agent system
│   │   │   ├── agents/                # Individual agents
│   │   │   ├── analyzers/             # Analysis modules
│   │   │   ├── coordinator/           # Multi-agent coordinator
│   │   │   ├── integration/           # Integration layer
│   │   │   ├── rag/                   # RAG implementation
│   │   │   ├── tools/                 # Agent tools
│   │   │   └── workflow/              # LangGraph workflows
│   │   ├── api/                       # FastAPI application
│   │   │   ├── v1/                    # API v1 endpoints
│   │   │   ├── main.py                # Main API app
│   │   │   └── auth.py                # Authentication
│   │   ├── core/                      # Core configurations
│   │   ├── db/                        # Database layer
│   │   ├── indicators/                # Technical indicators
│   │   ├── patterns/                  # Pattern recognition
│   │   ├── sentiment/                 # Sentiment analyzers
│   │   ├── services/                  # Business logic
│   │   ├── models/                    # Database models
│   │   ├── schemas/                   # Pydantic schemas
│   │   └── utils/                     # Utility functions
│   ├── scripts/                       # Utility scripts
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Docker configuration
│   └── docker-compose.yml             # Docker Compose config
│
├── ta-agent-frontend/                 # Frontend application
│   ├── public/                        # Static assets
│   ├── src/
│   │   ├── components/                # React components
│   │   │   ├── auth/                  # Authentication components
│   │   │   ├── dashboard/             # Dashboard components
│   │   │   └── common/                # Shared components
│   │   ├── services/                  # API services
│   │   ├── store/                     # Redux store
│   │   ├── theme/                     # Theme configuration
│   │   ├── types/                     # TypeScript types
│   │   ├── utils/                     # Utility functions
│   │   ├── App.tsx                    # Main App component
│   │   └── index.tsx                  # Entry point
│   ├── package.json                   # Node dependencies
│   └── tsconfig.json                  # TypeScript config
│
└── README.md                          # This file
```

---

## 🔑 Key Components

### 1. Multi-Agent Coordinator
Orchestrates multiple specialized agents to provide comprehensive analysis:
- **Technical Agent**: Chart patterns, indicators, price action
- **Sentiment Agent**: News, social media, SEC filings
- **Risk Agent**: Volatility, drawdown, position sizing
- **Recommendation Engine**: Synthesizes insights

### 2. RAG Engine
Retrieval-Augmented Generation for document intelligence:
- Document upload and processing
- Vector embedding with Sentence Transformers
- FAISS similarity search
- Context-aware answer generation

### 3. LangGraph Workflows
Multi-step analysis workflows with conditional logic:
- Data fetching → Technical analysis → Sentiment analysis → Risk assessment
- State management and error handling
- Parallel execution for efficiency

### 4. Sentiment Aggregator
Multi-source sentiment analysis:
- News APIs (NewsAPI, Alpha Vantage, Finnhub)
- Social media (Twitter/X, Reddit, StockTwits)
- SEC filings (10-K, 10-Q, 8-K)
- Earnings transcripts

---

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/auth/me` - Get current user info

### Analysis Endpoints
- `POST /api/v1/analysis/technical` - Get technical analysis
- `POST /api/v1/analysis/comprehensive` - Get full multi-agent analysis
- `GET /api/v1/sentiment/{ticker}` - Get sentiment analysis
- `POST /api/v1/analysis/compare` - Compare multiple stocks

### RAG Endpoints
- `POST /api/v1/rag/upload` - Upload document
- `POST /api/v1/rag/query` - Query documents
- `GET /api/v1/rag/documents` - List uploaded documents
- `DELETE /api/v1/rag/documents/{doc_id}` - Delete document

### Portfolio Endpoints
- `GET /api/v1/portfolio` - Get user portfolio
- `POST /api/v1/portfolio/positions` - Add position
- `PUT /api/v1/portfolio/positions/{id}` - Update position
- `DELETE /api/v1/portfolio/positions/{id}` - Remove position

### Watchlist Endpoints
- `GET /api/v1/watchlist` - Get watchlist
- `POST /api/v1/watchlist` - Add to watchlist
- `DELETE /api/v1/watchlist/{ticker}` - Remove from watchlist

Full API documentation available at: http://localhost:8000/docs

---

## 🧪 Testing

```bash
# Backend tests
cd ta_agent
pytest tests/

# Frontend tests
cd ta-agent-frontend
npm test

# Test database connection
python scripts/test_database.py
```

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **LangChain** for the amazing LLM orchestration framework
- **FastAPI** for the high-performance web framework
- **React** and **Material-UI** for the modern frontend
- **yfinance** for market data access
- All the open-source contributors who made this possible

---

## 📧 Contact

**Sourabh** - [@Sourabh0921](https://github.com/Sourabh0921)

Project Link: [https://github.com/Sourabh0921/AI-Powered-Multi-Agent-Technical-Analysis-System](https://github.com/Sourabh0921/AI-Powered-Multi-Agent-Technical-Analysis-System)

---

## 🚀 What's Next?

### Upcoming Features
- [ ] Real-time WebSocket streaming for live market data
- [ ] Advanced backtesting with walk-forward optimization
- [ ] Mobile app (React Native)
- [ ] Options analysis and Greeks calculation
- [ ] Cryptocurrency support
- [ ] Machine learning price prediction models
- [ ] Social trading and signal sharing
- [ ] Email/SMS alerts for signals
- [ ] Multi-language support
- [ ] Advanced portfolio optimization

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Sourabh](https://github.com/Sourabh0921)

</div>
