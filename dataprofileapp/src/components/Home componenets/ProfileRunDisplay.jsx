// import React, { useState, useEffect, useMemo, useCallback } from 'react';
// import {
//     Paper,
//     Typography,
//     Grid,
//     Box,
//     CircularProgress,
//     Card,
//     CardContent,
//     useTheme,
//     Select,
//     MenuItem,
//     FormControl,
//     InputLabel,
//     Table,
//     TableBody,
//     TableCell,
//     TableContainer,
//     TableHead,
//     TableRow,
// } from '@mui/material';
// import { styled } from '@mui/system';
// import { format } from 'date-fns';

// // Assuming these API functions exist in your project
// import { getDashboardOverview, getTableNamesForProfilingRun, getProfilingTableDetails } from '../../api/dbapi';

// // Styled components (keeping your existing ones and adding new ones)
// const DashboardCard = styled(Card)(({ theme }) => ({
//     display: 'flex',
//     flexDirection: 'column',
//     alignItems: 'center',
//     justifyContent: 'center',
//     padding: theme.spacing(2),
//     textAlign: 'center',
//     minHeight: 120,
//     backgroundColor: theme.palette.mode === 'light' ? '#e3f2fd' : '#263238',
//     color: theme.palette.mode === 'light' ? theme.palette.primary.dark : theme.palette.primary.light,
//     borderRadius: theme.shape.borderRadius,
//     boxShadow: theme.shadows[3],
// }));

// const ValueText = styled(Typography)(({ theme }) => ({
//     fontSize: '2.5rem',
//     fontWeight: 'bold',
//     lineHeight: 1,
//     color: theme.palette.mode === 'light' ? theme.palette.primary.main : theme.palette.primary.light,
// }));

// const LabelText = styled(Typography)(({ theme }) => ({
//     fontSize: '0.9rem',
//     color: theme.palette.text.secondary,
//     marginTop: theme.spacing(0.5),
// }));

// // Function to format large numbers (e.g., 32.5M, 5.2K)
// const formatNumber = (num) => {
//     if (num === null || num === undefined) return 'N/A';
//     if (num >= 1000000) {
//         return (num / 1000000).toFixed(1) + 'M';
//     }
//     if (num >= 1000) {
//         return (num / 1000).toFixed(1) + 'K';
//     }
//     return num.toString();
// };

// // --- Sparkline Component ---
// const Sparkline = ({ data, color, nullColor, width = 100, height = 30 }) => {
//     if (!data || data.length < 2) {
//         return <Box sx={{ width, height, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', color: nullColor }}>Not enough data</Box>;
//     }

//     const maxDataValue = Math.max(...data);
//     const minDataValue = Math.min(...data);

//     // Normalize data to fit within the SVG height
//     const points = data.map((d, i) => {
//         const x = (i / (data.length - 1)) * width;
//         // Scale y to be inverse (higher value means lower y-coordinate for "downward trend")
//         const y = height - ((d - minDataValue) / (maxDataValue - minDataValue + 0.001)) * height; // Add epsilon to prevent division by zero
//         return `${x},${y}`;
//     }).join(' ');

//     // Determine if the trend is downward (simple check: last value vs first value)
//     const isDownwardTrend = data[data.length - 1] < data[0];
//     const trendColor = isDownwardTrend ? 'purple' : color; // Purple for downward, default color otherwise

//     return (
//         <Box sx={{ width, height, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//             <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
//                 <polyline
//                     fill="none"
//                     stroke={trendColor}
//                     strokeWidth="1.5"
//                     points={points}
//                 />
//             </svg>
//         </Box>
//     );
// };

// // --- Radial Gauge Component ---
// const RadialGauge = ({ value, title, subValueLabel, subValue, trendData, gaugeColor = '#ffc107', sparklineNullColor = 'teal', sparklineDistinctColor = 'purple' }) => {
//     const theme = useTheme();
//     const normalizedValue = Math.min(100, Math.max(0, value)); // Ensure value is between 0 and 100

