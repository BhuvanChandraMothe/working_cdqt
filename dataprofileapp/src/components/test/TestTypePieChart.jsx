import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS_TEST_TYPE = [
  '#A0D8B3', '#D0F0C0', '#F5D3A3', '#F9B282', '#E87D7D', '#C86D7D', '#A85D7D', '#884D7D',
  '#99C2A2', '#B9D1C2', '#D3E0E2', '#E6E6E6', '#F5F5F5', '#C0A0D8', '#A0C8E0'
];

const TestTypePieChart = ({ data, onSliceClick, selectedStatus }) => { // Renamed prop
  const chartData = Object.keys(data).map(key => ({
    name: key,
    value: data[key],
  }));

  const handlePieClick = (dataEntry) => {
    const clickedTestType = dataEntry.name;
    onSliceClick(prevTestType => (prevTestType === clickedTestType ? null : clickedTestType));
  };

  if (chartData.length === 0) {
    return <div className="no-data-message">No test types found for the selected status.</div>;
  }

  return (
    <div style={{ color: '#e0e0e0' }}>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={80}
            fill="#8884d8"
            paddingAngle={3}
            dataKey="value"
            labelLine={false}
            onClick={handlePieClick}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS_TEST_TYPE[index % COLORS_TEST_TYPE.length]}
                opacity={selectedStatus === entry.name || selectedStatus === null ? 1 : 0.4} // Uses selectedStatus
                style={{ cursor: 'pointer' }}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#333', borderColor: '#555', color: '#f0f0f0' }}
            itemStyle={{ color: '#f0f0f0' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TestTypePieChart;