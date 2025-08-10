// Mock data for testing the search functionality
// You can use this data to test the search UI before the backend API is fully implemented

export const mockSearchResults = {
  results: [
    {
      id: "1",
      title: "State of Maharashtra v. Madhukar Narayan Mardikar",
      description: "Supreme Court case regarding constitutional validity of certain provisions under the Indian Penal Code",
      type: "case" as const,
      date: "1991-01-15",
      source: "Supreme Court of India",
      relevance_score: 0.92,
      url: "https://indiankanoon.org/doc/1234567/",
      excerpt: "The constitutional validity of Section 309 of the Indian Penal Code was challenged in this landmark case. The Court held that the right to life under Article 21 of the Constitution does not include the right to die."
    },
    {
      id: "2",
      title: "Indian Contract Act, 1872 - Section 10",
      description: "Defines what constitutes a valid contract under Indian law",
      type: "statute" as const,
      date: "1872-04-25",
      source: "Indian Contract Act",
      relevance_score: 0.87,
      excerpt: "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void."
    },
    {
      id: "3",
      title: "Precedent Analysis: Breach of Contract Remedies",
      description: "Analysis of judicial precedents regarding remedies available for breach of contract",
      type: "precedent" as const,
      date: "2023-03-10",
      source: "Legal Research Database",
      relevance_score: 0.78,
      excerpt: "Courts have consistently held that the primary remedy for breach of contract is damages, with specific performance being available only in exceptional circumstances where damages would not be adequate compensation."
    },
    {
      id: "4",
      title: "Property Transfer Agreement Template",
      description: "Standard template for property transfer agreements in India",
      type: "document" as const,
      date: "2024-01-20",
      source: "Legal Document Repository",
      relevance_score: 0.65,
      url: "https://example.com/property-transfer-template",
      excerpt: "This agreement is executed between the transferor and transferee for the transfer of immovable property situated at..."
    },
    {
      id: "5",
      title: "Vishaka v. State of Rajasthan",
      description: "Landmark case establishing guidelines for prevention of sexual harassment at workplace",
      type: "case" as const,
      date: "1997-08-13",
      source: "Supreme Court of India",
      relevance_score: 0.94,
      url: "https://indiankanoon.org/doc/1031794/",
      excerpt: "In the absence of domestic law occupying the field, to formulate effective measures to check the evil of sexual harassment of working women at all work places, the contents of international conventions and norms are significant."
    },
    {
      id: "6",
      title: "Information Technology Act, 2000 - Section 65",
      description: "Computer source code tampering - punishment and legal provisions",
      type: "statute" as const,
      date: "2000-06-09",
      source: "Information Technology Act",
      relevance_score: 0.71,
      excerpt: "Whoever knowingly or intentionally conceals, destroys or alters or intentionally or knowingly causes another to conceal, destroy or alter any computer source code used for a computer, computer programme, computer system or computer network..."
    }
  ],
  total: 6,
  query: "contract law",
  took: 245
};

export const mockEmptyResults = {
  results: [],
  total: 0,
  query: "nonexistent legal term xyz123",
  took: 12
};

// Function to simulate API delay
export const simulateApiDelay = (ms: number = 1000): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};