//     return (
//         <Box sx={{
//             display: 'flex',
//             flexDirection: 'column',
//             alignItems: 'center',
//             justifyContent: 'center',
//             position: 'relative',
//             width: 160, // Adjust size as needed
//             height: 180, // Slightly taller to accommodate sparkline
//             p: 2,
//             borderRadius: theme.shape.borderRadius,
//             backgroundColor: theme.palette.background.paper,
//             boxShadow: theme.shadows[3],
//         }}>
//             <Box sx={{ position: 'relative', width: 100, height: 100, mb: 1 }}>
//                 <CircularProgress
//                     variant="determinate"
//                     value={100}
//                     size={100}
//                     thickness={4}
//                     sx={{
//                         color: theme.palette.action.disabledBackground, // Background arc color
//                         position: 'absolute',
//                         left: 0,
//                         top: 0,
//                     }}
//                 />
//                 <CircularProgress
//                     variant="determinate"
//                     value={normalizedValue}
//                     size={100}
//                     thickness={4}
//                     sx={{
//                         color: gaugeColor, // Filled arc color (yellow by default)
//                         position: 'absolute',
//                         left: 0,
//                         top: 0,
//                         transform: 'rotate(-90deg)', // Start from top
//                         transformOrigin: 'center center',
//                     }}
//                 />
//                 <Box
//                     sx={{
//                         position: 'absolute',
//                         top: '50%',
//                         left: '50%',
//                         transform: 'translate(-50%, -50%)',
//                         display: 'flex',
//                         flexDirection: 'column',
//                         alignItems: 'center',
//                         justifyContent: 'center',
//                     }}
//                 >
//                     <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>
//                         {`${Math.round(value)}%`}
//                     </Typography>
//                 </Box>
//             </Box>
//             <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary, mt: 0.5 }}>
//                 {title}
//             </Typography>

//             {/* Sparkline */}
//             <Box sx={{ mt: 1 }}>
//                 <Sparkline
//                     data={trendData}
//                     color={sparklineDistinctColor}
//                     nullColor={sparklineNullColor}
//                     width={120} // Adjust sparkline width
//                     height={30} // Adjust sparkline height
//                 />
//             </Box>

//             {/* Contextual Value */}
//             {subValueLabel && (
//                 <Typography variant="caption" sx={{ color: theme.palette.text.primary, mt: 0.5 }}>
//                     <Typography component="span" sx={{ fontWeight: 'bold' }}>{subValueLabel}:</Typography> {subValue}
//                 </Typography>
//             )}
//         </Box>
//     );
// };


// const ProfileRunDisplay = () => {
//     const theme = useTheme();
//     const [dashboardData, setDashboardData] = useState(null);
//     const [loadingDashboard, setLoadingDashboard] = useState(true);
//     const [errorDashboard, setErrorDashboard] = useState(null);

//     const [selectedRunId, setSelectedRunId] = useState(null);
//     const [tableNames, setTableNames] = useState([]);
//     const [selectedTableName, setSelectedTableName] = useState('');
//     const [tableDetails, setTableDetails] = useState(null);
//     const [loadingTableDetails, setLoadingTableDetails] = useState(false);
//     const [errorTableDetails, setErrorTableDetails] = useState(null);

//     // Mock trend data for demonstration
//     // In a real application, you would fetch this from your backend
//     const [totalScoreTrend, setTotalScoreTrend] = useState([85, 88, 90, 87, 92, 95, 93, 91, 89, 86]);
//     const [cdeScoreTrend, setCdeScoreTrend] = useState([70, 75, 72, 78, 80, 82, 79, 76, 73, 70]);
//     const [profilingScoreTrend, setProfilingScoreTrend] = useState([90, 92, 91, 93, 95, 94, 96, 97, 98, 99]); // Example for Profiling

