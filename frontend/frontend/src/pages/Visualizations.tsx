import { useState, useEffect } from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import DepartmentExpenses from '../components/charts/DepartmentExpenses';
import MonthlyTrends from '../components/charts/MonthlyTrends';
import CategoryDistribution from '../components/charts/CategoryDistribution';
import FraudAnalysis from '../components/charts/FraudAnalysis';
import VendorSpending from '../components/charts/VendorSpending';
import EmployeeExpenses from '../components/charts/EmployeeExpenses';

const Visualizations = () => {
  return (
    <Grid container spacing={3} padding={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Expense Analytics Dashboard
        </Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
          <MonthlyTrends />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
          <DepartmentExpenses />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
          <CategoryDistribution />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
          <EmployeeExpenses />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
          <FraudAnalysis />
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: 2, height: '400px' }}>
          <VendorSpending />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Visualizations;
