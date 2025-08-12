"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
<<<<<<< HEAD
import { Search, Loader2, FileText, ExternalLink, Scale } from "lucide-react";
=======
import { Search, Loader2, FileText } from "lucide-react";
>>>>>>> 1a29fd168724437961359413bad99020075647b4
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
<<<<<<< HEAD
// import { SearchResultCard } from "@/components/search/SearchResultCard"; // using custom card below
import { SearchFiltersComponent, SearchFilters } from "@/components/search/SearchFilters";
=======
import { SearchResultCard } from "@/components/search/SearchResultCard";
import { SearchFiltersComponent, SearchFilters } from "@/components/search/SearchFilters";
import apiClient from "@/lib/api";
>>>>>>> 1a29fd168724437961359413bad99020075647b4

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

<<<<<<< HEAD
// Dummy, sexy search results
const DUMMY_RESULTS: SearchResult[] = [
  {
    id: 'res_001',
    type: 'case',
    title: 'SLP(C) No. 12658/2025 — Fraud Tolling on Discovery',
    description: 'Supreme Court reiterates that limitation is tolled until discovery where fraud concealed title defects.',
    date: '2025-05-18',
    source: 'Supreme Court of India',
    relevance_score: 0.93,
    url: '#',
    excerpt: '...limitation period shall not commence until the fraud is discovered by the plaintiff...'
  },
  {
    id: 'res_002',
    type: 'case',
    title: 'CIVIL APPEAL No. 1796/2024 — Acknowledgement Resets Limitation',
    description: 'Court explains written acknowledgement can reset limitation; fresh computation applies from date of acknowledgment.',
    date: '2024-11-03',
    source: 'Supreme Court of India',
    relevance_score: 0.88,
    url: '#',
    excerpt: '...acknowledgement in writing signed by the party to be charged resets the period of limitation...'
  },
  {
    id: 'res_003',
    type: 'case',
    title: 'CIVIL APPEAL No. 6843/2025 — Strict Application of Limitation',
    description: 'Courts apply limitation strictly absent statutory basis for extension; equitable pleas alone insufficient.',
    date: '2025-03-09',
    source: 'Supreme Court of India',
    relevance_score: 0.82,
    url: '#',
    excerpt: '...the law of limitation must be applied strictly as prescribed by the legislature...'
  },
  {
    id: 'res_004',
    type: 'case',
    title: 'CIVIL APPEAL No. 4718/2025 — Discoverability is Mixed Question',
    description: 'Limitation often turns on facts; whether earlier discovery was reasonably possible may be tried.',
    date: '2025-04-02',
    source: 'Supreme Court of India',
    relevance_score: 0.79,
    url: '#',
    excerpt: '...mixed question of law and fact; examine possibility of earlier discovery...'
  },
  {
    id: 'res_005',
    type: 'statute',
    title: 'Limitation Act, 1963 — Section 17(1)(b)',
    description: 'Fraud concealment — limitation begins on discovery.',
    date: '1963-10-05',
    source: 'Statute',
    relevance_score: 0.95,
    url: '#',
    excerpt: '...period of limitation shall not begin to run until the plaintiff has discovered the fraud...'
  },
  {
    id: 'res_006',
    type: 'statute',
    title: 'Limitation Act, 1963 — Section 3',
    description: 'General rule — suits instituted after prescribed period shall be dismissed.',
    date: '1963-10-05',
    source: 'Statute',
    relevance_score: 0.74,
    url: '#',
    excerpt: '...a suit instituted after the prescribed period shall be dismissed...'
  },
  {
    id: 'res_007',
    type: 'statute',
    title: 'Limitation Act, 1963 — Section 18',
    description: 'Acknowledgement in writing resets limitation period.',
    date: '1963-10-05',
    source: 'Statute',
    relevance_score: 0.68,
    url: '#',
    excerpt: '...acknowledgement in writing...resets the period of limitation...'
  },
  {
    id: 'res_008',
    type: 'precedent',
    title: 'Delhi High Court — Title Fraud and Due Diligence (2021)',
    description: 'Guidance on reasonable discoverability and diligence in title verification.',
    date: '2021-08-12',
    source: 'Delhi High Court',
    relevance_score: 0.71,
    url: '#',
    excerpt: '...reasonable title search and absence of public notice may rebut constructive knowledge...'
  },
];

