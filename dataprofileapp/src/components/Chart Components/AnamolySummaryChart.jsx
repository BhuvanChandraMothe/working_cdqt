import React, { useRef, useState } from 'react';
import { Box, Grid,Paper, Typography, Popover, useTheme } from '@mui/material';
import { BarChart, Bar, ResponsiveContainer, Tooltip as RechartsTooltip, XAxis, YAxis } from 'recharts';
import { useDrag, useDrop } from 'react-dnd'; // Import drag and drop hooks

// Define the item type for drag and drop
const ItemTypes = {
    CHART: 'chart',
};

const AnomalySummaryChart = ({ id, index, displayedRunSummary, onChartClick, moveCard }) => {
    const theme = useTheme();
    const ref = useRef(null); // Ref for the draggable element

    // State for Popover
    const [popoverAnchorEl, setPopoverAnchorEl] = useState(null);

    // Data transformation for this specific chart
    const anomalyData = [
        { name: 'Anomaly Rows', value: displayedRunSummary?.anomaly_ct || 0 },
        { name: 'Anomaly Tables', value: displayedRunSummary?.anomaly_table_ct || 0 },
        { name: 'Anomaly Columns', value: displayedRunSummary?.anomaly_column_ct || 0 },
    ];

    // Overview content generation for this specific chart
    const generateAnomalyOverview = () => {
        if (!displayedRunSummary) return 'No anomaly data available.';
        return (
            <Box sx={{ p: 1 }}> {/* Added padding for popover content */}
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Anomaly Summary Overview</Typography>
                <Typography variant="body2">Total Anomaly Rows: {displayedRunSummary.anomaly_ct || 0}</Typography>
                <Typography variant="body2">Tables Affected: {displayedRunSummary.anomaly_table_ct || 0}</Typography>
                <Typography variant="body2">Columns Affected: {displayedRunSummary.anomaly_column_ct || 0}</Typography>
                 {/* Add more context if needed */}
            </Box>
        );
    };

    // Popover Handlers
    const handlePopoverOpen = (event) => {
        setPopoverAnchorEl(event.currentTarget);
    };

    const handlePopoverClose = () => {
        setPopoverAnchorEl(null);
    };

    const popoverOpen = Boolean(popoverAnchorEl);
    const popoverId = popoverOpen ? `anomaly-overview-popover-${id}` : undefined;


    // Drag and Drop Implementation
    const [, drop] = useDrop({
        accept: ItemTypes.CHART,
        hover(item, monitor) {
            if (!ref.current) {
                return;
            }
            const dragIndex = item.index;
            const hoverIndex = index;

            // Don't replace items with themselves
            if (dragIndex === hoverIndex) {
                return;
            }

            // Determine rectangle on screen
            const hoverBoundingRect = ref.current?.getBoundingClientRect();

            // Get vertical middle
            const hoverMiddleY = (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;

            // Get pixels to the top
            const clientOffset = monitor.getClientOffset();

            // Get pixels to the top
            const hoverClientY = clientOffset.y - hoverBoundingRect.top;

            // Only perform the move when the mouse has crossed half of the items height
            // When dragging downwards, only move when the cursor is below 50%
            // When dragging upwards, only move when the cursor is above 50%

            // Dragging downwards
            if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) {
                return;
            }

            // Dragging upwards
            if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) {
                return;
            }

            // Time to actually perform the action
            moveCard(dragIndex, hoverIndex);

            // Note: we're mutating the monitor item here!
            // Generally it's better to avoid mutations,
            // but it's useful here to avoid a costly search
            // of the array index by id.
            item.index = hoverIndex;
        },
    });

    const [{ isDragging }, drag] = useDrag({
        type: ItemTypes.CHART,
        item: () => {
            return { id, index };
        },
        collect: (monitor) => ({
            isDragging: monitor.isDragging(),
        }),
    });

    // Initialize drag and drop on the component's ref
    drag(drop(ref));


    return (
        <Grid item xs={12} sm={6} md={4} ref={ref} style={{ opacity: isDragging ? 0.5 : 1, cursor: 'move' }}> {/* Attach ref and style for drag */}
            <Box
                onClick={() => onChartClick(id)} // Single click to open full view
                onMouseEnter={handlePopoverOpen} // Hover to open overview popover
                onMouseLeave={handlePopoverClose} // Mouse leave to close popover
                sx={{ cursor: 'pointer', height: '100%' }}
            >
                <Paper sx={{ p: 2, height: '100%', minHeight: 280 }}>
                    <Typography variant="h6" gutterBottom>Anomaly Summary</Typography>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={anomalyData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <XAxis dataKey="name" stroke={theme.palette.text.primary} />
                            <YAxis stroke={theme.palette.text.primary} />
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, border: 'none' }} />
                            <Bar dataKey="value" fill={theme.palette.primary.main} />
                        </BarChart>
                    </ResponsiveContainer>
                    <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={1}>
                        Click for full view, hover for overview
                    </Typography>
                </Paper>
            </Box>

            {/* Popover for Overview on Hover */}
            <Popover
                id={popoverId}
                open={popoverOpen}
                anchorEl={popoverAnchorEl}
                onClose={handlePopoverClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                }}
                sx={{
                    pointerEvents: 'none', // Allows mouse events to pass through popover to trigger click on container
                    '& .MuiPopover-paper': {
                        bgcolor: theme.palette.background.paper, // Dark grey background for popover
                        color: theme.palette.text.primary, // Light text color
                        p: 1, // Add some padding
                        maxWidth: '300px' // Limit popover width
                    }
                }}
            >
                {generateAnomalyOverview()}
            </Popover>
        </Grid>
    );
};

export default AnomalySummaryChart;
