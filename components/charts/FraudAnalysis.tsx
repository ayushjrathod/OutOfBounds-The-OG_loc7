"use client";

import { useState, useEffect } from "react";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import axios from "axios";

const FraudAnalysis = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/analytics/fraud-analysis");
        const formattedData = response.data.map((item) => ({
          department: item._id.departmentId,
          fraudScore: item.avg_fraud_score,
          count: item.count,
          isAnomaly: item._id.isAnomaly,
        }));
        setData(formattedData);
      } catch (error) {
        console.error("Error fetching fraud analysis:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold mb-4">Fraud Analysis</h3>
      <ResponsiveContainer width="100%" height="90%">
        <ScatterChart>
          <CartesianGrid />
          <XAxis dataKey="department" />
          <YAxis dataKey="fraudScore" />
          <Tooltip />
          <Legend />
          <Scatter data={data.filter((d) => !d.isAnomaly)} name="Normal Transactions" fill="#82ca9d" />
          <Scatter data={data.filter((d) => d.isAnomaly)} name="Anomalies" fill="#ff0000" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FraudAnalysis;
