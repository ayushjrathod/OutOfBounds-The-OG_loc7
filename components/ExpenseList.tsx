import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface Expense {
  expenseId: string;
  description: string;
  submittedDate: string;
  approvalDate?: string;
  employeeId?: string;
  status: string;
  amount: number;
  rejectionReason?: string;
}

interface ExpenseListProps {
  expenses: Expense[];
  showEmployeeId?: boolean;
  linkPrefix: string;
}

export function ExpenseList({ expenses, showEmployeeId = false, linkPrefix }: ExpenseListProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Description</TableHead>
          <TableHead>Submitted Date</TableHead>
          <TableHead>Approval Date</TableHead>
          {showEmployeeId && <TableHead>Employee ID</TableHead>}
          <TableHead>Status</TableHead>
          <TableHead>Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {expenses.map((expense) => (
          <TableRow key={expense.expenseId}>
            <TableCell>{expense.description}</TableCell>
            <TableCell>{new Date(expense.submittedDate).toLocaleDateString()}</TableCell>
            <TableCell>{expense.approvalDate ? new Date(expense.approvalDate).toLocaleDateString() : "-"}</TableCell>
            {showEmployeeId && <TableCell>{expense.employeeId}</TableCell>}
            <TableCell>
              {expense.status === "Declined" && expense.rejectionReason ? (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <Badge variant="destructive">{expense.status}</Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{expense.rejectionReason}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              ) : (
                <Badge variant={expense.status === "Approved" ? "default" : "destructive"}>{expense.status}</Badge>
              )}
            </TableCell>
            <TableCell>${expense.amount.toFixed(2)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
