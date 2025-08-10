# Search Feature Documentation

## Overview

The search feature allows users to search through legal documents including cases, statutes, documents, and precedents. It provides a comprehensive search interface with filtering capabilities and detailed result display.

## Files Structure

```
frontend/
├── app/search/
│   └── page.tsx                 # Main search page component
├── components/search/
│   ├── SearchFilters.tsx        # Advanced search filters component
│   └── SearchResultCard.tsx     # Individual search result card component
└── lib/
    ├── api.ts                   # API client with search method
    └── mock-search-data.ts      # Mock data for testing
```

## Features

### 1. Basic Search
- Text-based search with instant results
- Search term highlighting
- Real-time search as you type
- URL parameters for shareable search results

### 2. Advanced Filters
- **Document Type**: Filter by case, statute, document, or precedent
- **Date Range**: Filter results by date range (from/to dates)
- **Results Limit**: Control number of results per page (10, 20, 50, 100)
- **Active Filter Display**: Visual badges showing applied filters
- **Filter Persistence**: Filters are preserved in URL parameters

### 3. Search Results Display
- **Grid Layout**: Responsive grid showing search results
- **Result Cards**: Rich result cards with:
  - Document type icons and color coding
  - Title and description
  - Date information
  - Relevance score
  - Source attribution
  - Text excerpts
  - External links where available
- **Loading States**: Skeleton loading during search
- **Empty States**: User-friendly no results messaging

### 4. User Experience
- **Keyboard Navigation**: Full keyboard support
- **Responsive Design**: Works on all device sizes
- **Error Handling**: User-friendly error messages
- **Toast Notifications**: Feedback for user actions
- **Search Performance**: Display search timing information

## API Integration

### Search Endpoint
```typescript
GET /v1/search?q={query}&type={type}&date_from={date}&date_to={date}&limit={limit}&offset={offset}
```

### Response Format
```typescript
interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  took: number; // search time in ms
}

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'case' | 'statute' | 'document' | 'precedent';
  date?: string;
  source?: string;
  relevance_score?: number;
  url?: string;
  excerpt?: string;
}
```

## Usage

### Navigation
Users can access the search page via:
- Direct URL: `/search`
- Header navigation link
- Search with query parameter: `/search?q=contract+law`

### Search Process
1. User enters search term in the main search input
2. User can optionally apply filters using the filters panel
3. User submits search (Enter key or search button)
4. Results are displayed with sorting and filtering applied
5. User can click on results to view details or external links

### URL Parameters
- `q`: Search query string
- `type`: Document type filter
- `date_from`: Start date filter (YYYY-MM-DD)
- `date_to`: End date filter (YYYY-MM-DD)
- `limit`: Number of results per page

## Component Props

### SearchFilters Component
```typescript
interface SearchFiltersProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onApplyFilters: () => void;
}
```

### SearchResultCard Component
```typescript
interface SearchResultCardProps {
  result: SearchResult;
  onClick?: () => void;
}
```

## Styling

The search interface uses the application's design system with:
- Brown/cream color scheme matching the OPAL brand
- Consistent spacing and typography
- Hover states and transitions
- Responsive breakpoints
- Accessible color contrasts

## Testing

For testing the UI before backend implementation, use the mock data:

```typescript
import { mockSearchResults } from '@/lib/mock-search-data';

// In your test or development environment
// Replace the API call with mock data
```

## Future Enhancements

1. **Search History**: Save and display recent searches
2. **Saved Searches**: Allow users to bookmark frequent searches
3. **Advanced Boolean Search**: Support AND, OR, NOT operators
4. **Faceted Search**: Category-based filtering sidebar
5. **Search Suggestions**: Auto-complete and search suggestions
6. **Export Results**: Export search results to PDF/CSV
7. **Pagination**: Load more results with pagination
8. **Search Analytics**: Track search patterns and popular queries

## Accessibility

- Keyboard navigation support
- Screen reader compatibility
- ARIA labels and roles
- Focus management
- High contrast mode support
- Semantic HTML structure

## Performance Considerations

- Debounced search to prevent excessive API calls
- Efficient re-rendering with proper React keys
- Lazy loading for large result sets
- Optimized images and icons
- Minimized bundle size