//     // Fetch dashboard overview and recent runs
//     useEffect(() => {
//         const fetchDashboardData = async () => {
//             try {
//                 setLoadingDashboard(true);
//                 const data = await getDashboardOverview();
//                 setDashboardData(data);
//                 setErrorDashboard(null);

//                 if (data.recentRuns && data.recentRuns.length > 0) {
//                     setSelectedRunId(data.recentRuns[0].profiling_id);
//                 }

//                 // Simulate fetching trend data (replace with actual API calls)
//                 // For now, we'll just use the mock data
//                 // const totalTrend = await fetchTotalScoreTrend();
//                 // setTotalScoreTrend(totalTrend);
//                 // const cdeTrend = await fetchCdeScoreTrend();
//                 // setCdeScoreTrend(cdeTrend);

//             } catch (err) {
//                 setErrorDashboard(err);
//                 console.error('Error fetching dashboard overview:', err);
//             } finally {
//                 setLoadingDashboard(false);
//             }
//         };

//         fetchDashboardData();
//     }, []);

//     // Fetch table names when selectedRunId changes
//     useEffect(() => {
//         const fetchTableNames = async () => {
//             if (selectedRunId) {
//                 try {
//                     const names = await getTableNamesForProfilingRun(selectedRunId);
//                     setTableNames(names);
//                     if (names.length > 0) {
//                         setSelectedTableName(names[0].tableName);
//                     } else {
//                         setSelectedTableName('');
//                     }
//                 } catch (err) {
//                     console.error(`Error fetching table names for run ${selectedRunId}:`, err);
//                     setTableNames([]);
//                     setSelectedTableName('');
//                 }
//             } else {
//                 setTableNames([]);
//                 setSelectedTableName('');
//             }
//         };
//         fetchTableNames();
//     }, [selectedRunId]);

//     // Fetch table details when selectedTableName or selectedRunId changes
//     useEffect(() => {
//         const fetchTableDetails = async () => {
//             if (selectedRunId && selectedTableName) {
//                 try {
//                     setLoadingTableDetails(true);
//                     const details = await getProfilingTableDetails(selectedRunId, selectedTableName);
//                     setTableDetails(details);
//                     setErrorTableDetails(null);
//                 } catch (err) {
//                     setErrorTableDetails(err);
//                     console.error(`Error fetching details for run ${selectedRunId}, table ${selectedTableName}:`, err);
//                 } finally {
//                     setLoadingTableDetails(false);
//                 }
//             } else {
//                 setTableDetails(null);
//             }
//         };
//         fetchTableDetails();
//     }, [selectedRunId, selectedTableName]);


//     // Handler for clicking a recent run entry
//     const handleRecentRunClick = useCallback((runId) => {
//         setSelectedRunId(runId);
//         setTableDetails(null);
//         setSelectedTableName('');
//     }, []);

//     if (loadingDashboard) {
//         return (
//             <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
//                 <CircularProgress />
//                 <Typography variant="h6" sx={{ ml: 2 }}>Loading Dashboard Data...</Typography>
//             </Box>
//         );
//     }

//     if (errorDashboard) {
//         return (
//             <Paper sx={{ p: 3, my: 3, bgcolor: theme.palette.error.light }}>
//                 <Typography color="error">Error loading dashboard: {errorDashboard.message}</Typography>
//                 <Typography variant="body2" color="text.secondary">Please check your backend connection and API.</Typography>
//             </Paper>
//         );
//     }

//     const { summary, recentRuns } = dashboardData;

//     // Calculate profiling score as a percentage (assuming it's a sub-score of total)
//     // This is a placeholder; you'll need actual data for this
//     const profilingScore = summary.profilingScore || 0; // Assuming summary provides this
//     const totalScorePercentage = summary.dqScore ? (summary.dqScore * 100).toFixed(1) : 'N/A';
//     const cdeScorePercentage = summary.cdeScore ? (summary.cdeScore * 100).toFixed(1) : 'N/A';


