'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { searchApi, apiUtils } from '@/lib/api'
import { QdrantSearchResponse, SearchFilters } from '@/types'
import { Loader2, Search, FileText, Calendar, Scale, Clock } from 'lucide-react'
import { formatDuration, truncateText } from '@/lib/utils'

export default function VectorSearchForm() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(10)
  const [filters, setFilters] = useState<SearchFilters>({
    court: '',
    date_from: '',
    date_to: '',
    statute_tags: [],
  })
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<QdrantSearchResponse | null>(null)
  const [error, setError] = useState<string>('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError('')
    setResults(null)

    try {
      const searchFilters: SearchFilters = {
        ...filters,
        statute_tags: filters.statute_tags?.length ? filters.statute_tags : undefined,
      }

      // Remove empty filters
      Object.keys(searchFilters).forEach(key => {
        const value = searchFilters[key as keyof SearchFilters]
        if (!value || (Array.isArray(value) && value.length === 0)) {
          delete searchFilters[key as keyof SearchFilters]
        }
      })

      const response = await searchApi.search({
        query_text: query.trim(),
        top_k: topK,
        filters: searchFilters,
      })

      setResults(response)
    } catch (err) {
      setError(apiUtils.formatError(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleStatuteTagsChange = (value: string) => {
    const tags = value.split(',').map(tag => tag.trim()).filter(Boolean)
    setFilters({ ...filters, statute_tags: tags })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Vector Search</CardTitle>
          <CardDescription>
            Search legal documents using semantic similarity in Qdrant vector database
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label htmlFor="searchQuery" className="block text-sm font-medium mb-2">
                Search Query
              </label>
              <Textarea
                id="searchQuery"
                placeholder="Enter your legal research query (e.g., 'privacy rights under Article 21')"
                rows={3}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label htmlFor="topK" className="block text-sm font-medium mb-2">
                  Results Limit
                </label>
                <Input
                  id="topK"
                  type="number"
                  min="1"
                  max="50"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value) || 10)}
                />
              </div>

              <div>
                <label htmlFor="court" className="block text-sm font-medium mb-2">
                  Court
                </label>
                <Input
                  id="court"
                  type="text"
                  placeholder="e.g., SC, HC, etc."
                  value={filters.court || ''}
                  onChange={(e) => setFilters({ ...filters, court: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="dateFrom" className="block text-sm font-medium mb-2">
                  Date From
                </label>
                <Input
                  id="dateFrom"
                  type="date"
                  value={filters.date_from || ''}
                  onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                />
              </div>

              <div>
                <label htmlFor="dateTo" className="block text-sm font-medium mb-2">
                  Date To
                </label>
                <Input
                  id="dateTo"
                  type="date"
                  value={filters.date_to || ''}
                  onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label htmlFor="statuteTags" className="block text-sm font-medium mb-2">
                Statute Tags
              </label>
              <Input
                id="statuteTags"
                type="text"
                placeholder="Enter comma-separated statute tags"
                value={filters.statute_tags?.join(', ') || ''}
                onChange={(e) => handleStatuteTagsChange(e.target.value)}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Separate multiple tags with commas (e.g., Article 21, Section 377)
              </p>
            </div>

            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Search Vectors
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-800">
              <Search className="h-5 w-5" />
              <span className="font-medium">Search Error</span>
            </div>
            <p className="mt-2 text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {results && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Search Results</span>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <span className="flex items-center">
                  <FileText className="h-4 w-4 mr-1" />
                  {results.total_found} results
                </span>
                <span className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  {formatDuration(results.search_time_ms)}
                </span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {results.results.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Search className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>No results found for your query</p>
                <p className="text-sm mt-2">Try adjusting your search terms or filters</p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.results.map((result, index) => (
                  <div key={result.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="secondary">Score: {result.score.toFixed(3)}</Badge>
                          {result.payload.court && (
                            <Badge variant="outline">{result.payload.court}</Badge>
                          )}
                          {result.payload.date && (
                            <Badge variant="outline" className="flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              {new Date(result.payload.date).getFullYear()}
                            </Badge>
                          )}
                        </div>
                        
                        {result.payload.title && (
                          <h4 className="font-medium text-lg mb-2">
                            {result.payload.title}
                          </h4>
                        )}
                        
                        {result.payload.text && (
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {truncateText(result.payload.text, 300)}
                          </p>
                        )}
                      </div>
                    </div>

                    {result.payload.statute_tags && result.payload.statute_tags.length > 0 && (
                      <div className="flex items-center space-x-2">
                        <Scale className="h-4 w-4 text-gray-500" />
                        <div className="flex flex-wrap gap-1">
                          {result.payload.statute_tags.map((tag, tagIndex) => (
                            <Badge key={tagIndex} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="text-xs text-gray-500 border-t pt-2">
                      ID: {result.id}
                      {result.payload.authority_id && ` • Authority: ${result.payload.authority_id}`}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
