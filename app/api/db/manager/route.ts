import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

export async function GET() {
  const uri =
    process.env.MONGODB_URI_neha ||
    "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("expensesDB"); // specify name if needed
    const collections = await db.collection("EmployeeExpenses").find().toArray(); // Convert cursor to array
    // Flatten the response: map each document's expenses array and convert date to Date object.
    const expenses = collections.flatMap((doc: any) =>
      doc.expenses.map((exp: any) => ({
        expenseId: exp.expenseId,
        date: new Date(exp.date),
        employeeId: exp.employeeId || doc.employeeId,
        status: exp.status,
        amount: exp.amount,
        // ...include other fields as necessary...
      }))
    );
    return NextResponse.json(expenses);
  } finally {
    await client.close();
  }
}
