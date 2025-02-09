import { MongoClient } from "mongodb";
import { NextResponse } from "next/server";

export async function GET() {
  const uri =
    process.env.MONGO_URI_neha ||
    "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db("expensesDB");
    const collections = await db.collection("EmployeeExpenses").find().toArray();

    const expenses = collections.flatMap((doc: any) =>
      doc.expenses.map((exp: any) => ({
        expenseId: exp.expenseId,
        expenseType: exp.expenseType,
        description: exp.description,
        date: new Date(exp.date),
        employeeId: exp.employeeId || doc.employeeId,
        departmentId: doc.departmentId,
        vendor: exp.vendor,
        categories: exp.categories,
        receiptImage: exp.receiptImage,
        bill_number: exp.bill_number,
        status: exp.status,
        amount: typeof exp.amount === "number" ? exp.amount : exp.amount.$numberDouble,
        fraudScore: typeof exp.fraudScore === "number" ? exp.fraudScore : exp.fraudScore.$numberDouble,
        isAnomaly: exp.isAnomaly,
        item_details: (exp.item_details || []).map((item: any) => ({
          name: item.name,
          price: typeof item.price === "number" ? item.price : item.price.$numberDouble,
        })),
        aiSummary: exp.aiSummary,
        submittedDate: new Date(exp.submittedDate),
        approvalDate: exp.approvalDate ? new Date(exp.approvalDate) : null,
        approvedBy: exp.approvedBy,
        rejectionReason: exp.rejectionReason,
        createdAt: exp.createdAt,
        updatedAt: exp.updatedAt,
      }))
    );
    return NextResponse.json(expenses);
  } finally {
    await client.close();
  }
}
