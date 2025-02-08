"use client";
import { ExpenseList2 } from "@/components/ExpenseList2";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { useEffect, useState } from "react";

export default function UserDashboard() {
  // Changed: initialize "data" as an empty array instead of null
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:3000/api/db/manager", {
        method: "GET",
      });
      const result = await res.json();
      setData(result);
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
