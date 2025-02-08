import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Typography } from '@mui/material';
import axios from 'axios';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const DepartmentExpenses = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8080/api/analytics/department-expenses');
        // Format data for pie chart
        const formattedData = response.data.map(item => ({
          name: item._id,
          value: item.total_amount
        }));
        setData(formattedData);
      } catch (error) {
        console.error('Error fetching department expenses:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Department Expenses Distribution</Typography>
      <ResponsiveContainer width="100%" height="90%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={80}
            fill="#8884d8"
            label={(entry) => `${entry.name}: ${entry.value.toFixed(2)}`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </>
  );
};

export default DepartmentExpenses;
