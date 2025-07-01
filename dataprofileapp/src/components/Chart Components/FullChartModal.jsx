import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Typography,
    Box,
    Grid,
    useTheme,
    Divider
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import {
    BarChart, Bar, ResponsiveContainer, Tooltip as RechartsTooltip, XAxis, YAxis,
    PieChart, Pie, Cell, Legend
} from 'recharts'; // Import Recharts components

// Define the item type for drag and drop (needed for chart components rendered inside)
const ItemTypes = {
    CHART: 'chart',
};

// Define COLORS again or pass as a prop if needed
const getColors = (theme) => [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.error.main,
    theme.palette.warning.main,
    theme.palette.info.main,
    theme.palette.success.main,
    theme.palette.grey[500]
];


const FullChartModal = ({ open, onClose, chartType, chartData, displayedRunSummary, displayedProfileResults, COLORS }) => {
    const theme = useTheme();
    const colors = COLORS || getColors(theme); // Use passed colors or generate

    // Helper function to calculate percentage safely (needed for bar chart data)
    const calculatePercentage = (numerator, denominator) => {
        if (denominator === null || denominator === undefined || denominator === 0) {
            return 0; // Avoid division by zero
        }
        return (numerator / denominator) * 100;
    };

    // Data transformation specific to chart types if needed for full view
    const getChartData = (type, runSummary, profileResults) => {
        switch (type) {
            case 'anomaly':
                return [
                    { name: 'Anomaly Rows', value: runSummary?.anomaly_ct || 0 },
                    { name: 'Anomaly Tables', value: runSummary?.anomaly_table_ct || 0 },
                    { name: 'Anomaly Columns', value: runSummary?.anomaly_column_ct || 0 },
                ];
            case 'completeness':
                 return runSummary?.dq_total_data_points !== undefined && runSummary?.dq_total_data_points !== null && runSummary?.dq_total_data_points > 0
                    ? [
                        {
                            name: 'Complete',
                            value: runSummary.dq_total_data_points - (runSummary.dq_affected_data_points || 0),
                        },
                        {
                            name: 'Affected',
                            value: runSummary.dq_affected_data_points || 0,
                        },
                    ]
                    : [];
             case 'column_type':
                return Object.entries(
                    profileResults.reduce((acc, cur) => {
                        if (cur.general_type) {
                            acc[cur.general_type] = (acc[cur.general_type] || 0) + 1;
                        }
                        return acc;
                    }, {})
                ).map(([type, count]) => ({ name: type, value: count }));
            case 'pii_flag':
                 return Object.entries(
                    profileResults.reduce((acc, cur) => {
                        const flag = cur.pii_flag && cur.pii_flag.trim() !== '' ? cur.pii_flag : 'Unknown';
                        acc[flag] = (acc[flag] || 0) + 1;
                        return acc;
                    }, {})
                ).map(([flag, count]) => ({ name: flag, value: count }));
            case 'top_null':
                return [...profileResults]
                    .filter(p => p.null_value_ct !== null && p.record_ct !== null && p.record_ct > 0)
                    .map(p => ({
                        name: `${p.table_name}.${p.column_name}`,
                        percent: calculatePercentage(p.null_value_ct, p.record_ct),
                    }))
                    .sort((a, b) => b.percent - a.percent)
                    .slice(0, 10); // Show more in full view if desired (e.g., top 10)
            case 'top_cardinality':
                 return [...profileResults]
                    .filter(p => p.distinct_value_ct !== null && p.value_ct !== null && p.value_ct > 0)
                    .map(p => ({
                        name: `${p.table_name}.${p.column_name}`,
                        percent: calculatePercentage(p.distinct_value_ct, p.value_ct),
                    }))
                    .sort((a, b) => b.percent - a.percent)
                    .slice(0, 10); // Show more in full view if desired (e.g., top 10)
            default:
                return [];
        }
    };

    const data = getChartData(chartType, displayedRunSummary, displayedProfileResults);

    const renderChart = (type, data) => {
        switch (type) {
            case 'anomaly':
                return (
                    <ResponsiveContainer width="100%" height={400}> {/* Larger height for full view */}
                        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <XAxis dataKey="name" stroke={'#fff'} />
                            <YAxis stroke={'#fff'} />
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, color:'#fff', border: 'none' }} />
                            <Bar dataKey="value" fill={theme.palette.primary.main} />
                        </BarChart>
                    </ResponsiveContainer>
                );
            case 'completeness':
                return (
                     <ResponsiveContainer width="100%" height={400}> {/* Larger height for full view */}
                        <PieChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <Pie
                                data={data}
                                dataKey="value"
                                nameKey="name"
                                outerRadius={150} // Larger radius
                                label={(entry) => `${entry.name}: ${entry.value}`}
                                labelLine={false}
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                             <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, color:'#fff', border: 'none' }} />
                             <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );
             case 'column_type':
                return (
                     <ResponsiveContainer width="100%" height={400}> {/* Larger height for full view */}
                        <PieChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <Pie
                                data={data}
                                dataKey="value"
                                nameKey="name"
                                outerRadius={150} // Larger radius
                                label={(entry) => `${entry.name}: ${entry.value}`}
                                labelLine={false}
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`type-cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, color:'#fff', border: 'none' }} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );
            case 'pii_flag':
                 return (
                     <ResponsiveContainer width="100%" height={400}> {/* Larger height for full view */}
                        <PieChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <Pie
                                data={data}
                                dataKey="value"
                                nameKey="name"
                                outerRadius={150} // Larger radius
                                label={(entry) => `${entry.name}: ${entry.value}`}
                                labelLine={false}
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`pii-cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, color:'#fff', border: 'none' }} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );
            case 'top_null':
                return (
                    <ResponsiveContainer width="100%" height={500}> {/* Adjust height for potentially more bars */}
                        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 120 }}> {/* Increased bottom margin */}
                            <XAxis dataKey="name" angle={-45} textAnchor="end" height={120} interval={0} stroke={'#fff'} /> {/* Increased height */}
                            <YAxis stroke={'#fff'} label={{ value: 'Null %', angle: -90, position: 'insideLeft', fill: '#fff' }} />
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, color:'#fff', border: 'none' }} />
                            <Bar dataKey="percent" fill={theme.palette.error.main} />
                        </BarChart>
                    </ResponsiveContainer>
                );
            case 'top_cardinality':
                 return (
                    <ResponsiveContainer width="100%" height={500}> {/* Adjust height for potentially more bars */}
                        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 120 }}> {/* Increased bottom margin */}
                            <XAxis dataKey="name" angle={-45} textAnchor="end" height={120} interval={0} stroke={'#fff'} /> {/* Increased height */}
                            <YAxis stroke={'#fff'} label={{ value: 'Cardinality %', angle: -90, position: 'insideLeft', fill: '#fff' }} />
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, color:'#fff', border: 'none' }} />
                            <Bar dataKey="percent" fill={theme.palette.info.main} />
                        </BarChart>
                    </ResponsiveContainer>
                );
            default:
                return <Typography>Select a chart to view.</Typography>;
        }
    };

    const getChartTitle = (type) => {
        switch (type) {
            case 'anomaly': return 'Anomaly Summary';
            case 'completeness': return 'Data Completeness';
            case 'column_type': return 'Column Type Distribution';
            case 'pii_flag': return 'PII Flag Distribution';
            case 'top_null': return `Top 10 Columns by Null %`; // Updated title for potential top 10
            case 'top_cardinality': return `Top 10 Columns by Cardinality %`; // Updated title for potential top 10
            default: return 'Chart View';
        }
    };


    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="md" // Use md or lg for a larger view
            PaperProps={{
                sx: {
                    backgroundColor: '#1e1e1e',
                    color: theme.palette.text.primary,
                    borderRadius: theme.shape.borderRadius * 2,
                }
            }}
        >
            <DialogTitle sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: theme.spacing(2, 3),
                borderBottom: `1px solid ${'#fff'}`,
            }}>
                <Typography variant="h6" component="div" color='#fff'>
                    {getChartTitle(chartType)}
                </Typography>
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={{ color: '#fff' }}
                >
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent dividers sx={{ padding: theme.spacing(3) }}>
               
                {renderChart(chartType, data)}
            </DialogContent>
        </Dialog>
    );
};

export default FullChartModal;
