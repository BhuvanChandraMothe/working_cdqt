import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TestSuiteProgressBar from './TestSuiteProgressBar';
import axiosInstance from '../../utilities/axiosInstance';
axiosInstance

const TestSuitesSummaryChart = () => {
  const [suiteSummaries, setSuiteSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    const fetchSuiteSummaries = async () => {
      try {
        setLoading(true);
        setError(null); // Clear previous errors
        const response = await axiosInstance.get(`${API_BASE_URL}/test_runs_summary_by_suite`);
        setSuiteSummaries(response.data.test_suite_summaries);
      } catch (err) {
        setError("Failed to fetch test suite summaries.");
        console.error("Error fetching test suite summaries:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSuiteSummaries();
  }, []);

  if (loading) {
    return <div className="no-data-message">Loading test suite summaries...</div>;
  }

  if (error) {
    return <div className="no-data-message error-message">Error: {error}</div>;
  }

  if (suiteSummaries.length === 0) {
    return <div className="no-data-message">No test suite data available to display.</div>;
  }

  return (
    <div className="test-suites-summary-chart-container">
      <h3 className="chart-title">Test Suite Overview</h3>
      {suiteSummaries.map((suite, index) => (
        <TestSuiteProgressBar key={suite.test_suite_id} suiteData={suite} />
      ))}
    </div>
  );
};

export default TestSuitesSummaryChart;