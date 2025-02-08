import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import Link from "next/link";

interface Expense {
  expenseId: string;
  date: Date;
  employeeId?: string;
  status: string;
  amount: number;
}

interface ExpenseListProps {
  expenses: Expense[];
  showEmployeeId?: boolean;
  linkPrefix: string;
}

export function ExpenseList({ expenses, showEmployeeId = false, linkPrefix }: ExpenseListProps) {
  console.log(expenses);
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Expense ID</TableHead>
          <TableHead>Date</TableHead>
          {showEmployeeId && <TableHead>Employee ID</TableHead>}
          <TableHead>Status</TableHead>
          <TableHead>Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {expenses.map((expense) => (
          <TableRow key={expense.expenseId}>
            <TableCell>
              <Link href={`${linkPrefix}/${expense.expenseId}`} className="text-blue-600 hover:underline">
                {expense.expenseId}
              </Link>
            </TableCell>
            <TableCell>{new Date(expense.date).toLocaleDateString()}</TableCell>
            {showEmployeeId && <TableCell>{expense.employeeId}</TableCell>}
            <TableCell>
              <Badge variant={expense.status === "Approved" ? "default" : "destructive"}>{expense.status}</Badge>
            </TableCell>
            <TableCell>${expense.amount.toFixed(2)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
