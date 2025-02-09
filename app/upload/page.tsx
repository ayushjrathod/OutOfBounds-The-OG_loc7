"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { motion } from "framer-motion";
import { AlertCircle, FileText, Upload } from "lucide-react";
import { useState } from "react";

const cloudUrl = process.env.NEXT_PUBLIC_CLOUDINARY_URL || "";
const uploadPreset = process.env.NEXT_PUBLIC_CLOUD_UPLOAD_PRESET;

if (!uploadPreset) {
  console.error("Upload preset is not configured!");
}

export default function ReceiptFraudDetection() {
  const [result, setResult] = useState<{ status: string; expense_id?: string; message?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

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

    console.log("Debug: File details:", {
      name: fileInput.name,
      type: fileInput.type,
      size: `${(fileInput.size / 1024).toFixed(2)} KB`,
    });

    // 1) Upload to Cloudinary
    const cloudForm = new FormData();
    cloudForm.append("file", fileInput);
    cloudForm.append("upload_preset", uploadPreset || "ml_default");

    console.log("Debug: Cloudinary request details:", {
      url: cloudUrl,
      uploadPreset,
      fileType: fileInput.type,
      formData: Object.fromEntries(cloudForm.entries()),
    });

    try {
      console.log("Debug: Initiating Cloudinary upload...");
      const cloudRes = await fetch(cloudUrl, {
        method: "POST",
        body: cloudForm,
      });
      const cloudData = await cloudRes.json();
      console.log("Debug: Cloudinary response:", { status: cloudRes.status, data: cloudData });

      if (!cloudRes.ok) {
        throw new Error(`Cloudinary upload failed: ${cloudData.error?.message || "Unknown error"}`);
      }
      const imageUrl = cloudData.secure_url;
      if (!imageUrl) throw new Error("No secure URL in Cloudinary response");

      // 2) Delete file from form and add image URL
      formData.delete("receipt");
      formData.append("receiptImage", imageUrl);

      console.log("Debug: Sending expense data to backend...");
      const response = await fetch("http://localhost:8000/api/expenses/", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log("Debug: Backend response:", data);

      if (!response.ok) {
        throw new Error(data.detail || "Failed to submit expense");
      }
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
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-indigo-200 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-3xl"
      >
        <Card className="shadow-2xl">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-extrabold text-gray-900">Expense Submission</CardTitle>
            <CardDescription className="mt-2 text-lg text-gray-600">
              Submit your expense receipt for processing and fraud detection
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="employeeId" className="text-sm font-medium text-gray-700">
                    Employee ID
                  </Label>
                  <Input
                    id="employeeId"
                    name="employeeId"
                    placeholder="Enter your employee ID"
                    required
                    className="w-full"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="departmentId" className="text-sm font-medium text-gray-700">
                    Department
                  </Label>
                  <Select name="departmentId" required>
                    <SelectTrigger className="w-full">
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
              </div>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="expenseType" className="text-sm font-medium text-gray-700">
                    Expense Type
                  </Label>
                  <Select name="expenseType" required>
                    <SelectTrigger className="w-full">
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
                  <Label htmlFor="categories" className="text-sm font-medium text-gray-700">
                    Expense Category
                  </Label>
                  <Select name="categories" required>
                    <SelectTrigger className="w-full">
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
              </div>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="vendor" className="text-sm font-medium text-gray-700">
                    Vendor
                  </Label>
                  <Input id="vendor" name="vendor" placeholder="Enter vendor name" className="w-full" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description" className="text-sm font-medium text-gray-700">
                  Description
                </Label>
                <Textarea
                  id="description"
                  name="description"
                  placeholder="Explain the expense details"
                  required
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="receipt" className="text-sm font-medium text-gray-700">
                  Receipt File
                </Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="receipt"
                    name="receipt"
                    type="file"
                    accept=".pdf,image/*"
                    required
                    className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
                    onChange={(e) => setFileName(e.target.files?.[0]?.name || null)}
                  />
                  <Upload className="h-5 w-5 text-gray-400" />
                </div>
                {fileName && <p className="mt-2 text-sm text-gray-500">Selected file: {fileName}</p>}
              </div>
              <Button
                type="submit"
                className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500 focus:ring-offset-indigo-200 text-white transition ease-in duration-200 text-center text-base font-semibold shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 rounded-lg"
                disabled={isLoading}
              >
                {isLoading ? "Processing..." : "Submit Expense"}
              </Button>
            </form>
          </CardContent>
          {result && (
            <CardFooter>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex items-center space-x-2 w-full justify-center p-4 rounded-lg ${
                  result.status === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                }`}
              >
                {result.status === "success" ? <FileText className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
                <p className="text-sm font-medium">
                  {result.status === "success"
                    ? `Expense submitted successfully (ID: ${result.expense_id})`
                    : result.message || "Error submitting expense"}
                </p>
              </motion.div>
            </CardFooter>
          )}
        </Card>
      </motion.div>
    </div>
  );
}
