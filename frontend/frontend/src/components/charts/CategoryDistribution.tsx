import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Typography } from '@mui/material';
import axios from 'axios';

const CategoryDistribution = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8080/api/analytics/category-distribution');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching category distribution:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Category Distribution</Typography>
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
    </>
  );
};

export default CategoryDistribution;
