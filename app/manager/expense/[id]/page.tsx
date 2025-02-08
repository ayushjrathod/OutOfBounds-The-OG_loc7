"use client"

import { useState } from "react"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, CheckCircle } from "lucide-react"

// This would typically come from your API or database
const mockExpense = {
  expenseId: "1",
  expenseType: "Travel",
  amount: 150.0,
  date: new Date("2023-05-01"),
  vendor: "Airline XYZ",
  description: "Flight to client meeting",
  receiptImage: "/placeholder.svg",
  item_details: [
    { item: "Flight ticket", amount: 120.0 },
    { item: "Taxi", amount: 30.0 },
  ],
  aiSummary: "This expense appears to be a legitimate travel expense for a client meeting.",
  status: "Pending",
  submittedDate: new Date("2023-05-02"),
  approvedBy: "",
  approvalDate: null,
  rejectionReason: "",
  fraudScore: 0.1,
  isAnomaly: false,
}

export default function ExpenseDetails({ params }: { params: { id: string } }) {
  const [status, setStatus] = useState(mockExpense.status)
  const router = useRouter()

  const handleApprove = () => {
    setStatus("Approved")
    // Here you would typically make an API call to update the status
  }

  const handleDecline = () => {
    setStatus("Declined")
    // Here you would typically make an API call to update the status
  }

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Expense Details - {params.id}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="aspect-video relative">
            <Image
              src={mockExpense.receiptImage || "/placeholder.svg"}
              alt="Receipt"
              layout="fill"
              objectFit="contain"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold">Expense Type</h3>
              <p>{mockExpense.expenseType}</p>
            </div>
            <div>
              <h3 className="font-semibold">Amount</h3>
              <p>${mockExpense.amount.toFixed(2)}</p>
            </div>
            <div>
              <h3 className="font-semibold">Date</h3>
              <p>{mockExpense.date.toLocaleDateString()}</p>
            </div>
            <div>
              <h3 className="font-semibold">Vendor</h3>
              <p>{mockExpense.vendor}</p>
            </div>
            <div className="col-span-2">
              <h3 className="font-semibold">Description</h3>
              <p>{mockExpense.description}</p>
            </div>
          </div>
          <div>
            <h3 className="font-semibold">Item Details</h3>
            <ul>
              {mockExpense.item_details.map((item, index) => (
                <li key={index}>
                  {item.item}: ${item.amount.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold">AI Summary</h3>
            <p>{mockExpense.aiSummary}</p>
          </div>
          <div>
            <h3 className="font-semibold">Status</h3>
            <Badge variant={status === "Approved" ? "success" : status === "Declined" ? "destructive" : "warning"}>
              {status}
            </Badge>
          </div>
          <div>
            <h3 className="font-semibold">Submitted Date</h3>
            <p>{mockExpense.submittedDate.toLocaleDateString()}</p>
          </div>
          {mockExpense.fraudScore > 0.5 || mockExpense.isAnomaly ? (
            <div className="bg-yellow-100 p-4 rounded-md flex items-center space-x-2">
              <AlertTriangle className="text-yellow-700" />
              <span className="text-yellow-700">This expense has been flagged for review.</span>
            </div>
          ) : (
            <div className="bg-green-100 p-4 rounded-md flex items-center space-x-2">
              <CheckCircle className="text-green-700" />
              <span className="text-green-700">This expense appears to be normal.</span>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
          <Button variant="outline" onClick={() => router.push("/manager")}>
            Back
          </Button>
          <Button variant="destructive" onClick={handleDecline} disabled={status !== "Pending"}>
            Decline
          </Button>
          <Button variant="default" onClick={handleApprove} disabled={status !== "Pending"}>
            Approve
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

