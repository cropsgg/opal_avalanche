"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { apiClient } from "@/lib/api";

export default function ApiTestPage() {
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [matterId, setMatterId] = useState("");
  const [testMessage, setTestMessage] = useState("What are the key considerations for contract formation?");

  const runTest = async (testName: string, testFn: () => Promise<any>) => {
    setLoading(prev => ({ ...prev, [testName]: true }));
    try {
      const result = await testFn();
      setResults(prev => ({ ...prev, [testName]: result }));
    } catch (error) {
      setResults(prev => ({ ...prev, [testName]: { error: error instanceof Error ? error.message : "Unknown error" } }));
    } finally {
      setLoading(prev => ({ ...prev, [testName]: false }));
    }
  };

  const tests = [
    {
      name: "Health Check",
      fn: () => apiClient.health()
    },
    {
      name: "Get Case Types",
      fn: () => apiClient.getCaseTypes()
    },
    {
      name: "Get Jurisdictions", 
      fn: () => apiClient.getJurisdictions()
    },
    {
      name: "Create Matter",
      fn: async () => {
        const result = await apiClient.createMatter({ title: `Test Matter ${Date.now()}` });
        if (result.data) {
          const id = 'matter_id' in result.data ? result.data.matter_id : result.data.id;
          setMatterId(id); // Auto-populate matter ID for chat test
        }
        return result;
      }
    },
    {
      name: "Test Arbiter",
      fn: () => apiClient.testArbiter("contract")
    },
    {
      name: "Send Chat Message",
      fn: () => {
        if (!matterId) {
          throw new Error("Please create a matter first and enter the Matter ID");
        }
        return apiClient.sendChatMessage({
          matter_id: matterId,
          message: testMessage,
          case_type: "Contract Law",
          jurisdiction_region: "California"
        });
      }
    }
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">FastAPI Backend Integration Test</h1>
        <Button 
          onClick={() => window.location.href = "/chat"}
          className="bg-blue-600 hover:bg-blue-700"
        >
          Go to Chat
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Test Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Matter ID (for chat test):</label>
            <Input
              value={matterId}
              onChange={(e) => setMatterId(e.target.value)}
              placeholder="Enter matter ID from Create Matter test result"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Test Message:</label>
            <Textarea
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Enter a test legal question"
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tests.map((test) => (
          <Card key={test.name}>
            <CardHeader>
              <CardTitle className="text-lg">{test.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => runTest(test.name, test.fn)}
                disabled={loading[test.name]}
                className="w-full mb-4"
              >
                {loading[test.name] ? "Running..." : "Run Test"}
              </Button>
              
              {results[test.name] && (
                <div className="mt-4">
                  <h4 className="font-semibold text-sm mb-2">Result:</h4>
                  <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto max-h-64">
                    {JSON.stringify(results[test.name], null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Backend URL</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="font-mono text-sm">
                         {process.env.NEXT_PUBLIC_API_URL || "https://648cd54b91d1.ngrok-free.app"}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Make sure your backend is running and accessible at this URL
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
