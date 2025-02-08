import { ExpenseList } from "@/components/ExpenseList"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// This would typically come from your API or database
const mockExpenses = [
  {
    expenseId: "1",
    date: new Date("2023-05-01"),
    employeeId: "EMP001",
    status: "Pending",
    amount: 150.0,
  },
  {
    expenseId: "2",
    date: new Date("2023-05-02"),
    employeeId: "EMP002",
    status: "Approved",
    amount: 200.0,
  },
  // Add more mock data as needed
]

export default function ManagerDashboard() {
  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Manager Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <ExpenseList expenses={mockExpenses} showEmployeeId={true} linkPrefix="/manager/expense" />
        </CardContent>
      </Card>
    </div>
  )
}

