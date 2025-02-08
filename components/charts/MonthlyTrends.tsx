"use client";

import axios from "axios";
import { useEffect, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const MonthlyTrends = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/analytics/monthly-trends");
        const formattedData = response.data.map((item) => ({
          month: `${item._id.year}-${String(item._id.month).padStart(2, "0")}`,
          amount: item.total_amount,
        }));
        setData(formattedData);
      } catch (error) {
        console.error("Error fetching monthly trends:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="w-full h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-4">Monthly Expense Trends</h3>
      <div className="flex-1 min-h-[300px]">
        {" "}
        {/* Add minimum height */}
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" angle={-45} textAnchor="end" height={60} interval={0} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="amount" stroke="#8884d8" activeDot={{ r: 8 }} name="Total Amount" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MonthlyTrends;
