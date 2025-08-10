import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import VectorSearchForm from '@/components/search/VectorSearchForm'
import { Search, Database, Zap, Filter } from 'lucide-react'

export default function SearchPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Vector Search
        </h1>
        <p className="text-gray-600">
          Semantic search through legal documents using Qdrant vector database and OpenAI embeddings
        </p>
      </div>

      {/* Search Interface */}
      <VectorSearchForm />

      {/* Information Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <Search className="h-5 w-5" />
              <span>Semantic Search</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>• <strong>Natural Language:</strong> Search using plain English queries</div>
            <div>• <strong>Contextual Understanding:</strong> Finds relevant content beyond keyword matching</div>
            <div>• <strong>Legal Terminology:</strong> Optimized for legal document comprehension</div>
            <div>• <strong>Similarity Scoring:</strong> Results ranked by semantic relevance</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <Filter className="h-5 w-5" />
              <span>Advanced Filtering</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>• <strong>Court Filtering:</strong> Supreme Court, High Courts, Tribunals</div>
            <div>• <strong>Date Ranges:</strong> Filter by judgment dates</div>
            <div>• <strong>Statute Tags:</strong> Search by legal provisions</div>
            <div>• <strong>Result Limits:</strong> Control number of returned results</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <Database className="h-5 w-5" />
              <span>Vector Database</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>• <strong>Qdrant Engine:</strong> High-performance vector similarity search</div>
            <div>• <strong>3072 Dimensions:</strong> OpenAI text-embedding-3-large model</div>
            <div>• <strong>COSINE Distance:</strong> Optimized for text similarity</div>
            <div>• <strong>Payload Indexing:</strong> Fast filtering on metadata</div>
          </CardContent>
        </Card>
      </div>

      {/* Search Tips */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Search Tips</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium mb-2">Effective Queries</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• Use specific legal concepts and terminology</li>
                <li>• Include relevant article numbers or sections</li>
                <li>• Describe the legal issue in context</li>
                <li>• Use complete sentences for better results</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Example Queries</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• &ldquo;Privacy rights under Article 21 of Constitution&rdquo;</li>
                <li>• &ldquo;Contract interpretation principles&rdquo;</li>
                <li>• &ldquo;Criminal procedure bail conditions&rdquo;</li>
                <li>• &ldquo;Property rights and acquisition&rdquo;</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Technical Details */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="text-blue-800">Technical Implementation</CardTitle>
          <CardDescription className="text-blue-700">
            Understanding the vector search pipeline
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-200 rounded-lg flex items-center justify-center mx-auto mb-2">
                <span className="text-blue-800 font-bold">1</span>
              </div>
              <div className="font-medium">Query Embedding</div>
              <div className="text-gray-600">OpenAI API generates 3072-dimensional vector</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-200 rounded-lg flex items-center justify-center mx-auto mb-2">
                <span className="text-blue-800 font-bold">2</span>
              </div>
              <div className="font-medium">Vector Search</div>
              <div className="text-gray-600">Qdrant finds similar vectors using COSINE distance</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-200 rounded-lg flex items-center justify-center mx-auto mb-2">
                <span className="text-blue-800 font-bold">3</span>
              </div>
              <div className="font-medium">Filter Application</div>
              <div className="text-gray-600">Metadata filters applied for refinement</div>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-200 rounded-lg flex items-center justify-center mx-auto mb-2">
                <span className="text-blue-800 font-bold">4</span>
              </div>
              <div className="font-medium">Result Ranking</div>
              <div className="text-gray-600">Results sorted by similarity score</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