=======
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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

<<<<<<< HEAD
=======
  // Perform search on initial load if query param exists
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
      // Simulate search delay and return hardcoded results
      await new Promise((r) => setTimeout(r, 900));
      const took = 350 + Math.floor(Math.random() * 300);
      setResults(DUMMY_RESULTS);
      setTotalResults(DUMMY_RESULTS.length);
      setSearchTime(took);

      const params = new URLSearchParams();
      params.set('q', query);
      if (searchFilters.type) params.set('type', String(searchFilters.type));
      if (searchFilters.date_from) params.set('date_from', String(searchFilters.date_from));
      if (searchFilters.date_to) params.set('date_to', String(searchFilters.date_to));
      if (searchFilters.limit && searchFilters.limit !== 20) params.set('limit', String(searchFilters.limit));

      router.push(`/search?${params.toString()}`, { scroll: false });
=======
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
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
=======
    // Reset offset when doing a new search
>>>>>>> 1a29fd168724437961359413bad99020075647b4
    const searchFilters = { ...filters, offset: 0 };
    setFilters(searchFilters);
    performSearch(searchTerm, searchFilters);
  };

  const handleFiltersChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
  };

  const handleApplyFilters = () => {
    if (searchTerm.trim()) {
<<<<<<< HEAD
=======
      // Reset offset when applying new filters
>>>>>>> 1a29fd168724437961359413bad99020075647b4
      const searchFilters = { ...filters, offset: 0 };
      setFilters(searchFilters);
      performSearch(searchTerm, searchFilters);
    }
  };

  const handleResultClick = (result: SearchResult) => {
<<<<<<< HEAD
=======
    // You can implement result detail view here
    // For now, if there's a URL, open it
>>>>>>> 1a29fd168724437961359413bad99020075647b4
    if (result.url) {
      window.open(result.url, '_blank');
    }
  };

