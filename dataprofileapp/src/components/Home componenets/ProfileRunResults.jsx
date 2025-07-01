import React, { useState, useEffect, useCallback } from 'react';
import {
    Paper,
    Typography,
    Grid,
    Box,
    CircularProgress,
    Card,
    useTheme,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';
import { styled } from '@mui/system';
import { format } from 'date-fns';

// Assuming these API functions exist in your project
import { getDashboardOverview } from '../../api/dbapi';

// Helper components and functions (consider moving these to a shared 'utils' or 'components/shared' directory)
const DashboardCard = styled(Card)(({ theme }) => ({
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing(2),
    textAlign: 'center',
    minHeight: 120,
    backgroundColor: theme.palette.mode === 'light' ? '#e3f2fd' : '#263238',
    color: theme.palette.mode === 'light' ? theme.palette.primary.dark : theme.palette.primary.light,
    borderRadius: theme.shape.borderRadius,
    boxShadow: theme.shadows[3],
}));

const ValueText = styled(Typography)(({ theme }) => ({
    fontSize: '2.5rem',
    fontWeight: 'bold',
    lineHeight: 1,
    color: theme.palette.mode === 'light' ? theme.palette.primary.main : theme.palette.primary.light,
}));

const LabelText = styled(Typography)(({ theme }) => ({
    fontSize: '0.9rem',
    color: theme.palette.text.secondary,
    marginTop: theme.spacing(0.5),
}));

const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
};

// const Sparkline = ({ data, color, nullColor, width = 100, height = 30 }) => {
//     if (!data || data.length < 2) {
//         return <Box sx={{ width, height, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', color: nullColor }}>Not enough data</Box>;
//     }

//     const maxDataValue = Math.max(...data);
//     const minDataValue = Math.min(...data);

//     const points = data.map((d, i) => {
//         const x = (i / (data.length - 1)) * width;
//         const y = height - ((d - minDataValue) / (maxDataValue - minDataValue + 0.001)) * height;
//         return `${x},${y}`;
//     }).join(' ');

//     const isDownwardTrend = data[data.length - 1] < data[0];
//     const trendColor = isDownwardTrend ? 'purple' : color;

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

const RadialGauge = ({ value, title, subValueLabel, gaugeColor = '#ffc107' }) => {
    const theme = useTheme();
    const normalizedValue = Math.min(100, Math.max(0, value));

    return (
        <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            width: 160,
            height: 180,
            p: 2,
            borderRadius: theme.shape.borderRadius,
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.shadows[3],
        }}>
            <Box sx={{ position: 'relative', width: 100, height: 100, mb: 1 }}>
                <CircularProgress
                    variant="determinate"
                    value={100}
                    size={100}
                    thickness={4}
                    sx={{
                        color: theme.palette.action.disabledBackground,
                        position: 'absolute',
                        left: 0,
                        top: 0,
                    }}
                />
                <CircularProgress
                    variant="determinate"
                    value={normalizedValue}
                    size={100}
                    thickness={4}
                    sx={{
                        color: gaugeColor,
                        position: 'absolute',
                        left: 0,
                        top: 0,
                        transform: 'rotate(-90deg)',
                        transformOrigin: 'center center',
                    }}
                />
                <Box
                    sx={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>
                        {`${Math.round(value)}%`}
                    </Typography>
                </Box>
            </Box>
            <Typography variant="subtitle2" sx={{ color: theme.palette.text.secondary, mt: 0.5 }}>
                {title}
            </Typography>

            <Box sx={{ mt: 1 }}>
                {/* <Sparkline
                    // data={trendData}
                    color={sparklineDistinctColor}
                    nullColor={sparklineNullColor}
                    width={120}
                    height={30}
                /> */}
            </Box>

            {subValueLabel && (
                <Typography variant="caption" sx={{ color: theme.palette.text.primary, mt: 0.5 }}>
                    <Typography component="span" sx={{ fontWeight: 'bold' }}>{subValueLabel}:</Typography> {subValue}
                </Typography>
            )}
        </Box>
    );
};


