"use client";
import { ExpenseList } from "@/components/ExpenseList2";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { useEffect, useState } from "react";
export default async function ManagerDashboard() {
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
          <ExpenseList expenses={data} showEmployeeId={true} linkPrefix="/manager/expense" />
        </CardContent>
      </Card>
    </div>
  );
}