//     return (
//         <Grid container spacing={3}>
//             {/* Left Column: Profile Run Results */}
//             <Grid item xs={12} md={6}>
//                 <Paper sx={{ p: 3, height: '100%', bgcolor: theme.palette.background.paper, boxShadow: theme.shadows[4] }}>
//                     <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: theme.palette.text.primary }}>
//                         Profile Run Results
//                     </Typography>

//                     <Typography variant="h6" sx={{ mb: 2, color: theme.palette.text.secondary }}>
//                         Profile Run Dashboard
//                     </Typography>

//                     {/* Dashboard Cards (keeping existing ones) */}
//                     <Grid container spacing={2} sx={{ mb: 3 }}>
//                         <Grid item xs={6} sm={3}>
//                             <DashboardCard>
//                                 <ValueText>{summary.tables}</ValueText>
//                                 <LabelText>Tables</LabelText>
//                             </DashboardCard>
//                         </Grid>
//                         <Grid item xs={6} sm={3}>
//                             <DashboardCard>
//                                 <ValueText>{summary.columns}</ValueText>
//                                 <LabelText>Columns</LabelText>
//                             </DashboardCard>
//                         </Grid>
//                         <Grid item xs={6} sm={3}>
//                             <DashboardCard>
//                                 <ValueText>{formatNumber(summary.rowCount)}</ValueText>
//                                 <LabelText>Row Count</LabelText>
//                             </DashboardCard>
//                         </Grid>
//                         <Grid item xs={6} sm={3}>
//                             <DashboardCard>
//                                 <ValueText>{formatNumber(summary.missingValues)}</ValueText>
//                                 <LabelText>Missing Values</LabelText>
//                             </DashboardCard>
//                         </Grid>
//                     </Grid>

//                     {/* Radial Gauges with Sparklines */}
//                     <Typography variant="h6" sx={{ mb: 1, color: theme.palette.text.secondary }}>
//                         Data Quality Scores
//                     </Typography>
//                     <Grid container spacing={2} sx={{ mb: 3 }}>
//                         {/* The RadialGauge component itself has a fixed width. If you find these too wide, you might need to adjust their internal 'width' property or the Grid 'xs' props */}
//                         <Grid item xs={12} sm={6} md={4} display="flex" justifyContent="center">
//                             <RadialGauge
//                                 value={parseFloat(totalScorePercentage)} // Convert to float
//                                 title="Total Score"
//                                 subValueLabel="Profiling" // Example label
//                                 subValue={profilingScore} // Example sub-score value
//                                 trendData={totalScoreTrend}
//                                 gaugeColor={theme.palette.warning.main} // Yellow color for gauge
//                             />
//                         </Grid>
//                         <Grid item xs={12} sm={6} md={4} display="flex" justifyContent="center">
//                             <RadialGauge
//                                 value={parseFloat(cdeScorePercentage)} // Convert to float
//                                 title="CDE Score"
//                                 subValueLabel="Completeness" // Example label
//                                 subValue="98.1" // Example sub-score value
//                                 trendData={cdeScoreTrend}
//                                 gaugeColor={theme.palette.success.main} // Greenish color for CDE
//                             />
//                         </Grid>
//                         {/* Add more gauges as needed, e.g., for Distinct Values if you want to represent it as a score */}
//                         {/* Example for a "Distinctness Score" (if you want to represent your previous distinct values graph as a score) */}
//                         <Grid item xs={12} sm={6} md={4} display="flex" justifyContent="center">
//                             <RadialGauge
//                                 value={summary.distinctValuesPercentage || 0} // Assuming summary.distinctValuesPercentage exists (0-100)
//                                 title="Distinctness Score"
//                                 subValueLabel="Uniqueness"
//                                 subValue={formatNumber(summary.distinctValues)} // Show actual distinct count
//                                 trendData={profilingScoreTrend} // Reuse an existing trend or create a new one
//                                 gaugeColor={theme.palette.info.main} // Blueish color
//                             />
//                         </Grid>
//                     </Grid>


