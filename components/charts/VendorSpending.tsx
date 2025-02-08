"use client";

import axios from "axios";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const VendorSpending = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8080/api/analytics/vendor-spending");
        setData(response.data);
      } catch (error) {
        console.error("Error fetching vendor spending:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold mb-4">Top Vendor Spending</h3>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="_id" type="category" width={150} />
          <Tooltip />
          <Legend />
          <Bar dataKey="total_amount" fill="#8884d8" name="Total Amount" />
          <Bar dataKey="transaction_count" fill="#82ca9d" name="Transaction Count" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default VendorSpending;
