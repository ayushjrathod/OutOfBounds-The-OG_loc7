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
  const [result, setResult] = useState<{ status: string; expense_id?: string; message?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const fileInput = formData.get("receipt") as File;

    // Validate file type and size
    if (fileInput && fileInput.size > 10 * 1024 * 1024) {
      setResult({
        status: "error",
        message: "File size must be less than 10MB",
      });
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/expenses/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to submit expense");
      }
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      setResult({
        status: "error",
        message: error instanceof Error ? error.message : "Failed to submit expense",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Expense Submission</CardTitle>
          <CardDescription>Submit your expense receipt for processing</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="employeeId">Employee ID</Label>
              <Input id="employeeId" name="employeeId" placeholder="Enter your employee ID" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="departmentId">Department</Label>
              <Select name="departmentId" required>
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
            <div className="space-y-2">
              <Label htmlFor="expenseType">Expense Type</Label>
              <Select name="expenseType" required>
                <SelectTrigger>
                  <SelectValue placeholder="Select expense type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="travel">Travel</SelectItem>
                  <SelectItem value="meals">Meals</SelectItem>
                  <SelectItem value="supplies">Supplies</SelectItem>
                  <SelectItem value="equipment">Equipment</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="vendor">Vendor</Label>
              <Input id="vendor" name="vendor" placeholder="Enter vendor name" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" name="description" placeholder="Explain the expense details" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="receipt">Receipt File</Label>
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
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Processing..." : "Submit Expense"}
            </Button>
          </form>
        </CardContent>
        {result && (
          <CardFooter>
            <div
              className={`flex items-center space-x-2 ${result.status === "success" ? "text-green-500" : "text-red-500"}`}
            >
              {result.status === "success" ? <FileText className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
              <p>
                {result.status === "success"
                  ? `Expense submitted successfully (ID: ${result.expense_id})`
                  : result.message || "Error submitting expense"}
              </p>
            </div>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
