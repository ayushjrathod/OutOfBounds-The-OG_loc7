"use client";

import axios from "axios";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const EmployeeExpenses = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/analytics/employee-expenses");
        setData(response.data);
      } catch (error) {
        console.error("Error fetching employee expenses:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold mb-4">Employee Expenses Overview</h3>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="_id" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="total_amount" fill="#8884d8" name="Total Amount" />
          <Bar dataKey="transaction_count" fill="#82ca9d" name="Transaction Count" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EmployeeExpenses;
