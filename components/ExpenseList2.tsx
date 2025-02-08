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
          <TableHead>Fraud Score</TableHead>
          <TableHead>Anomaly</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {expenses.map((expense) => (
          <TableRow key={expense.expenseId}>
            <TableCell>
              <Link href={`${linkPrefix}/${expense.expenseId}`} className="text-blue-600 hover:underline">
                {expense.description}
              </Link>
            </TableCell>
            {showEmployeeId && <TableCell>{expense.employeeId}</TableCell>}
            <TableCell>
              {new Intl.DateTimeFormat("en-US", { year: "numeric", month: "long", day: "numeric" }).format(
                new Date(expense.date)
              )}
            </TableCell>
            <TableCell>
              <Badge variant={expense.status === "Approved" ? "default" : "destructive"}>{expense.status}</Badge>
            </TableCell>
            <TableCell>${expense.amount.toFixed(2)}</TableCell>
            <TableCell>{(expense.fraudScore * 100).toFixed(1)}%</TableCell>
            <TableCell>{expense.isAnomaly ? "Yes" : "No"}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
