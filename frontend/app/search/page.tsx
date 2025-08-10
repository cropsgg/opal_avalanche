"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Search, Loader2, FileText } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { SearchResultCard } from "@/components/search/SearchResultCard";
import { SearchFiltersComponent, SearchFilters } from "@/components/search/SearchFilters";
import apiClient from "@/lib/api";

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

interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  took: number; // search time in ms
}

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  const [searchTerm, setSearchTerm] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const [searchTime, setSearchTime] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    limit: 20,
    offset: 0,
  });

  // Perform search on initial load if query param exists
  useEffect(() => {
    const initialQuery = searchParams.get('q');
    if (initialQuery) {
      setSearchTerm(initialQuery);
      performSearch(initialQuery, filters);
    }
  }, [searchParams]);

  const performSearch = async (query: string, searchFilters: SearchFilters = filters) => {
    if (!query.trim()) {
      toast({
        title: "Search term required",
        description: "Please enter a search term",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setHasSearched(true);

    try {
      const response = await apiClient.search(query, searchFilters);

      if (response.error) {
        toast({
          title: "Search failed",
          description: response.error,
          variant: "destructive",
        });
        return;
      }

      if (response.data) {
        setResults(response.data.results);
        setTotalResults(response.data.total);
        setSearchTime(response.data.took);

        // Update URL with search query and filters
        const params = new URLSearchParams();
        params.set('q', query);
        if (searchFilters.type) params.set('type', searchFilters.type);
        if (searchFilters.date_from) params.set('date_from', searchFilters.date_from);
        if (searchFilters.date_to) params.set('date_to', searchFilters.date_to);
        if (searchFilters.limit && searchFilters.limit !== 20) params.set('limit', searchFilters.limit.toString());

        router.push(`/search?${params.toString()}`, { scroll: false });
      }
    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Search failed",
        description: "An unexpected error occurred while searching",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Reset offset when doing a new search
    const searchFilters = { ...filters, offset: 0 };
    setFilters(searchFilters);
    performSearch(searchTerm, searchFilters);
  };

  const handleFiltersChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
  };

  const handleApplyFilters = () => {
    if (searchTerm.trim()) {
      // Reset offset when applying new filters
      const searchFilters = { ...filters, offset: 0 };
      setFilters(searchFilters);
      performSearch(searchTerm, searchFilters);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    // You can implement result detail view here
    // For now, if there's a URL, open it
    if (result.url) {
      window.open(result.url, '_blank');
    }
  };

  return (
    <div className="min-h-screen bg-cream-100">
      <Header />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-brown-900 mb-2">
            Legal Research Search
          </h1>
          <p className="text-brown-600">
            Search through cases, statutes, documents, and precedents
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative max-w-3xl mx-auto">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-brown-400" />
            </div>
            <Input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search for cases, statutes, precedents..."
              className="pl-10 pr-20 py-3 text-lg border-brown-200 focus:border-brown-500 focus:ring-brown-500"
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="bg-brown-700 hover:bg-brown-600 text-cream-100"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </form>

        {/* Search Filters */}
        {hasSearched && (
          <div className="max-w-3xl mx-auto">
            <SearchFiltersComponent
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onApplyFilters={handleApplyFilters}
            />
          </div>
        )}

        {/* Search Results */}
        {hasSearched && (
          <div>
            {/* Results Header */}
            {!isLoading && (
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-brown-900">
                    Search Results
                  </h2>
                  <p className="text-brown-600 text-sm">
                    {totalResults.toLocaleString()} results found in {searchTime}ms
                  </p>
                </div>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="p-4">
                    <div className="space-y-3">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-1/2" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-2/3" />
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Results */}
            {!isLoading && results.length > 0 && (
              <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                {results.map((result) => (
                  <SearchResultCard
                    key={result.id}
                    result={result}
                    onClick={() => handleResultClick(result)}
                  />
                ))}
              </div>
            )}

            {/* No Results */}
            {!isLoading && hasSearched && results.length === 0 && (
              <Card>
                <CardContent className="text-center py-12">
                  <FileText className="h-16 w-16 text-brown-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-brown-900 mb-2">
                    No results found
                  </h3>
                  <p className="text-brown-600 mb-4">
                    Try adjusting your search terms or filters, or search for something else
                  </p>
                  <div className="flex gap-2 justify-center">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setFilters({ limit: 20, offset: 0 });
                      }}
                    >
                      Clear Filters
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setSearchTerm('');
                        setResults([]);
                        setHasSearched(false);
                        setFilters({ limit: 20, offset: 0 });
                      }}
                    >
                      Clear Search
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