//                     {/* Recent Profile Runs Table */}
//                     <Typography variant="h6" sx={{ mt: 4, mb: 1, color: theme.palette.text.secondary }}>
//                         Recent Profile Runs
//                     </Typography>
//                     <TableContainer component={Paper} sx={{ boxShadow: theme.shadows[2], border: `1px solid ${theme.palette.divider}`, overflowX: 'auto' }}> {/* ADDED overflowX: 'auto' HERE */}
//                         <Table size="small">
//                             <TableHead sx={{ bgcolor: theme.palette.action.hover }}>
//                                 <TableRow>
//                                     <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Profiling Time</TableCell>
//                                     <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Status</TableCell>
//                                     <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Tables</TableCell>
//                                 </TableRow>
//                             </TableHead>
//                             <TableBody>
//                                 {recentRuns.length > 0 ? (
//                                     recentRuns.map((run) => (
//                                         <TableRow
//                                             key={run.profiling_id}
//                                             onClick={() => handleRecentRunClick(run.profiling_id)}
//                                             sx={{
//                                                 '&:hover': {
//                                                     backgroundColor: theme.palette.action.selected,
//                                                     cursor: 'pointer',
//                                                 },
//                                                 transition: 'background-color 0.2s ease-in-out',
//                                             }}
//                                         >
//                                             <TableCell>{format(new Date(run.profilingTime), 'MMM dd, yyyy, h:mm a')}</TableCell>
//                                             <TableCell>
//                                                 <Typography
//                                                     variant="body2"
//                                                     sx={{
//                                                         color: run.status === 'Completed' ? theme.palette.success.main :
//                                                             run.status === 'Failed' ? theme.palette.error.main :
//                                                                 theme.palette.warning.main,
//                                                         fontWeight: 'bold',
//                                                     }}
//                                                 >
//                                                     {run.status}
//                                                 </Typography>
//                                             </TableCell>
//                                             <TableCell>{run.tables}</TableCell>
//                                         </TableRow>
//                                     ))
//                                 ) : (
//                                     <TableRow>
//                                         <TableCell colSpan={3} sx={{ textAlign: 'center', py: 3, color: theme.palette.text.secondary }}>
//                                             No recent profile runs found.
//                                         </TableCell>
//                                     </TableRow>
//                                 )}
//                             </TableBody>
//                         </Table>
//                     </TableContainer>
//                 </Paper>
//             </Grid>

//             {/* Right Column: Profile Run Details */}
//             <Grid item xs={16} md={8}>
//                 <Paper sx={{ p: 3, height: '100%', bgcolor: theme.palette.background.paper, boxShadow: theme.shadows[4] }}>
//                     <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: theme.palette.text.primary }}>
//                         Profile Run Details
//                     </Typography>

