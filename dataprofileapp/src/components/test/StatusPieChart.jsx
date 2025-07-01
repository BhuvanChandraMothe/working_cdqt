import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = {
  'Passed': '#00C49F',   // Green
  'Warning': '#FFBB28', // Yellow/Orange
  'Failed': '#FF8042',  // Orange/Red (Assuming 'Failed' is the status, not 'Fail')
  'Complete': '#0088FE', // Blue (if 'Complete' is a status)
  'Error': '#C84F4F' // Darker Red for Error if it's a direct status
};

const StatusPieChart = ({ data, onSliceClick, selectedStatus }) => { // Renamed prop
  const chartData = Object.keys(data).map(key => ({
    name: key,
    value: data[key],
  }));

  const handlePieClick = (dataEntry) => {
    const clickedStatus = dataEntry.name; // Uses clickedStatus
    onSliceClick(prevStatus => (prevStatus === clickedStatus ? null : clickedStatus)); // Uses prevStatus
  };

  return (
    <div style={{ color: '#e0e0e0' }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            fill="#8884d8"
            paddingAngle={5}
            dataKey="value"
            labelLine={false}
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
            onClick={handlePieClick}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[entry.name] || '#8884d8'}
                opacity={selectedStatus === entry.name || selectedStatus === null ? 1 : 0.4} // Uses selectedStatus
                style={{ cursor: 'pointer' }}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#333', borderColor: '#555', color: '#f0f0f0' }}
            itemStyle={{ color: '#f0f0f0' }}
          />
          <Legend wrapperStyle={{ color: '#e0e0e0' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StatusPieChart;