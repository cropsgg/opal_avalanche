import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { 
  Blocks, 
  Search, 
  Activity, 
  Zap, 
  Shield, 
  Database,
  ArrowRight,
  CheckCircle,
  Sparkles,
  Lock,
  Network,
  Brain,
  Cpu,
  Globe
} from 'lucide-react'

export default function HomePage() {
  const features = [
    {
      icon: Blocks,
      title: 'Subnet Notarization',
      description: 'Publish Merkle roots to private Avalanche subnet with cryptographic verification',
      href: '/blockchain',
      gradient: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-50',
    },
    {
      icon: Search,
      title: 'Vector Search',
      description: 'Semantic search through legal documents using Qdrant vector database',
      href: '/search',
      gradient: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-50',
    },
    {
      icon: Database,
      title: 'Knowledge Graph',
      description: 'Visualize and explore the live knowledge database with interactive graph',
      href: '/knowledge-graph',
      gradient: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50',
    },
    {
      icon: Activity,
      title: 'System Monitoring',
      description: 'Real-time status monitoring for blockchain and database connections',
      href: '/status',
      gradient: 'from-orange-500 to-red-500',
      bgColor: 'bg-orange-50',
    },
  ]

  const capabilities = [
    'AES-GCM encrypted audit data storage',
    'Merkle tree evidence integrity proofs', 
    'Smart contract interactions (Notary, CommitStore)',
    'Legal document semantic search',
    'Multi-court filtering and date ranges',
    'Real-time health monitoring',
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          {/* Main Hero Content */}
          <div className="text-center mb-16 relative z-10">
            <div className="flex items-center justify-center mb-6">
              <div className="relative">
                <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-brown-700 to-gold-500 rounded-2xl shadow-elegant animate-glow">
                  <Zap className="h-10 w-10 text-cream-100" />
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                  <div className="w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-display font-bold text-brown-900 tracking-tight mb-6 animate-fadeIn">
              OPAL Server
              <span className="block text-3xl md:text-4xl text-gold-500 font-light mt-2">
                Blockchain & Vector Operations
              </span>
            </h1>

            <p className="text-xl text-brown-500 mb-8 max-w-4xl mx-auto leading-relaxed animate-fadeIn" style={{animationDelay: '0.2s'}}>
              Advanced blockchain notarization and vector database operations for legal document 
              integrity, cryptographic storage, and AI-powered semantic discovery.
            </p>

            <div className="flex flex-wrap justify-center gap-4 mb-12 animate-fadeIn" style={{animationDelay: '0.4s'}}>
              <Badge className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 text-base font-medium flex items-center shadow-soft">
                <CheckCircle className="h-4 w-4 mr-2" />
                  Production Ready
                </Badge>
              <Badge variant="outline" className="border-brown-300 text-brown-700 px-4 py-2 text-base font-medium">
                v1.0.0
              </Badge>
              <Badge className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 text-base font-medium flex items-center">
                <Globe className="h-4 w-4 mr-2" />
                Chain ID: 43210
              </Badge>
            </div>

            {/* Technology Stack Visual */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto mb-16 animate-fadeIn" style={{animationDelay: '0.6s'}}>
              <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-brown-200 shadow-soft card-hover">
                <Database className="h-10 w-10 mx-auto mb-3 text-blue-600" />
                <div className="text-lg font-bold text-brown-900">Qdrant</div>
                <div className="text-sm text-brown-600">Vector Database</div>
              </div>
              <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-brown-200 shadow-soft card-hover">
                <Shield className="h-10 w-10 mx-auto mb-3 text-red-600" />
                <div className="text-lg font-bold text-brown-900">Avalanche</div>
                <div className="text-sm text-brown-600">Private Subnet</div>
                </div>
              <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-brown-200 shadow-soft card-hover">
                <Brain className="h-10 w-10 mx-auto mb-3 text-purple-600" />
                <div className="text-lg font-bold text-brown-900">OpenAI</div>
                <div className="text-sm text-brown-600">AI Embeddings</div>
                </div>
              <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-brown-200 shadow-soft card-hover">
                <Cpu className="h-10 w-10 mx-auto mb-3 text-green-600" />
                <div className="text-lg font-bold text-brown-900">FastAPI</div>
                <div className="text-sm text-brown-600">Backend API</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-64 h-64 bg-gradient-to-r from-gold-500/20 to-brown-500/20 rounded-full filter blur-3xl animate-float"></div>
          <div className="absolute bottom-20 right-10 w-80 h-80 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-full filter blur-3xl animate-float" style={{animationDelay: '3s'}}></div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">

      {/* Features Grid */}
        <section className="py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-brown-900 mb-4">
              Core Capabilities
            </h2>
            <p className="text-xl text-brown-600 max-w-3xl mx-auto">
              Comprehensive blockchain and AI-powered document operations built for enterprise security and performance.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8 mb-16">
            {features.map((feature, index) => (
              <Card key={feature.title} className={`${feature.bgColor} border-0 shadow-elegant card-hover group relative overflow-hidden animate-fadeIn`} style={{animationDelay: `${0.1 * index}s`}}>
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
                <CardHeader className="relative z-10">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className={`flex items-center justify-center w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-xl shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <feature.icon className="h-7 w-7 text-white" />
                </div>
                    <CardTitle className="text-xl font-display text-brown-900 group-hover:text-brown-700 transition-colors">
                      {feature.title}
                    </CardTitle>
              </div>
                  <CardDescription className="text-brown-600 leading-relaxed text-base">
                    {feature.description}
                  </CardDescription>
            </CardHeader>
                <CardContent className="relative z-10">
              <Link href={feature.href}>
                    <Button 
                      variant="outline" 
                      className="w-full group bg-white/80 backdrop-blur-sm border-brown-300 text-brown-700 hover:bg-brown-700 hover:text-white hover:border-brown-700 transition-all duration-300 font-medium"
                    >
                      Explore Feature
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
        </section>

      {/* Capabilities Section */}
        <section className="py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="bg-white/80 backdrop-blur-sm border-brown-200 shadow-elegant">
          <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl font-display text-brown-900">
                  <div className="p-2 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
              <span>Security & Blockchain</span>
            </CardTitle>
                <CardDescription className="text-brown-600">
                  Enterprise-grade cryptographic security and immutable storage
                </CardDescription>
          </CardHeader>
              <CardContent className="space-y-4">
            {capabilities.slice(0, 3).map((capability, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-green-50 border border-green-200">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-brown-700 font-medium">{capability}</span>
              </div>
            ))}
          </CardContent>
        </Card>

            <Card className="bg-white/80 backdrop-blur-sm border-brown-200 shadow-elegant">
          <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl font-display text-brown-900">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                    <Database className="h-6 w-6 text-white" />
                  </div>
              <span>Search & Monitoring</span>
            </CardTitle>
                <CardDescription className="text-brown-600">
                  AI-powered semantic search and real-time system monitoring
                </CardDescription>
          </CardHeader>
              <CardContent className="space-y-4">
            {capabilities.slice(3).map((capability, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-blue-50 border border-blue-200">
                    <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <span className="text-brown-700 font-medium">{capability}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
        </section>

      {/* Quick Actions */}
        <section className="py-16">
          <Card className="bg-gradient-to-r from-brown-700 to-gold-500 border-0 shadow-elegant text-white overflow-hidden relative">
            <div className="absolute inset-0 bg-black/10"></div>
            <CardHeader className="relative z-10">
              <CardTitle className="text-3xl font-display text-white flex items-center space-x-3">
                <Sparkles className="h-8 w-8" />
                <span>Quick Actions</span>
              </CardTitle>
              <CardDescription className="text-cream-100 text-lg">
                Essential operations and management tasks at your fingertips
          </CardDescription>
        </CardHeader>
            <CardContent className="relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link href="/blockchain">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white hover:text-brown-700 transition-all duration-300 h-14 text-base font-medium"
                  >
                    <Blocks className="mr-3 h-5 w-5" />
                    Notarize Documents
              </Button>
            </Link>
            
            <Link href="/search">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white hover:text-brown-700 transition-all duration-300 h-14 text-base font-medium"
                  >
                    <Search className="mr-3 h-5 w-5" />
                Search Vectors
              </Button>
            </Link>
            
                <Link href="/knowledge-graph">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white hover:text-brown-700 transition-all duration-300 h-14 text-base font-medium"
                  >
                    <Network className="mr-3 h-5 w-5" />
                    Knowledge Graph
              </Button>
            </Link>
            
                <Link href="/status">
              <Button 
                variant="outline" 
                    className="w-full justify-start bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white hover:text-brown-700 transition-all duration-300 h-14 text-base font-medium"
              >
                    <Activity className="mr-3 h-5 w-5" />
                    System Status
              </Button>
            </Link>
          </div>
              
              <div className="mt-8 pt-6 border-t border-white/20">
                <div className="flex flex-col sm:flex-row gap-4">
                  <Link href="/docs" target="_blank" className="flex-1">
                    <Button 
                      variant="secondary"
                      className="w-full bg-white text-brown-700 hover:bg-cream-100 font-medium h-12 text-base"
                    >
                      <ArrowRight className="mr-2 h-5 w-5" />
                      API Documentation
                    </Button>
                  </Link>
                  <div className="flex-1 flex items-center justify-center space-x-4 text-cream-100">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-sm font-medium">System Online</span>
                    </div>
                    <div className="text-sm opacity-80">
                      Port 8001 • Ready
                    </div>
                  </div>
                </div>
              </div>
        </CardContent>
      </Card>
        </section>

      {/* API Information */}
        <section className="py-16">
          <Card className="bg-white/60 backdrop-blur-sm border-brown-200 shadow-elegant">
        <CardHeader>
              <CardTitle className="text-3xl font-display text-brown-900 flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-lg">
                  <Cpu className="h-6 w-6 text-white" />
                </div>
                <span>API Reference</span>
              </CardTitle>
              <CardDescription className="text-brown-600 text-lg">
                Comprehensive server endpoints for blockchain operations and vector search
          </CardDescription>
        </CardHeader>
        <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="space-y-4">
                  <h4 className="font-display font-semibold text-lg text-brown-900 flex items-center space-x-2">
                    <Lock className="h-5 w-5 text-brown-700" />
                    <span>Blockchain Operations</span>
                  </h4>
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <code className="text-blue-700 font-mono text-sm">POST /api/v1/subnet/notarize</code>
                      <p className="text-xs text-blue-600 mt-1">Document notarization</p>
                    </div>
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <code className="text-blue-700 font-mono text-sm">GET /api/v1/subnet/notary/{'{run_id}'}</code>
                      <p className="text-xs text-blue-600 mt-1">Verification lookup</p>
                    </div>
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <code className="text-blue-700 font-mono text-sm">GET /api/v1/status</code>
                      <p className="text-xs text-blue-600 mt-1">Network status</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-display font-semibold text-lg text-brown-900 flex items-center space-x-2">
                    <Search className="h-5 w-5 text-brown-700" />
                    <span>Vector Operations</span>
                  </h4>
                  <div className="space-y-3">
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <code className="text-purple-700 font-mono text-sm">POST /api/v1/search</code>
                      <p className="text-xs text-purple-600 mt-1">Semantic search</p>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <code className="text-purple-700 font-mono text-sm">GET /api/v1/knowledge-graph/</code>
                      <p className="text-xs text-purple-600 mt-1">Graph visualization</p>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <code className="text-purple-700 font-mono text-sm">POST /api/v1/documents/hash</code>
                      <p className="text-xs text-purple-600 mt-1">Document hashing</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-display font-semibold text-lg text-brown-900 flex items-center space-x-2">
                    <Activity className="h-5 w-5 text-brown-700" />
                    <span>System Health</span>
                  </h4>
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <code className="text-green-700 font-mono text-sm">GET /health</code>
                      <p className="text-xs text-green-600 mt-1">Basic health check</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <code className="text-green-700 font-mono text-sm">GET /health/detailed</code>
                      <p className="text-xs text-green-600 mt-1">Detailed diagnostics</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <code className="text-green-700 font-mono text-sm">GET /metrics</code>
                      <p className="text-xs text-green-600 mt-1">Performance metrics</p>
                    </div>
                  </div>
                </div>
            </div>
              
              <div className="mt-8 pt-6 border-t border-brown-200">
                <div className="text-center">
                  <p className="text-brown-600 mb-4">Explore comprehensive API documentation with interactive examples</p>
                  <Link href="/docs" target="_blank">
                    <Button className="bg-brown-700 hover:bg-brown-600 text-white px-8 py-3 text-base font-medium">
                      <ArrowRight className="mr-2 h-5 w-5" />
                      Open API Documentation
                    </Button>
                  </Link>
            </div>
          </div>
        </CardContent>
      </Card>
        </section>
      </div>
    </div>
  )
}
