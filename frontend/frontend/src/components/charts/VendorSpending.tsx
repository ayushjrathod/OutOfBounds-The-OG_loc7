import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Typography } from '@mui/material';
import axios from 'axios';

const VendorSpending = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8080/api/analytics/vendor-spending');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching vendor spending:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Top Vendor Spending</Typography>
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
    </>
  );
};

export default VendorSpending;