//                     {selectedRunId ? (
//                         <>
//                             {/* Run Summary */}
//                             <Box sx={{ mb: 2 }}>
//                                 <Typography variant="body1" sx={{ color: theme.palette.text.secondary, mb: 0.5 }}>
//                                     <Typography component="span" sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Profiling Time:</Typography>{' '}
//                                     {tableDetails?.profilingTime ? format(new Date(tableDetails.profilingTime), 'MMM dd, yyyy, h:mm a') : 'Loading...'}
//                                 </Typography>
//                                 <Typography variant="body1" sx={{ color: theme.palette.text.secondary, mb: 0.5 }}>
//                                     <Typography component="span" sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Status:</Typography>{' '}
//                                     <Typography
//                                         component="span"
//                                         sx={{
//                                             color: tableDetails?.status === 'Completed' ? theme.palette.success.main :
//                                                 tableDetails?.status === 'Failed' ? theme.palette.error.main :
//                                                     theme.palette.warning.main,
//                                             fontWeight: 'bold',
//                                         }}
//                                     >
//                                         {tableDetails?.status || 'Loading...'}
//                                     </Typography>
//                                 </Typography>
//                                 <FormControl fullWidth size="small" sx={{ mt: 2 }}>
//                                     <InputLabel id="table-select-label">Table</InputLabel>
//                                     <Select
//                                         labelId="table-select-label"
//                                         id="table-select"
//                                         value={selectedTableName}
//                                         label="Table"
//                                         onChange={(e) => setSelectedTableName(e.target.value)}
//                                         disabled={loadingTableDetails || tableNames.length === 0}
//                                     >
//                                         {tableNames.length > 0 ? (
//                                             tableNames.map((table) => (
//                                                 <MenuItem key={table.tableName} value={table.tableName}>
//                                                     {table.tableName}
//                                                 </MenuItem>
//                                             ))
//                                         ) : (
//                                             <MenuItem value="" disabled>No tables found for this run</MenuItem>
//                                         )}
//                                     </Select>
//                                 </FormControl>
//                             </Box>

//                             {/* Column Data Types (Placeholder for future image) */}
//                             <Box sx={{ mb: 3, p: 2, border: `1px dashed ${theme.palette.divider}`, borderRadius: theme.shape.borderRadius, minHeight: 120, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.palette.text.disabled }}>
//                                 <Typography variant="body2">Add new API, sq score over time - history laga try, refer to the last 3rd page of notepad - points written </Typography>
//                             </Box>

//                             {/* Data Distribution Table */}
//                             <Typography variant="h6" sx={{ mb: 1, color: theme.palette.text.secondary }}>
//                                 Data Distribution
//                             </Typography>
//                             {loadingTableDetails ? (
//                                 <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 150 }}>
//                                     <CircularProgress size={30} />
//                                     <Typography sx={{ ml: 2 }}>Loading table details...</Typography>
//                                 </Box>
//                             ) : errorTableDetails ? (
//                                 <Typography color="error">Error: {errorTableDetails.message}</Typography>
//                             ) : tableDetails && tableDetails.dataDistribution.length > 0 ? (
//                                 <TableContainer component={Paper} sx={{ boxShadow: theme.shadows[2], border: `1px solid ${theme.palette.divider}`, overflowX: 'auto' }}> {/* ADDED overflowX: 'auto' HERE */}
//                                     <Table size="small">
//                                         <TableHead sx={{ bgcolor: theme.palette.action.hover }}>
//                                             <TableRow>
//                                                 <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Column</TableCell>
//                                                 <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Data Type</TableCell>
//                                                 <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Distinct Values</TableCell>
//                                                 <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Missing Values</TableCell>
//                                                 <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Empty Values</TableCell>
//                                             </TableRow>
//                                         </TableHead>
//                                         <TableBody>
//                                             {tableDetails.dataDistribution.map((row, index) => (
//                                                 <TableRow key={index}>
//                                                     <TableCell>{row.column}</TableCell>
//                                                     <TableCell>{row.dataType}</TableCell>
//                                                     <TableCell>{formatNumber(row.distinctValues)}</TableCell>
//                                                     <TableCell>{row.missingValues}</TableCell>
//                                                     <TableCell>{row.emptyValues}</TableCell>
//                                                 </TableRow>
//                                             ))}
//                                         </TableBody>
//                                     </Table>
//                                 </TableContainer>
//                             ) : (
//                                 <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
//                                     No data distribution details available for this table.
//                                 </Typography>
//                             )}
//                         </>
//                     ) : (
//                         <Box sx={{ textAlign: 'center', py: 5, color: theme.palette.text.secondary }}>
//                             <Typography variant="h6">Select a recent profiling run to view details.</Typography>
//                         </Box>
//                     )}
//                 </Paper>
//             </Grid>
//         </Grid>
//     );
// };

// export default ProfileRunDisplay;