<<<<<<< HEAD
  const ResultCard = ({ result }: { result: SearchResult }) => {
    const typeStyle = {
      case: 'border-black text-black',
      statute: 'border-black text-black',
      document: 'border-black text-black',
      precedent: 'border-black text-black',
    }[result.type];

    return (
      <Card className="group hover:shadow-xl transition-all duration-200 border-black/10 bg-white">
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-[11px] uppercase tracking-wider border px-2 py-0.5 rounded-full ${typeStyle}`}>{result.type}</span>
                {result.relevance_score !== undefined && (
                  <span className="text-[11px] text-gray-600">Relevance {(result.relevance_score * 100).toFixed(0)}%</span>
                )}
              </div>
              <h3 className="text-lg font-medium text-black group-hover:translate-x-[1px] transition-transform">{result.title}</h3>
              {result.source || result.date ? (
                <div className="text-xs text-gray-600 mt-1">
                  {[result.source, result.date]?.filter(Boolean).join(' • ')}
                </div>
              ) : null}
              <p className="text-sm text-gray-800 mt-3">{result.description}</p>
              {result.excerpt && (
                <blockquote className="text-sm text-gray-700 italic border-l-2 border-gray-300 pl-3 mt-3">“{result.excerpt}”</blockquote>
              )}
            </div>
            <Button
              variant="ghost"
              className="text-black hover:bg-black/5"
              onClick={() => handleResultClick(result)}
              aria-label="Open"
            >
              <ExternalLink className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  const OpalLoader = () => (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="relative">
        <div className="h-12 w-12 rounded-full border-2 border-black animate-spin border-t-transparent" />
        <div className="absolute inset-0 flex items-center justify-center text-black text-sm font-medium">Opal</div>
      </div>
      <div className="mt-4 text-sm text-gray-700">Searching OPAL Knowledge Graph…</div>
      <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2 mt-8 w-full">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="p-4 border-black/10">
            <div className="space-y-3 animate-pulse">
              <div className="h-5 w-3/4 bg-black/10 rounded" />
              <div className="h-3 w-1/2 bg-black/10 rounded" />
              <div className="h-3 w-full bg-black/10 rounded" />
              <div className="h-3 w-2/3 bg-black/10 rounded" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#EFEAE3" }}>
=======
  return (
    <div className="min-h-screen bg-cream-100">
>>>>>>> 1a29fd168724437961359413bad99020075647b4
      <Header />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Header */}
        <div className="text-center mb-8">
<<<<<<< HEAD
          <h1 className="text-3xl font-bold text-black mb-2">OPAL Search</h1>
          <p className="text-gray-700">
=======
          <h1 className="text-3xl font-bold text-brown-900 mb-2">
            Legal Research Search
          </h1>
          <p className="text-brown-600">
>>>>>>> 1a29fd168724437961359413bad99020075647b4
            Search through cases, statutes, documents, and precedents
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative max-w-3xl mx-auto">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
<<<<<<< HEAD
              <Search className="h-5 w-5 text-gray-500" />
=======
              <Search className="h-5 w-5 text-brown-400" />
>>>>>>> 1a29fd168724437961359413bad99020075647b4
            </div>
            <Input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search for cases, statutes, precedents..."
<<<<<<< HEAD
              className="pl-10 pr-24 !rounded-full py-3 text-lg border-black/20 focus:border-black focus:ring-black bg-white text-black placeholder:text-gray-500"
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-0">
              <Button
                type="submit"
                disabled={isLoading}
                className="bg-black hover:bg-black/90 text-white rounded-full px-4"
=======
              className="pl-10 pr-20 py-3 text-lg border-brown-200 focus:border-brown-500 focus:ring-brown-500"
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="bg-brown-700 hover:bg-brown-600 text-cream-100"
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
<<<<<<< HEAD
            {!isLoading && (
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-medium text-black">
                    Search Results
                  </h2>
                  <p className="text-gray-700 text-sm">
=======
            {/* Results Header */}
            {!isLoading && (
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-brown-900">
                    Search Results
                  </h2>
                  <p className="text-brown-600 text-sm">
>>>>>>> 1a29fd168724437961359413bad99020075647b4
                    {totalResults.toLocaleString()} results found in {searchTime}ms
                  </p>
                </div>
              </div>
            )}

            {/* Loading State */}
<<<<<<< HEAD
            {isLoading && <OpalLoader />}
=======
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
>>>>>>> 1a29fd168724437961359413bad99020075647b4

            {/* Results */}
            {!isLoading && results.length > 0 && (
              <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
                {results.map((result) => (
<<<<<<< HEAD
                  <ResultCard key={result.id} result={result} />
=======
                  <SearchResultCard
                    key={result.id}
                    result={result}
                    onClick={() => handleResultClick(result)}
                  />
>>>>>>> 1a29fd168724437961359413bad99020075647b4
                ))}
              </div>
            )}

            {/* No Results */}
            {!isLoading && hasSearched && results.length === 0 && (
<<<<<<< HEAD
              <Card className="border-black/10">
                <CardContent className="text-center py-12">
                  <FileText className="h-16 w-16 text-black/30 mx-auto mb-4" />
                  <h3 className="text-xl font-medium text-black mb-2">
                    No results found
                  </h3>
                  <p className="text-gray-700 mb-4">
=======
              <Card>
                <CardContent className="text-center py-12">
                  <FileText className="h-16 w-16 text-brown-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-brown-900 mb-2">
                    No results found
                  </h3>
                  <p className="text-brown-600 mb-4">
>>>>>>> 1a29fd168724437961359413bad99020075647b4
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
