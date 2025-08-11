# ⚖️ OPAL – Avalanche Subnet GenAI Legal Co-Counsel for India

<div align="center">
  <img src="https://cryptologos.cc/logos/avalanche-avax-logo.png?v=026" alt="Avalanche Logo" width="200" height="200" />
  
  **Empowering Indian lawyers with AI & Blockchain – Trust, Transparency, Compliance.**

  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black.svg)](https://nextjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
  [![Avalanche](https://img.shields.io/badge/Blockchain-Avalanche-red.svg)](https://avax.network/)
  [![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
</div>

## 🎯 Overview

**OPAL** is a next-generation GenAI-powered legal co-counsel platform, purpose-built for Indian lawyers. It combines advanced multi-agent AI reasoning, hybrid legal research, and blockchain notarization on a custom Avalanche Subnet for trust, transparency, and compliance.

## ✨ Key Features

- 🤖 **Multi-Agent Legal AI** – Statute, Precedent, Limitation, Risk, Devil’s Advocate, Ethics, Drafting
- 🔍 **Hybrid Legal Search** – Combines semantic (Qdrant) & keyword (PostgreSQL) retrieval
- 📜 **Blockchain Notarization** – Immutable Merkle root & encrypted evidence storage on Avalanche Subnet
- 📑 **Citation Verification** – Automatic legal citation extraction & validation
- 🔐 **Data Privacy & Security** – AES-256 encryption, DPDP 2023 compliance
- 📊 **Auditability** – Cryptographically anchored research for transparency

## 🏗️ Architecture

```
Frontend (Next.js)  ←→  Backend (FastAPI)  ←→  Avalanche Subnet (Solidity)
     │                        │                      │
     │                   PostgreSQL + Qdrant     Avalanche Validators
     │                        │                      │
     └────────────── AI Multi-Agent Layer ────────────┘
```

## 🔗 Avalanche Subnet Integration

### Why Avalanche Subnet?

- **Custom Blockchain** – Legal research notarization & storage
- **Smart Contracts** – Immutable proofs & encrypted evidence
- **Transparency** – Every AI output anchored on-chain
- **Compliance** – Supports audit trails for Indian legal standards

### Key Contracts

- **Notary.sol** – Stores Merkle roots for tamper-proof verification  
- **CommitStore.sol** – Encrypted legal evidence blobs  
- **ProjectRegistry.sol** – Manages protocol versioning & release history  

## 🛡️ Security & Compliance

- End-to-end AES-256 encryption  
- Automatic PII detection & redaction  
- Row Level Security for multi-tenancy  
- Indian **DPDP 2023** compliance  

## 📦 Tech Stack

- **Frontend:** Next.js (TypeScript), Clerk Auth, TailwindCSS  
- **Backend:** FastAPI (Python), Celery, SQLAlchemy  
- **AI:** GPT-4o, Custom Multi-Agent System  
- **Storage:** PostgreSQL, Qdrant, Supabase, Redis  
- **Blockchain:** Avalanche Subnet, Solidity Smart Contracts  

## 📝 How It Works

1. User submits a legal query  
2. PII is detected & redacted  
3. AI agents analyze the query  
4. Results aggregated, verified & cited  
5. Merkle root notarized on Avalanche Subnet  
6. User receives a verifiable report (PDF/DOCX)  

## 🌐 Live Demo

> _Add your deployed link or demo video here_

## 📸 Screenshots

![Dashboard](./docs/screenshot-dashboard.png)  
![Notarization](./docs/screenshot-notarization.png)  

## 🛠️ Local Development

```bash
# Clone the repo
git clone https://github.com/your-org/opal-avalanche.git
cd opal-avalanche

# Start infrastructure
cd infra
docker-compose up -d
cd ..

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup
cd ../frontend
npm install
npm run dev
```

## 🤝 Team & Credits

- **Indian Legal System:** Supreme Court & High Court judgments  
- **OpenAI:** GPT & embeddings  
- **Avalanche:** Blockchain infra  
- **Jazzee Technologies:** Engineering & design  

## 📬 Contact

- **Email:** support@opal.law  
- **Discord:** [Join Community](https://discord.gg/opal)  

---

<div align="center">
  <strong>Powered by Avalanche • Built for Indian Legal Professionals</strong>
</div>
