"use client";
// feature-section.tsx
import {
  Scale,
  Shield,
  Users,
  FileText,
  Clock,
  Award,
  Heart,
  Currency,
} from "lucide-react";
import Image from "next/image";
import { Baskervville, Montserrat } from "next/font/google";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-montserrat",
});
const baskervville = Baskervville({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-baskervville",
});
export default function FeaturesSection() {

  const practiceAreas = [
    {
      icon: Users,
      title: "Agentic RAG Research",
      description:
        "Hybrid semantic and keyword retrieval from comprehensive Supreme Court and High Court judgment database with agent ensemble reasoning.",
    },
    {
      icon: Scale,
      title: "Explainable AI Reasoning",
      description:
        "Second-layer verifier ensures statute, precedent, limitation, and jurisdiction consistency with structured 'Why OPAL suggests X' explanations.",
    },
    {
      icon: Currency,
      title: "Immutable Audit Trail",
      description:
        "Blockchain notarization of judgment hashes on Avalanche Fuji provides transparent, tamper-proof documentation of research sources.",
    },
  ];

  return (
    <section className="py-16 bg-[#F8F3EE]">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2
            className={`text-3xl md:text-4xl lg:text-5xl font-light text-[#2A2A2A] mb-8 tracking-wide ${baskervville.className}`}
          >
            AI-POWERED LEGAL RESEARCH & ANALYSIS PLATFORM
          </h2>
          <p
            className={`text-base md:text-lg text-[#8B7355] max-w-2xl mx-auto leading-relaxed ${montserrat.className}`}
          >
            OPAL delivers intelligent legal research with verifiable citations,
            explainable AI reasoning, and blockchain-verified integrity for Indian
            legal practitioners working with Supreme Court and High Court matters.
          </p>
        </div>

        {/* Practice Areas Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {practiceAreas.map((area, index) => {
            const IconComponent = area.icon;
            return (
              <div key={index} className="text-center group cursor-pointer">
                {/* Icon Circle */}
                <div className="w-20 h-20 bg-[#D4B59E] rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-[#C4A584] transition-colors duration-300">
                  <IconComponent className="w-8 h-8 text-white" />
                </div>

                {/* Title */}
                <h3
                  className={`text-xl font-extrabold text-[#2A2A2A] mb-4 ${baskervville.className}`}
                >
                  {area.title}
                </h3>

                {/* Description */}
                <p
                  className={`text-[#8B7355] leading-relaxed text-sm md:text-base ${montserrat.className}`}
                >
                  {area.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
