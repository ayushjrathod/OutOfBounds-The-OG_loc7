import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Typography } from '@mui/material';
import axios from 'axios';

const EmployeeExpenses = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8080/api/analytics/employee-expenses');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching employee expenses:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Employee Expenses Overview</Typography>
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
    </>
  );
};

export default EmployeeExpenses;