const ProfileRunResults = ({ onSelectRun, selectedRunId }) => {
    const theme = useTheme();
    const [dashboardData, setDashboardData] = useState(null);
    const [loadingDashboard, setLoadingDashboard] = useState(true);
    const [errorDashboard, setErrorDashboard] = useState(null);

    // Mock trend data for demonstration (ideally fetched from backend)
    const [totalScoreTrend] = useState([85, 88, 90, 87, 92, 95, 93, 91, 89, 86]);
    const [cdeScoreTrend] = useState([70, 75, 72, 78, 80, 82, 79, 76, 73, 70]);
    const [profilingScoreTrend] = useState([90, 92, 91, 93, 95, 94, 96, 97, 98, 99]);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoadingDashboard(true);
                const data = await getDashboardOverview();
                setDashboardData(data);
                setErrorDashboard(null);
                if (data.recentRuns && data.recentRuns.length > 0) {
                    onSelectRun(data.recentRuns[0].profiling_id); // Automatically select the first run
                }
            } catch (err) {
                setErrorDashboard(err);
                console.error('Error fetching dashboard overview:', err);
            } finally {
                setLoadingDashboard(false);
            }
        };
        fetchDashboardData();
    }, [onSelectRun]); // Depend on onSelectRun to ensure initial selection

    const handleRecentRunClick = useCallback((runId) => {
        onSelectRun(runId);
    }, [onSelectRun]);

    if (loadingDashboard) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', minHeight: 400 }}>
                <CircularProgress />
                <Typography variant="h6" sx={{ ml: 2 }}>Loading Dashboard Data...</Typography>
            </Box>
        );
    }

    if (errorDashboard) {
        return (
            <Paper sx={{ p: 3, my: 3, bgcolor: theme.palette.error.light, height: '100%', minHeight: 400 }}>
                <Typography color="error">Error loading dashboard: {errorDashboard.message}</Typography>
                <Typography variant="body2" color="text.secondary">Please check your backend connection and API.</Typography>
            </Paper>
        );
    }

    const { summary, recentRuns } = dashboardData;
    const profilingScore = summary.profilingScore || 0;
    const totalScorePercentage = summary.dqScore ? (summary.dqScore * 100).toFixed(1) : 'N/A';
    const cdeScorePercentage = summary.completenessPercentage || 'N/A';

    return (
        <Paper sx={{ p: 3, height: '100%', bgcolor: theme.palette.background.paper, boxShadow: theme.shadows[4] }}>
            <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: theme.palette.text.primary }}>
                Profile Run Results
            </Typography>

            <Typography variant="h6" sx={{ mb: 2, color: theme.palette.text.secondary }}>
                Profile Run Dashboard
            </Typography>

            {/* Dashboard Cards */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} sm={3}>
                    <DashboardCard>
                        <ValueText>{summary.tables}</ValueText>
                        <LabelText>Tables</LabelText>
                    </DashboardCard>
                </Grid>
                <Grid item xs={6} sm={3}>
                    <DashboardCard>
                        <ValueText>{summary.columns}</ValueText>
                        <LabelText>Columns</LabelText>
                    </DashboardCard>
                </Grid>
                <Grid item xs={6} sm={3}>
                    <DashboardCard>
                        <ValueText>{formatNumber(summary.rowCount)}</ValueText>
                        <LabelText>Row Count</LabelText>
                    </DashboardCard>
                </Grid>
                <Grid item xs={6} sm={3}>
                    <DashboardCard>
                        <ValueText>{formatNumber(summary.missingValues)}</ValueText>
                        <LabelText>Missing Values</LabelText>
                    </DashboardCard>
                </Grid>
            </Grid>

            {/* Radial Gauges with Sparklines */}
            <Typography variant="h6" sx={{ mb: 1, color: theme.palette.text.secondary }}>
                Data Quality Scores
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={4} display="flex" justifyContent="center">
                    <RadialGauge
                        value={parseFloat(totalScorePercentage)}
                        title="Data Quality Score"
                        // subValueLabel="Profiling"
                        // subValue={profilingScore}
                        // trendData={totalScoreTrend}
                        // gaugeColor={theme.palette.warning.main}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4} display="flex" justifyContent="center">
                    <RadialGauge
                        value={parseFloat(cdeScorePercentage)}
                        title="CDE Score"
                        // subValueLabel="Completeness"
                        // subValue="98.1"
                        // trendData={cdeScoreTrend}
                        gaugeColor={theme.palette.success.main}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={4} display="flex" justifyContent="center">
                    <RadialGauge
                        value={summary.distinctValuesPercentage || 0}
                        title="Distinctness Score"
                        // subValueLabel="Uniqueness"
                        // subValue={formatNumber(summary.distinctValues)}
                        // trendData={profilingScoreTrend}
                        // gaugeColor={theme.palette.info.main}
                    />
                </Grid>
            </Grid>

            {/* Recent Profile Runs Table */}
            <Typography variant="h6" sx={{ mt: 4, mb: 1, color: theme.palette.text.secondary }}>
                Recent Profile Runs
            </Typography>
            <TableContainer component={Paper} sx={{ boxShadow: theme.shadows[2], border: `1px solid ${theme.palette.divider}`, overflowX: 'auto' }}>
                <Table size="small">
                    <TableHead sx={{ bgcolor: theme.palette.action.hover }}>
                        <TableRow>
                            <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Profiling Time</TableCell>
                            <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Status</TableCell>
                            <TableCell sx={{ fontWeight: 'bold', color: theme.palette.text.primary }}>Tables</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {recentRuns.length > 0 ? (
                            recentRuns.map((run) => (
                                <TableRow
                                    key={run.profiling_id}
                                    onClick={() => handleRecentRunClick(run.profiling_id)}
                                    sx={{
                                        '&:hover': {
                                            backgroundColor: theme.palette.action.selected,
                                            cursor: 'pointer',
                                        },
                                        transition: 'background-color 0.2s ease-in-out',
                                        backgroundColor: selectedRunId === run.profiling_id ? theme.palette.action.selected : 'inherit',
                                    }}
                                >
                                    <TableCell>{format(new Date(run.profilingTime), 'MMM dd, yyyy, h:mm a')}</TableCell>
                                    <TableCell>
                                        <Typography
                                            variant="body2"
                                            sx={{
                                                color: run.status === 'Completed' ? theme.palette.success.main :
                                                    run.status === 'Failed' ? theme.palette.error.main :
                                                        theme.palette.warning.main,
                                                fontWeight: 'bold',
                                            }}
                                        >
                                            {run.status}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>{run.tables}</TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={3} sx={{ textAlign: 'center', py: 3, color: theme.palette.text.secondary }}>
                                    No recent profile runs found.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
};

export default ProfileRunResults;