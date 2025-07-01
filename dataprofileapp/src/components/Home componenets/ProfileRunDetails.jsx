import React, { useState, useEffect } from 'react';
import {
    Paper,
    Typography,
    Box,
    CircularProgress,
    useTheme,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    List, // For displaying tables from a run
    ListItem,
    ListItemText,
    Grid // For layout if needed within this component
} from '@mui/material';
import { format } from 'date-fns';

// Import Recharts components
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

// Assuming this API function exists in your project
import { getProfilingTableDetails, getTableNamesForProfilingRun } from '../../api/dbapi';

const ProfileRunDetails = ({ selectedRunId, selectedTableName, onSelectTableName }) => {
    const theme = useTheme();
    const [tableNames, setTableNames] = useState([]);
    const [loadingTableNames, setLoadingTableNames] = useState(false);
    const [errorTableNames, setErrorTableNames] = useState(null);

    const [tableDetails, setTableDetails] = useState(null);
    const [loadingTableDetails, setLoadingTableDetails] = useState(false);
    const [errorTableDetails, setErrorTableDetails] = useState(null);

    // Effect to fetch table names when a run is selected
    useEffect(() => {
        const fetchTableNames = async () => {
            if (!selectedRunId) {
                setTableNames([]);
                setLoadingTableNames(false);
                return;
            }

            try {
                setLoadingTableNames(true);
                const data = await getTableNamesForProfilingRun(selectedRunId);
                setTableNames(data);
                setErrorTableNames(null);

                if (data.length > 0) {
                    const isSelectedTableInNewRun = data.some(item => item.tableName === selectedTableName);
                    if (!selectedTableName || !isSelectedTableInNewRun) {
                        onSelectTableName(data[0].tableName);
                    }
                } else {
                    onSelectTableName(null);
                }
            } catch (err) {
                setErrorTableNames(err);
                console.error(`Error fetching table names for run ${selectedRunId}:`, err);
                setTableNames([]);
                onSelectTableName(null);
            } finally {
                setLoadingTableNames(false);
            }
        };

        fetchTableNames();
    }, [selectedRunId, onSelectTableName, selectedTableName]);

    // Effect to fetch details for a specific table when selected
    useEffect(() => {
        const fetchTableDetails = async () => {
            if (!selectedRunId || !selectedTableName) {
                setTableDetails(null);
                setLoadingTableDetails(false);
                return;
            }

            try {
                setLoadingTableDetails(true);
                const data = await getProfilingTableDetails(selectedRunId, selectedTableName);
                setTableDetails(data);
                setErrorTableDetails(null);
            } catch (err) {
                setErrorTableDetails(err);
                console.error(`Error fetching details for table '${selectedTableName}' in run ${selectedRunId}:`, err);
                setTableDetails(null);
            } finally {
                setLoadingTableDetails(false);
            }
        };

        fetchTableDetails();
    }, [selectedRunId, selectedTableName]);


    // Prepare data for the DQ score trend chart
    const dqScoreChartData = (tableDetails?.tableDQScoreHistory || [])
        .filter(item => item.dqScore !== null && item.dqScore !== undefined)
        .map(item => ({
            // Store the original profilingTime string, and convert DQ Score
            profilingTime: item.profilingTime, // Keep the original date string here
            'DQ Score': item.dqScore ? parseFloat((item.dqScore * 100).toFixed(1)) : 0
        }))
        // Ensure data is sorted by time
        // Create Date objects for sorting, but keep the string for the chart data
        .sort((a, b) => new Date(a.profilingTime).getTime() - new Date(b.profilingTime).getTime());


    return (
        <Paper sx={{ p: 3, height: '100%', bgcolor: theme.palette.background.paper, boxShadow: theme.shadows[4], display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: theme.palette.text.primary }}>
                Profile Run Details
            </Typography>

            {!selectedRunId && (
                <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <Typography variant="h6" color="text.secondary">Select a run from the left panel to see details.</Typography>
                </Box>
            )}

            {selectedRunId && (
                <Grid container spacing={2} sx={{ flexGrow: 1 }}>
                    {/* Left Column: List of Tables in the Run */}
                    <Grid item xs={12} md={4}>
                        <Typography variant="h6" sx={{ mb: 1, color: theme.palette.text.secondary }}>
                            Tables in Run
                        </Typography>
                        {loadingTableNames ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                <CircularProgress size={24} />
                            </Box>
                        ) : errorTableNames ? (
                            <Typography color="error" variant="body2">Error loading tables: {errorTableNames.message}</Typography>
                        ) : tableNames.length > 0 ? (
                            
                            <List dense sx={{ maxHeight: 300, overflow: 'auto', border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                                {tableNames.map((item) => (
                                    <ListItem
                                        component="dropdown"
                                        key={item.tableName}
                                        onClick={() => onSelectTableName(item.tableName)}
                                        sx={{
                                            backgroundColor: selectedTableName === item.tableName ? theme.palette.action.selected : 'inherit',
                                            '&:hover': {
                                                backgroundColor: theme.palette.action.hover,
                                            },
                                        }}
                                    >
                                        <ListItemText primary={item.tableName} />
                                    </ListItem>
                                ))}
                            </List>
                        ) : (
                            <Typography variant="body2" color="text.secondary">No tables found for this run.</Typography>
                        )}
                    </Grid>

                    {/* Right Column: Details for Selected Table */}
                    <Grid item xs={12} md={8}>
                        {loadingTableDetails ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', minHeight: 300 }}>
                                <CircularProgress />
                                <Typography variant="h6" sx={{ ml: 2 }}>Loading Table Details...</Typography>
                            </Box>
                        ) : errorTableDetails ? (
                            <Typography color="error" variant="body2">Error loading table details: {errorTableDetails.message}</Typography>
                        ) : selectedTableName && tableDetails ? (
                            <Box>
                                <Typography variant="h6" sx={{ mb: 1, color: theme.palette.text.secondary }}>
                                    Details for: {tableDetails.tableName}
                                </Typography>
                                <Typography variant="subtitle2" sx={{ mb: 1, color: theme.palette.text.secondary }}>
                                    Last Profiled: {format(new Date(tableDetails.profilingTime), 'MMM dd,yyyy, h:mm a')} | Status: {tableDetails.status}
                                </Typography>

                                {/* DQ Score Trend Chart - This is the "space that was left" */}
                                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: theme.palette.text.secondary }}>
                                    DQ Score Trend Over Time
                                </Typography>
                                <Box sx={{ height: 250, width: '100%', mb: 3, border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                                    {dqScoreChartData.length > 1 ? (
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart
                                                data={dqScoreChartData}
                                                margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
                                            >
                                                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                                                <XAxis
                                                    dataKey="profilingTime" // Use the original profilingTime string as dataKey
                                                    tickFormatter={(tick) => format(new Date(tick), 'MMM dd\nh:mm a')} // Format it only here for display
                                                    angle={-30}
                                                    textAnchor="end"
                                                    height={60}
                                                    stroke={theme.palette.text.secondary}
                                                    tick={{ fontSize: 10 }}
                                                />
                                                <YAxis
                                                    domain={[0, 100]}
                                                    tickFormatter={(tick) => `${tick}%`}
                                                    stroke={theme.palette.text.secondary}
                                                    tick={{ fontSize: 10 }}
                                                />
                                                <Tooltip
                                                    formatter={(value, name) => [`${value.toFixed(1)}%`, name]}
                                                    labelFormatter={(label) => `Time: ${format(new Date(label), 'MMM dd, yyyy, h:mm a')}`} // Format label for tooltip
                                                    contentStyle={{
                                                        backgroundColor: theme.palette.background.paper,
                                                        border: `1px solid ${theme.palette.divider}`,
                                                        color: theme.palette.text.primary
                                                    }}
                                                />
                                                <Legend />
                                                <Line
                                                    type="monotone"
                                                    dataKey="DQ Score"
                                                    stroke={theme.palette.primary.main}
                                                    strokeWidth={2}
                                                    dot={{ r: 3 }}
                                                    activeDot={{ r: 5 }}
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', p: 2 }}>
                                            <Typography variant="body2" color="text.secondary" textAlign="center">
                                                Not enough historical data to show DQ score trend for this table.
                                            </Typography>
                                        </Box>
                                    )}
                                </Box>

                                {/* Column Data Types */}
                                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: theme.palette.text.secondary }}>
                                    Column Data Types
                                </Typography>
                                <TableContainer component={Paper} sx={{ mb: 3, boxShadow: theme.shadows[1], border: `1px solid ${theme.palette.divider}`, maxHeight: 200, overflowY: 'auto' }}>
                                    <Table size="small" stickyHeader>
                                        <TableHead sx={{ bgcolor: theme.palette.action.hover }}>
                                            <TableRow>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Column Name</TableCell>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Column Type</TableCell>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>General Type</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {tableDetails.columnDataTypes.length > 0 ? (
                                                tableDetails.columnDataTypes.map((col, index) => (
                                                    <TableRow key={index}>
                                                        <TableCell>{col.columnName}</TableCell>
                                                        <TableCell>{col.columnType}</TableCell>
                                                        <TableCell>{col.generalType}</TableCell>
                                                    </TableRow>
                                                ))
                                            ) : (
                                                <TableRow>
                                                    <TableCell colSpan={3} sx={{ textAlign: 'center', py: 2, color: theme.palette.text.secondary }}>
                                                        No column data types found.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>

                                {/* Data Distribution */}
                                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: theme.palette.text.secondary }}>
                                    Data Distribution
                                </Typography>
                                <TableContainer component={Paper} sx={{ boxShadow: theme.shadows[1], border: `1px solid ${theme.palette.divider}`, maxHeight: 200, overflowY: 'auto' }}>
                                    <Table size="small" stickyHeader>
                                        <TableHead sx={{ bgcolor: theme.palette.action.hover }}>
                                            <TableRow>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Column</TableCell>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Data Type</TableCell>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Distinct Values</TableCell>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Missing Values</TableCell>
                                                <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Empty Values</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {tableDetails.dataDistribution.length > 0 ? (
                                                tableDetails.dataDistribution.map((dist, index) => (
                                                    <TableRow key={index}>
                                                        <TableCell>{dist.column}</TableCell>
                                                        <TableCell>{dist.dataType}</TableCell>
                                                        <TableCell>{dist.distinctValues}</TableCell>
                                                        <TableCell>{dist.missingValues}</TableCell>
                                                        <TableCell>{dist.emptyValues}</TableCell>
                                                    </TableRow>
                                                ))
                                            ) : (
                                                <TableRow>
                                                    <TableCell colSpan={5} sx={{ textAlign: 'center', py: 2, color: theme.palette.text.secondary }}>
                                                        No data distribution details found.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Box>
                        ) : (
                            <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                                <Typography variant="h6" color="text.secondary">Select a table from the list.</Typography>
                            </Box>
                        )}
                    </Grid>
                </Grid>
            )}
        </Paper>
    );
};

export default ProfileRunDetails;