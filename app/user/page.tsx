import { ExpenseList } from "@/components/ExpenseList"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// This would typically come from your API or database
const mockUserExpenses = [
  {
    expenseId: "1",
    date: new Date("2023-05-01"),
    status: "Pending",
    amount: 150.0,
  },
  {
    expenseId: "2",
    date: new Date("2023-05-02"),
    status: "Approved",
    amount: 200.0,
  },
  // Add more mock data as needed
]

export default function UserDashboard() {
  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>User Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <ExpenseList expenses={mockUserExpenses} showEmployeeId={false} linkPrefix="/user/expense" />
        </CardContent>
      </Card>
    </div>
  )
}

