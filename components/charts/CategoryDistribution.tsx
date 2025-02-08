"use client";
import axios from "axios";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const CategoryDistribution = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/analytics/category-distribution");
        setData(response.data);
      } catch (error) {
        console.error("Error fetching category distribution:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold mb-4">Category Distribution</h3>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="_id" angle={-45} textAnchor="end" height={60} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="total_amount" fill="#82ca9d" name="Total Amount" />
          <Bar dataKey="count" fill="#8884d8" name="Number of Expenses" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CategoryDistribution;
