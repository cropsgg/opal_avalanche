# OPAL Server Frontend

Modern React/Next.js frontend for OPAL Server blockchain and vector database operations.

## Overview

This frontend provides a comprehensive interface for:

- **Blockchain Operations**: Subnet notarization, verification, and audit data management
- **Vector Search**: Semantic search through legal documents using Qdrant
- **System Monitoring**: Real-time status dashboards and health checks

## Features

### 🔗 **Blockchain Interface**
- **Notarization Form**: Submit evidence for cryptographic notarization
- **Verification Lookup**: Check notarization status by run ID
- **Transaction Tracking**: View blockchain transaction details
- **Contract Status**: Monitor smart contract connectivity

### 🔍 **Search Interface**
- **Semantic Search**: Natural language queries for legal documents
- **Advanced Filters**: Court, date, and statute-based filtering
- **Result Visualization**: Scored results with metadata display
- **Search Analytics**: Performance metrics and timing

### 📊 **Monitoring Dashboard**
- **System Health**: Real-time component status monitoring
- **Performance Metrics**: Database and blockchain connectivity
- **Error Tracking**: Issue identification and troubleshooting
- **Auto-refresh**: Continuous status updates

## Quick Start

### Prerequisites
- Node.js 18+
- Server backend running on port 8001
- Qdrant vector database
- Private Avalanche subnet (optional)

### Installation

```bash
cd Server/frontend
npm install
```

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The frontend will start on `http://localhost:3001`

### Configuration

Create `.env.local` file:

```env
SERVER_API_URL=http://localhost:8001
```

## Architecture

### Technology Stack
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + Radix UI components
- **Icons**: Lucide React
- **HTTP Client**: Axios with interceptors
- **State Management**: React hooks + local state
- **TypeScript**: Full type safety

### Component Structure

```
components/
├── ui/                 # Base UI components (buttons, cards, etc.)
├── blockchain/         # Blockchain operation components
├── search/            # Vector search components
├── dashboard/         # Status monitoring components
└── Navigation.tsx     # Main navigation
```

### API Integration

The frontend connects to the Server backend through:

- **Blockchain API**: `/api/v1/subnet/*` endpoints
- **Search API**: `/api/v1/search` endpoint
- **Health API**: `/health/*` endpoints

All API calls include:
- Request/response logging
- Error handling with user-friendly messages
- Loading states and feedback
- Connection testing utilities

## Usage Guide

### Blockchain Operations

1. **Notarize Data**:
   - Navigate to Blockchain page
   - Enter run ID and evidence text
   - Choose whether to include audit commit
   - Submit for notarization

2. **Verify Notarization**:
   - Use the lookup form with run ID
   - View Merkle root and verification status
   - Copy transaction hashes

### Vector Search

1. **Search Documents**:
   - Enter natural language query
   - Apply filters (court, date, statutes)
   - Review scored results
   - Explore document metadata

2. **Optimize Searches**:
   - Use specific legal terminology
   - Include relevant article numbers
   - Adjust result limits as needed

### System Monitoring

1. **Check Status**:
   - Visit Status page for overview
   - Monitor component health
   - Review performance metrics

2. **Troubleshoot Issues**:
   - Check connection indicators
   - Review error messages
   - Use refresh buttons for updates

## Development

### Component Development

Components follow these patterns:

```tsx
'use client'  // For interactive components

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'

export default function MyComponent() {
  const [loading, setLoading] = useState(false)
  
  const handleAction = async () => {
    setLoading(true)
    try {
      await api.someEndpoint()
    } catch (error) {
      // Handle error
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardContent>
        <Button onClick={handleAction} disabled={loading}>
          {loading ? 'Loading...' : 'Action'}
        </Button>
      </CardContent>
    </Card>
  )
}
```

### Styling Guidelines

- Use Tailwind CSS utility classes
- Leverage Radix UI for complex components
- Follow consistent spacing and color schemes
- Ensure responsive design for mobile devices

### Type Safety

All API responses and component props are fully typed:

```tsx
interface BlockchainStatusProps {
  refreshInterval?: number
}

const BlockchainStatus: React.FC<BlockchainStatusProps> = ({
  refreshInterval = 30000
}) => {
  // Implementation
}
```

## Deployment

### Production Build

```bash
npm run build
npm start
```

### Environment Variables

Required for production:

```env
SERVER_API_URL=https://your-server-domain.com
NEXT_PUBLIC_APP_NAME="OPAL Server"
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

## Contributing

1. Follow the existing component patterns
2. Add proper TypeScript types
3. Include error handling and loading states
4. Test with the Server backend
5. Ensure responsive design

## License

[Your License Here]
