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

    return NextResponse.json({ success: true, status: data.status });
  } finally {
    await client.close();
  }
}
