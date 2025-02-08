"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, FileText, Upload } from "lucide-react";
import { useState } from "react";

const cloudUrl = process.env.NEXT_PUBLIC_CLOUDINARY_URL || "";
const uploadPreset = process.env.NEXT_PUBLIC_CLOUD_UPLOAD_PRESET;

// Add this validation early in the component
if (!uploadPreset) {
  console.error("Upload preset is not configured!");
}

export default function ReceiptFraudDetection() {
  const [result, setResult] = useState<{ status: string; expense_id?: string; message?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);
    const formData = new FormData(e.currentTarget);
    const fileInput = formData.get("receipt") as File;

    if (!fileInput) {
      console.error("Debug: No file selected");
      setResult({ status: "error", message: "No file selected." });
      setIsLoading(false);
      return;
    }

    // Debug file details
    console.log("Debug: File details:", {
      name: fileInput.name,
      type: fileInput.type,
      size: `${(fileInput.size / 1024).toFixed(2)} KB`,
    });

    // 1) Upload to Cloudinary
    const cloudForm = new FormData();
    cloudForm.append("file", fileInput);
    cloudForm.append("upload_preset", uploadPreset || "ml_default"); // Ensure preset is set

    console.log("Debug: Cloudinary request details:", {
      url: cloudUrl,
      uploadPreset: uploadPreset,
      fileType: fileInput.type,
      formData: Object.fromEntries(cloudForm.entries()), // Log form data
    });

    try {
      if (!uploadPreset) {
        throw new Error("Cloudinary upload preset is not configured");
      }
      console.log("Debug: Initiating Cloudinary upload...");
      const cloudRes = await fetch(cloudUrl, {
        method: "POST",
        body: cloudForm,
      });

      const cloudData = await cloudRes.json();
      console.log("Debug: Cloudinary response:", {
        status: cloudRes.status,
        statusText: cloudRes.statusText,
        data: cloudData,
      });

      if (!cloudRes.ok) {
        throw new Error(`Cloudinary upload failed: ${cloudData.error?.message || "Unknown error"}`);
      }

      const imageUrl = cloudData.secure_url;
      if (!imageUrl) throw new Error("No secure URL in Cloudinary response");

      console.log("Debug: Successfully uploaded to Cloudinary:", imageUrl);

      // 2) Delete file from form and add image URL
      formData.delete("receipt");
      formData.append("receiptImage", imageUrl);

      // 3) Send the updated form data
      console.log("Debug: Sending expense data to backend...");
      const response = await fetch("http://localhost:8000/api/expenses/", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log("Debug: Backend response:", data);

      if (!response.ok) throw new Error(data.detail || "Failed to submit expense");
      setResult(data);
    } catch (error) {
      console.error("Debug: Error details:", error);
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
                  <SelectItem value="DEP001">Sales</SelectItem>
                  <SelectItem value="DEP002">Finance</SelectItem>
                  <SelectItem value="DEP003">Human Resources</SelectItem>
                  <SelectItem value="DEP004">Research</SelectItem>
                  <SelectItem value="DEP005">Information Technology</SelectItem>
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
              <Label htmlFor="categories">Expense Category</Label>
              <Select name="categories" required>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Travel Expenses">Travel Expenses</SelectItem>
                  <SelectItem value="Work Equipment & Supplies">Work Equipment & Supplies</SelectItem>
                  <SelectItem value="Meals & Entertainment">Meals & Entertainment</SelectItem>
                  <SelectItem value="Internet & Phone Bills">Internet & Phone Bills</SelectItem>
                  <SelectItem value="Professional Development">Professional Development</SelectItem>
                  <SelectItem value="Health & Wellness">Health & Wellness</SelectItem>
                  <SelectItem value="Commuting Expenses">Commuting Expenses</SelectItem>
                  <SelectItem value="Software & Subscriptions">Software & Subscriptions</SelectItem>
                  <SelectItem value="Relocation Assistance">Relocation Assistance</SelectItem>
                  <SelectItem value="Client & Marketing Expenses">Client & Marketing Expenses</SelectItem>
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
