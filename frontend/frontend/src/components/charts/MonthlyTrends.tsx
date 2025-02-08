import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Typography } from '@mui/material';
import axios from 'axios';

const MonthlyTrends = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8080/api/analytics/monthly-trends');
        const formattedData = response.data.map(item => ({
          month: `${item._id.year}-${String(item._id.month).padStart(2, '0')}`,
          amount: item.total_amount
        }));
        setData(formattedData);
      } catch (error) {
        console.error('Error fetching monthly trends:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Monthly Expense Trends</Typography>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="month" 
            angle={-45} 
            textAnchor="end" 
            height={60}
            interval={0}
          />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="amount" 
            stroke="#8884d8" 
            activeDot={{ r: 8 }} 
            name="Total Amount"
          />
        </LineChart>
      </ResponsiveContainer>
    </>
  );
};

export default MonthlyTrends;
