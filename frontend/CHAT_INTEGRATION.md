# OPAL Chat Integration

This document describes the chat page implementation and its integration with the FastAPI backend.

## Overview

The chat page provides a conversational interface for legal analysis using the OPAL DAO Arbiter system. It features:

- **DAO Verdict Display**: First responses show collective agent analysis with explainability
- **Follow-up Chat**: Subsequent messages use conversational follow-up for natural dialogue
- **Citations Panel**: Real-time legal references and supporting documents
- **Matter Management**: Automatic matter creation for conversation tracking

## Architecture

### Frontend Components

- **`/app/chat/page.tsx`**: Main chat page with state management
- **`/components/chat/ChatHeader.tsx`**: Header with Opal logo and user profile
- **`/components/chat/ChatInput.tsx`**: Input form with case type and jurisdiction selection
- **`/components/chat/ChatMessages.tsx`**: Message display with special DAO verdict formatting
- **`/components/chat/CitationsPanel.tsx`**: Citations sidebar with relevance scoring

### API Integration

- **`/lib/api-client.ts`**: Type-safe API client for backend communication
- **`/lib/config.ts`**: Configuration management for API endpoints

## Backend Integration

### Endpoints Used

1. **POST `/chat`** - Initial DAO analysis
   - Creates new analysis run
   - Returns DAO verdict with agent breakdown
   - Includes citations and explainability

2. **POST `/chat-followup`** - Follow-up questions
   - Continues conversation within existing run
   - Maintains context from previous analysis

3. **POST `/matters`** - Matter creation
   - Auto-creates matter for conversation tracking
   - Links all messages to specific legal matter

4. **GET `/case-types`** - Dynamic case type options
5. **GET `/jurisdictions`** - Dynamic jurisdiction options

### Data Flow

```
User Input → Chat Page → API Client → FastAPI Backend
                ↓              ↓
         Message State ← Response Processing ← Backend Response
                ↓
    UI Components (Messages, Citations)
```

## Configuration

### Environment Variables

Set in `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Configuration

Located in `/lib/config.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  ENDPOINTS: {
    CHAT: '/chat',
    CHAT_FOLLOWUP: '/chat-followup',
    MATTERS: '/matters',
    // ... other endpoints
  }
}
```

## Message Types

### User Messages
- Display case type and jurisdiction
- Right-aligned layout
- Input validation

### DAO Verdict (First Response)
- Seven agent avatars
- "Final DAO Verdict" heading
- Explainability section
- Citations integration

### Follow-up Messages
- Standard assistant responses
- Left-aligned layout
- Conversational format

## Features

### Real-time Options Loading
- Case types and jurisdictions loaded from backend
- Fallback to static options if backend unavailable
- Loading states and error handling

### Matter Management
- Automatic matter creation per chat session
- Conversation history tracking
- Export capabilities (via backend API)

### Error Handling
- Network error recovery
- User-friendly error messages
- Fallback content when APIs unavailable

## Usage

1. Navigate to `/chat` from dashboard
2. Select case type and jurisdiction
3. Enter legal question
4. Review DAO verdict and citations
5. Continue with follow-up questions

## Development

### Adding New Message Types
1. Update `Message` interface in `/app/chat/page.tsx`
2. Add display logic in `ChatMessages.tsx`
3. Handle in `handleSendMessage` function

### Extending API Integration
1. Add endpoint to `/lib/config.ts`
2. Create method in `/lib/api-client.ts`
3. Add TypeScript interfaces for request/response

### Styling Customization
- Uses Tailwind CSS with white/black color scheme
- Components are styled for professional legal interface
- Responsive design for desktop and tablet use
