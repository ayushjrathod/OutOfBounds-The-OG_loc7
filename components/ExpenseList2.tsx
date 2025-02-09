import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import Link from "next/link";

interface Expense {
  expenseId: string;
  description: string;
  date: Date;
  employeeId?: string;
  status: string;
  amount: number;
  fraudScore: number;
  isAnomaly: boolean;
}

interface ExpenseListProps {
  expenses: Expense[];
  showEmployeeId?: boolean;
  linkPrefix: string;
}

export function ExpenseList2({ expenses, showEmployeeId = false, linkPrefix }: ExpenseListProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Description</TableHead>
          {showEmployeeId && <TableHead>Employee ID</TableHead>}
          <TableHead>Date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead>Anomaly Score</TableHead>
          <TableHead>Anomaly</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {expenses.map((expense) => (
          <TableRow key={expense.expenseId}>
            <TableCell className="py-4">
              <Link href={`${linkPrefix}/${expense.expenseId}`} className="text-blue-600 hover:underline">
                <span className="font-semibold">{expense.description}</span>
              </Link>
            </TableCell>
            {showEmployeeId && <TableCell className="py-4">{expense.employeeId}</TableCell>}
            <TableCell className="py-4">
              {new Intl.DateTimeFormat("en-US", { year: "numeric", month: "long", day: "numeric" }).format(
                new Date(expense.date)
              )}
            </TableCell>
            <TableCell className="py-4">
              <Badge
                variant={
                  expense.status === "Approved" ? "default" : expense.status === "Pending" ? "pending" : "destructive"
                }
              >
                {expense.status}
              </Badge>
            </TableCell>
            <TableCell className="py-4">{`₹${expense.amount.toFixed(2)}`}</TableCell>
            <TableCell className="py-4">{(expense.fraudScore * 100).toFixed(1)}%</TableCell>
            <TableCell className="py-4">
              <span className={expense.isAnomaly ? "text-red-600 font-medium" : "text-gray-900"}>
                {expense.isAnomaly ? "Yes" : "No"}
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
