"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import CategoryDistribution from "../../components/charts/CategoryDistribution";
import DepartmentExpenses from "../../components/charts/DepartmentExpenses";
import EmployeeExpenses from "../../components/charts/EmployeeExpenses";
import FraudAnalysis from "../../components/charts/FraudAnalysis";
import MonthlyTrends from "../../components/charts/MonthlyTrends";
import VendorSpending from "../../components/charts/VendorSpending";

export default function Visualizations() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Expense Analytics Dashboard</h1>
        <Separator className="my-4" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Increase the height and ensure proper padding for chart containers */}
        <Card className="min-h-[500px]">
          <CardContent className="p-6 h-[450px]">
            <MonthlyTrends />
          </CardContent>
        </Card>

        <Card className="min-h-[500px]">
          <CardContent className="p-6 h-[450px]">
            <DepartmentExpenses />
          </CardContent>
        </Card>

        <Card className="min-h-[500px]">
          <CardContent className="p-6 h-[450px]">
            <CategoryDistribution />
          </CardContent>
        </Card>

        <Card className="min-h-[500px]">
          <CardContent className="p-6 h-[450px]">
            <EmployeeExpenses />
          </CardContent>
        </Card>

        <Card className="min-h-[500px]">
          <CardContent className="p-6 h-[450px]">
            <FraudAnalysis />
          </CardContent>
        </Card>

        <Card className="min-h-[500px]">
          <CardContent className="p-6 h-[450px]">
            <VendorSpending />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
