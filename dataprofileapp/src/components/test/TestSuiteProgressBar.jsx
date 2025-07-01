import React from 'react';

const TestSuiteProgressBar = ({ suiteData }) => {
  const {
    test_suite_id,
    passed_ct,
    failed_ct,
    warning_ct,
    error_ct,
    total_tests_executed,
    percentages
  } = suiteData;

  if (total_tests_executed === 0) {
    return (
      <div className="test-suite-progress-bar-container no-data">
        <p>No tests executed for {test_suite_id.substring(0, 8)}...</p>
      </div>
    );
  }

  // Define colors for each segment, matching the general theme
  const segmentColors = {
    passed: '#00C49F',  // Green (Passed)
    warning: '#FFBB28', // Yellow/Orange (Warning)
    failed: '#FF8042',  // Orange/Red (Failed)
    error: '#C84F4F',   // Darker Red (Error) - distinct from failed if needed
    // Assuming 'Dismissed' is not directly from the API for now, but can be added if needed
  };

  return (
    <div className="test-suite-progress-bar-container">
      <div className="test-suite-id">{test_suite_id.substring(0, 8)}...</div> {/* Display truncated ID */}
      <div className="progress-bar-wrapper">
        <div
          className="progress-segment passed"
          style={{ width: `${percentages.passed_pct || 0}%`, backgroundColor: segmentColors.passed }}
          title={`Passed: ${passed_ct} (${percentages.passed_pct.toFixed(1)}%)`}
        ></div>
        <div
          className="progress-segment warning"
          style={{ width: `${percentages.warning_pct || 0}%`, backgroundColor: segmentColors.warning }}
          title={`Warning: ${warning_ct} (${percentages.warning_pct.toFixed(1)}%)`}
        ></div>
        <div
          className="progress-segment failed"
          style={{ width: `${percentages.failed_pct || 0}%`, backgroundColor: segmentColors.failed }}
          title={`Failed: ${failed_ct} (${percentages.failed_pct.toFixed(1)}%)`}
        ></div>
        <div
          className="progress-segment error"
          style={{ width: `${percentages.error_pct || 0}%`, backgroundColor: segmentColors.error }}
          title={`Error: ${error_ct} (${percentages.error_pct.toFixed(1)}%)`}
        ></div>
      </div>
      <div className="progress-legend">
        <span style={{ color: segmentColors.passed }}>• Passed: {passed_ct}</span>
        <span style={{ color: segmentColors.warning }}>• Warning: {warning_ct}</span>
        <span style={{ color: segmentColors.failed }}>• Failed: {failed_ct}</span>
        <span style={{ color: segmentColors.error }}>• Error: {error_ct}</span>
        {/* If 'Dismissed' data comes from somewhere, add it here */}
        {/* <span>• Dismissed: 0</span> */}
      </div>
    </div>
  );
};

export default TestSuiteProgressBar;