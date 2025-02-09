import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  const uri =
    process.env.MONGODB_URI_neha ||
    "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("expensesDB");

    if (id) {
      const result = await db
        .collection("EmployeeExpenses")
        .aggregate([
          { $unwind: "$expenses" },
          { $match: { "expenses.expenseId": id } },
          { $project: { expense: "$expenses", _id: 0 } },
        ])
        .toArray();
      if (result[0]) {
        return NextResponse.json(result[0].expense);
      } else {
        return NextResponse.json({ error: "Expense not found" }, { status: 404 });
      }
    }

    // If no id query provided, return all collections or an error.
    const collections = await db.collection("EmployeeExpenses").find().toArray();
    return NextResponse.json(collections);
  } finally {
    await client.close();
  }
}

export async function PUT(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");
  const data = await request.json();

  const uri =
    process.env.MONGODB_URI_neha ||
    "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("expensesDB");

    const result = await db.collection("EmployeeExpenses").updateOne(
      { "expenses.expenseId": id },
      {
        $set: {
          "expenses.$.status": data.status,
          "expenses.$.approvedBy": "manager123", // You might want to make this dynamic
          "expenses.$.approvalDate": new Date().toISOString(),
          "expenses.$.updatedAt": new Date().toISOString(),
          "expenses.$.rejectionReason": data.status === "Declined" ? data.reason || "" : "",
        },
      }
    );

    if (result.modifiedCount === 0) {
      return NextResponse.json({ error: "Expense not found" }, { status: 404 });
    }

    // Make API call to localhost:8000 based on status
    try {
      console.log(`Attempting to notify backend for expense ${id} with status ${data.status}`);

      if (data.status === "Approved") {
        const payload = { reason: data.reason || "Approved - all documentation correct" };
        console.log("Making approval API call with payload:", payload);

        const response = await fetch(`http://localhost:8000/api/expenses/${id}/accept`, {
          method: "POST",
          body: JSON.stringify(payload),
          headers: { "Content-Type": "application/json" },
        });

        console.log("Approval API response status:", response.status);
        const responseData = await response.text();
        console.log("Approval API response body:", responseData);
      } else if (data.status === "Declined") {
        const formData = new FormData();
        formData.append("reason", data.reason || "Rejected - insufficient documentation");
        console.log("Making rejection API call with reason:", formData.get("reason"));

        const response = await fetch(`http://localhost:8000/api/expenses/${id}/reject`, {
          method: "POST",
          body: formData,
        });

        console.log("Rejection API response status:", response.status);
        const responseData = await response.text();
        console.log("Rejection API response body:", responseData);
      }

      console.log("Backend notification completed successfully");
    } catch (error) {
      console.error("Error notifying backend:", error);
      console.error("Error details:", {
        message: error.message,
        stack: error.stack,
        status: error.status,
      });
      // Continue execution even if notification fails
    }

    return NextResponse.json({ success: true, status: data.status });
  } finally {
    await client.close();
  }
}
