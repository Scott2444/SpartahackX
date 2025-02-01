import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export default function Home() {
  const [jsonData, setJsonData] = useState('{"terms": [{"term": "France", "definition": "Paris"}]}');
  const [status, setStatus] = useState("");

  const handleSubmit = async () => {
    try {
      const response = await fetch("https://your-backend-url.com/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonData,
      });
      if (response.ok) {
        setStatus("Data successfully uploaded!");
      } else {
        setStatus("Error uploading data.");
      }
    } catch (error) {
      setStatus("Failed to connect to server.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Card className="w-full max-w-lg">
        <CardContent>
          <h2 className="text-xl font-bold mb-4">Upload Custom Quiz Data</h2>
          <Textarea
            value={jsonData}
            onChange={(e) => setJsonData(e.target.value)}
            className="w-full h-40"
          />
          <Button onClick={handleSubmit} className="mt-4">Submit</Button>
          {status && <p className="mt-2 text-sm">{status}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
