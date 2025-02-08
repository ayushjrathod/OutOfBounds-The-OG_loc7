"use client";
import { ExpenseList2 } from "@/components/ExpenseList2";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { useEffect, useState } from "react";

export default function UserDashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:3000/api/db/manager", {
        method: "GET",
      });
      const result = await res.json();
      // Sort expenses by fraudScore in descending order
      const sortedData = result.sort((a: any, b: any) => b.fraudScore - a.fraudScore);
      setData(sortedData);
    };

    fetchData();
  }, []);
  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Manager Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <ExpenseList2 expenses={data} showEmployeeId={true} linkPrefix="/manager/expense" />
        </CardContent>
      </Card>
    </div>
  );
}
