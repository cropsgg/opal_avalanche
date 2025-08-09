import { Card, CardContent } from '@/components/ui/card';
import { Brain, Users, ShieldCheck, Zap, FileSearch, Globe } from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'RAG-Powered Research',
    description: 'Advanced retrieval-augmented generation finds relevant case law and statutes with precise citation anchoring.'
  },
  {
    icon: Users,
    title: 'DAO of Legal Agents',
    description: 'Multiple AI agents collaborate and vote on legal analysis, providing confidence-weighted recommendations.'
  },
  {
    icon: ShieldCheck,
    title: 'Blockchain Notarization',
    description: 'Every research run is cryptographically verified and published on Avalanche for immutable audit trails.'
  },
  {
    icon: Zap,
    title: 'Real-time Analysis',
    description: 'Upload documents and get instant legal insights with multilingual OCR support for English and Hindi.'
  },
  {
    icon: FileSearch,
    title: 'Smart Citations',
    description: 'AI verifies every citation and provides paragraph-level anchors with conflict detection.'
  },
  {
    icon: Globe,
    title: 'Jurisdiction Aware',
    description: 'Understands court hierarchies and jurisdiction boundaries to prevent citation errors.'
  }
];

export function FeaturesSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-display font-bold text-brown-900 mb-4">
            Why Legal Professionals Choose OPAL
          </h2>
          <p className="text-xl text-brown-500 max-w-2xl mx-auto">
            Experience the future of legal research with our comprehensive AI-powered platform
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="bg-cream-100 border-stone-200 hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="mb-4">
                    <div className="inline-flex p-3 bg-brown-700 text-cream-100 rounded-md">
                      <Icon className="h-6 w-6" />
                    </div>
                  </div>
                  <h3 className="text-xl font-display font-semibold text-brown-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-brown-500 leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}