"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, FileText, Upload } from "lucide-react";
import { useState } from "react";

export default function ReceiptFraudDetection() {
  const [result, setResult] = useState<{ success: boolean; isFraudulent: boolean; message: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);

    try {
      const response = await fetch("http://localhost:8000/api/detect-fraud", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      setResult({
        success: false,
        isFraudulent: false,
        message: "Error processing request. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Receipt Fraud Detection</CardTitle>
          <CardDescription>Upload a receipt for AI-based fraud detection</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="empId">Employee ID</Label>
              <Input id="empId" name="empId" placeholder="Enter your employee ID" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="receipt">Receipt File (Image or PDF)</Label>
              <div className="flex items-center space-x-2">
                <Input
                  id="receipt"
                  name="receipt"
                  type="file"
                  accept=".pdf,image/*"
                  required
                  className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
                />
                <Upload className="h-4 w-4 text-muted-foreground" />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="justification">Justification</Label>
              <Textarea
                id="justification"
                name="justification"
                placeholder="Explain the purpose of this expense"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="department">Department</Label>
              <Select name="department" required>
                <SelectTrigger>
                  <SelectValue placeholder="Select a department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sales">Sales</SelectItem>
                  <SelectItem value="marketing">Marketing</SelectItem>
                  <SelectItem value="engineering">Engineering</SelectItem>
                  <SelectItem value="hr">Human Resources</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Processing..." : "Submit for Fraud Detection"}
            </Button>
          </form>
        </CardContent>
        {result && (
          <CardFooter>
            <div className={`flex items-center space-x-2 ${result.isFraudulent ? "text-red-500" : "text-green-500"}`}>
              {result.isFraudulent ? <AlertCircle className="h-5 w-5" /> : <FileText className="h-5 w-5" />}
              <p>{result.message}</p>
            </div>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
