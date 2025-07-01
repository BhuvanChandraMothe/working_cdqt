import React, { useRef, useState } from 'react';
import { Box, Paper,Grid, Typography, Popover, useTheme } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip } from 'recharts';
import { useDrag, useDrop } from 'react-dnd'; // Import drag and drop hooks

// Define the item type for drag and drop
const ItemTypes = {
    CHART: 'chart',
};

const PIIFlagDistributionChart = ({ id, index, displayedProfileResults, onChartClick, moveCard, COLORS }) => {
    const theme = useTheme();
    const ref = useRef(null); // Ref for the draggable element

    // State for Popover
    const [popoverAnchorEl, setPopoverAnchorEl] = useState(null);

    // Data transformation for this specific chart
    const piiFlagData = Object.entries(
        displayedProfileResults.reduce((acc, cur) => {
             // Ensure pii_flag exists, default to 'Unknown' if null/empty
            const flag = cur.pii_flag && cur.pii_flag.trim() !== '' ? cur.pii_flag : 'Unknown';
            acc[flag] = (acc[flag] || 0) + 1;
            return acc;
        }, {})
    ).map(([flag, count]) => ({ name: flag, value: count }));

    // Overview content generation for this specific chart
     const generatePiiFlagOverview = () => {
        if (piiFlagData.length === 0) return 'No PII flag data available.';
        const totalColumns = displayedProfileResults.length;
        const content = (
            <Box sx={{ p: 1 }}> {/* Added padding for popover content */}
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>PII Flag Distribution Overview</Typography>
                 {piiFlagData.map((item, index) => (
                    <Typography variant="body2" key={index}>{item.name}: {item.value} columns ({totalColumns > 0 ? ((item.value / totalColumns) * 100).toFixed(1) : 0}%)</Typography>
                ))}
                 {/* Add explanation of PII flag meanings if helpful */}
            </Box>
        );
        return content;
     };

    // Popover Handlers
    const handlePopoverOpen = (event) => {
        setPopoverAnchorEl(event.currentTarget);
    };

    const handlePopoverClose = () => {
        setPopoverAnchorEl(null);
    };

    const popoverOpen = Boolean(popoverAnchorEl);
    const popoverId = popoverOpen ? `pii-overview-popover-${id}` : undefined;

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
        <Grid item xs={12} sm={6} ref={ref} style={{ opacity: isDragging ? 0.5 : 1, cursor: 'move' }}> {/* Attach ref and style for drag */}
            <Box
                onClick={() => onChartClick(id)} // Single click to open full view
                onMouseEnter={handlePopoverOpen} // Hover to open overview popover
                onMouseLeave={handlePopoverClose} // Mouse leave to close popover
                sx={{ cursor: 'pointer', height: '100%' }}
            >
                <Paper sx={{ p: 2, height: '100%', minHeight: 330 }}>
                    <Typography variant="h6" gutterBottom>PII Flag Distribution</Typography>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <Pie
                                data={piiFlagData}
                                dataKey="value"
                                nameKey="name"
                                outerRadius={90}
                                label={(entry) => `${entry.name}: ${entry.value}`}
                            >
                                {piiFlagData.map((entry, index) => (
                                    <Cell key={`pii-cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <RechartsTooltip contentStyle={{ backgroundColor: theme.palette.background.paper, border: 'none' }} />
                            <Legend />
                        </PieChart>
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
                {generatePiiFlagOverview()}
            </Popover>
        </Grid>
    );
};

export default PIIFlagDistributionChart;
