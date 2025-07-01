import React from 'react';

const TestDetailsTable = ({ data, selectedStatus, selectedTestType }) => { // Renamed prop
  if (!data || data.length === 0) {
    return <div className="no-data-message">No detailed results to display for the selected filters.</div>;
  }

  const columns = [
    { key: 'table_name', header: 'Table' },
    { key: 'column_names', header: 'Column(s)' },
    { key: 'test_description', header: 'Description' },
    { key: 'dq_prevalence', header: 'DQ Prevalence' },
    { key: 'dq_record_ct', header: 'DQ Record Count' },
  ];

  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => (
            <th key={col.key}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, index) => (
          <tr key={row.id || index}>
            {columns.map(col => (
              <td key={`${row.id}-${col.key}`}>
                {row[col.key] !== null && row[col.key] !== undefined ? String(row[col.key]) : 'N/A'}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TestDetailsTable;