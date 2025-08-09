# 🏛️ OPAL - GenAI Co-Counsel for Indian Lawyers

OPAL is an advanced GenAI-powered legal co-counsel specifically designed for Indian lawyers. It combines sophisticated AI reasoning with blockchain notarization to provide trustworthy legal research and analysis.

![OPAL Architecture](./docs/architecture.png)

## ✨ Features

### 🤖 Multi-Agent AI System
- **7 Specialized Legal Agents**: Statute, Precedent, Limitation, Risk, Devil's Advocate, Ethics, and Drafting agents
- **Confidence-Weighted Voting**: Using Multiplicative Weights Update (MWU) algorithm
- **Continuous Learning**: Agents improve over time based on alignment with successful outcomes

### 🔍 Advanced Legal Research
- **Hybrid Search**: Combines semantic (Qdrant) and keyword (PostgreSQL FTS) retrieval
- **Indian Jurisdiction Focus**: Supreme Court + All High Courts coverage
- **Multilingual Support**: English and Hindi document processing with OCR
- **Citation Analysis**: Automatic extraction and verification of legal citations

### 🔐 Blockchain Notarization
- **Avalanche Integration**: Immutable proof of research integrity on Avalanche Fuji
- **Merkle Tree Verification**: Cryptographic proof of cited document authenticity
- **Audit Trail**: Complete transparency of AI reasoning and sources

### 🛡️ Security & Compliance
- **DPDP 2023 Compliant**: Full Indian data protection compliance
- **End-to-End Encryption**: AES-256 encryption for sensitive data
- **PII Detection**: Automatic redaction with audit trails
- **Row Level Security**: Multi-tenant data isolation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │     Qdrant      │    │    Supabase     │
         │              │   (Vectors)     │    │   (Storage)     │
         │              └─────────────────┘    └─────────────────┘
         │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Clerk       │    │     OpenAI      │    │   Avalanche     │
│    (Auth)       │    │   (AI/LLM)      │    │  (Blockchain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+ and pip
- **Docker** and Docker Compose
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd opal_avalanche
```

### 2. Start Infrastructure Services

```bash
cd infra
docker-compose up -d
cd ..
```

This starts:
- PostgreSQL (port 5432)
- Qdrant Vector DB (port 6333)
- Redis (port 6379)

### 3. Quick Start Script

```bash
./start-dev.sh
```

This script will:
- Check prerequisites
- Set up Python virtual environment
- Install dependencies
- Create basic configuration files
- Start both frontend and backend servers

### 4. Manual Setup (Alternative)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your Clerk keys

# Start the development server
npm run dev
```

## 🔧 Configuration

### Required API Keys

1. **Clerk Authentication**
   - Sign up at [clerk.com](https://clerk.com)
   - Create a new application
   - Copy your publishable and secret keys

2. **OpenAI API**
   - Get your API key from [platform.openai.com](https://platform.openai.com)
   - Recommended models: GPT-4, text-embedding-3-large

3. **Supabase Storage**
   - Create project at [supabase.com](https://supabase.com)
   - Set up storage bucket for documents
   - Copy your project URL and service key

4. **Avalanche Wallet** (Optional)
   - For blockchain notarization
   - Use Fuji testnet for development

### Environment Variables

#### Backend (.env)
```bash
DATABASE_URL=postgresql://opal:opal123@localhost:5432/opal_db
ASYNC_DATABASE_URL=postgresql+asyncpg://opal:opal123@localhost:5432/opal_db
OPENAI_API_KEY=your_openai_api_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
QDRANT_URL=http://localhost:6333
AVALANCHE_RPC=https://api.avax-test.network/ext/bc/C/rpc
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
```

## 📖 Usage

### 1. Create a Matter

1. Navigate to the dashboard
2. Click "Create New Matter"
3. Fill in matter details and language preference
4. Upload your legal documents (PDF, DOCX, images)

### 2. Research with AI

1. Open your matter workspace
2. Choose research mode:
   - **General**: General legal research
   - **Precedent**: Find relevant case law
   - **Limitation**: Check time limitations
   - **Draft**: Get drafting assistance
3. Ask your legal question
4. Review AI analysis with citations

### 3. Verify with Blockchain

1. After getting AI analysis, click "Notarize Research"
2. Connect your wallet (or use platform wallet)
3. Confirm transaction on Avalanche Fuji
4. Get immutable proof of research integrity

### 4. Export Results

1. Download analysis as PDF, DOCX, or JSON
2. Share secure links with colleagues
3. Export audit trail for compliance

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Testing
```bash
# Start all services
./start-dev.sh

# In another terminal
cd frontend
npm run test:e2e
```

## 🚀 Deployment

### Production Environment

1. **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
2. **Vector DB**: Use Qdrant Cloud or self-hosted cluster
3. **Storage**: Use Supabase or AWS S3
4. **Hosting**: Vercel (frontend) + Railway/Render (backend)
5. **Monitoring**: Set up logging and metrics

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints

- `POST /v1/matters` - Create new matter
- `POST /v1/chat` - Send research query
- `POST /v1/runs/{id}/notarize` - Notarize research
- `GET /v1/analytics` - Get usage analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow TypeScript/Python type hints
- Add comprehensive tests
- Update documentation
- Follow security best practices

## 🛡️ Security

### Responsible Disclosure

If you discover security vulnerabilities, please email security@opal.law instead of using public issue tracker.

### Security Features

- **Authentication**: Clerk-based auth with JWT tokens
- **Authorization**: Role-based access control
- **Data Protection**: End-to-end encryption
- **Audit Logging**: Complete activity tracking
- **Rate Limiting**: API abuse prevention

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Indian Legal System**: Supreme Court and High Court judgments
- **OpenAI**: GPT and embedding models
- **Avalanche**: Blockchain infrastructure
- **Open Source Community**: Various libraries and tools

## 📞 Support

- **Documentation**: [docs.opal.law](https://docs.opal.law)
- **Community**: [Discord](https://discord.gg/opal)
- **Email**: support@opal.law
- **Issues**: [GitHub Issues](https://github.com/your-org/opal/issues)

---

**Built with ❤️ for Indian Lawyers**

*Empowering legal professionals with AI while maintaining the highest standards of accuracy, security, and compliance.*
