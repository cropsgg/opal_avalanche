# OPAL Avalanche Subnet – GenAI Legal Co-Counsel for India

![Avalanche Logo](https://cryptologos.cc/logos/avalanche-avax-logo.png?v=026)

---

## 🚀 Overview

**OPAL** is a next-generation GenAI-powered legal co-counsel platform, purpose-built for Indian lawyers. It combines advanced multi-agent AI reasoning, hybrid legal research, and blockchain notarization on a custom Avalanche Subnet for trust, transparency, and compliance.

---

## 🏆 Avalanche Hackathon Submission

- **Category:** LegalTech / AI / Blockchain
- **Track:** Avalanche Subnet, Smart Contracts, AI Integration

---

## 🖼️ Architecture

![OPAL Architecture](./docs/architecture.png)

*Above: End-to-end flow from user query to notarized, verifiable legal research.*

---

## 🔗 Avalanche Subnet Integration

### Why Avalanche Subnet?

- **Custom Blockchain:** OPAL runs its own Avalanche Subnet for legal research notarization.
- **Smart Contracts:** Immutable storage of research proofs, Merkle roots, and encrypted evidence.
- **Transparency:** Every AI-generated legal opinion is cryptographically anchored on-chain.
- **Compliance:** Enables auditability and regulatory compliance for legal professionals.

### Key Contracts

- **Notary.sol:** Stores Merkle roots of research runs for tamper-proof verification.
- **CommitStore.sol:** Stores encrypted blobs of legal evidence.
- **ProjectRegistry.sol:** Manages versioning and release history for legal research protocols.

---

## 🧠 Multi-Agent AI System

- **7 Specialized Legal Agents:** Statute, Precedent, Limitation, Risk, Devil’s Advocate, Ethics, Drafting.
- **Confidence-Weighted Voting:** Uses Multiplicative Weights Update (MWU) for agent learning.
- **Hybrid Search:** Combines semantic (Qdrant) and keyword (PostgreSQL) retrieval.
- **Citation Analysis:** Automatic extraction and verification of legal citations.

---

## 🛡️ Security & Compliance

- **End-to-End Encryption:** AES-256 for all sensitive data.
- **PII Detection & Redaction:** Automatic, with audit trails.
- **Row Level Security:** Multi-tenant data isolation.
- **DPDP 2023 Compliant:** Indian data protection standards.

---

## 📦 Tech Stack

- **Frontend:** Next.js (TypeScript), Clerk Auth, TailwindCSS
- **Backend:** FastAPI (Python), Celery, SQLAlchemy
- **AI:** OpenAI GPT-4o, Custom Multi-Agent System
- **Storage:** PostgreSQL, Qdrant, Supabase, Redis
- **Blockchain:** Avalanche Subnet, Solidity Smart Contracts

---

## 📝 How It Works

1. **User submits a legal query** via the web app.
2. **PII is detected and redacted** for privacy.
3. **AI agents analyze the query** using hybrid search and LLMs.
4. **Results are aggregated, verified, and cited.**
5. **Merkle root of the research** is notarized on the Avalanche Subnet.
6. **Users receive a verifiable, exportable report** (PDF/DOCX).

---

## 🌐 Live Demo

> _Add your deployed link or demo video here!_

---

## 📸 Screenshots

![Dashboard](./docs/screenshot-dashboard.png)  
![Notarization](./docs/screenshot-notarization.png)

---

## 🛠️ Local Development

\`\`\`bash
# Clone the repo
git clone https://github.com/your-org/opal-avalanche.git
cd opal-avalanche

# Start infrastructure
cd infra
docker-compose up -d
cd ..

# Start backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Start frontend
cd ../frontend
npm install
npm run dev
\`\`\`

---

## 🤝 Team & Credits

- **Indian Legal System:** Supreme Court and High Court judgments
- **OpenAI:** GPT and embedding models
- **Avalanche:** Blockchain infrastructure
- **Jazzee Technologies:** Engineering & Design

---

## 📬 Contact

- **Email:** support@opal.law
- **Discord:** [Join our community](https://discord.gg/opal)

---

**Empowering Indian lawyers with AI and blockchain – with trust, transparency, and compliance.**
