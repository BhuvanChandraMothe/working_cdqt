import React, { useEffect, useState } from "react";
import {
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Typography,
    CircularProgress,
    Box,
    useTheme, // Import useTheme to access theme palette
    List, // Import List component
    ListItemButton, // Import ListItemButton component
    ListItemText, // Import ListItemText component
    Divider // Optional: Import Divider for list items
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useNavigate } from "react-router-dom";
import { getAllConnections } from "../../api/dbapi"; // adjust path if needed

const ConnectionsDialog = ({ open, onClose }) => {
    const [connections, setConnections] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const theme = useTheme(); // Access the current theme (including dark mode palette)

    useEffect(() => {
        if (open) {
            setLoading(true);
            setError(null);
            getAllConnections()
                .then((data) => {
                    // Ensure the API returns an array of connections
                    if (Array.isArray(data)) {
                        setConnections(data);
                    } else {
                        console.error("API returned non-array data:", data);
                        setConnections([]); // Set to empty array if API response is invalid
                        setError("Received unexpected data format.");
                    }
                })
                .catch((err) => {
                    console.error("Failed to load connections:", err);
                    setError("Failed to load connections.");
                })
                .finally(() => setLoading(false));
        }
    }, [open]);

    // Renamed from handleCardClick for clarity with ListItems
    const handleListItemClick = (conn) => {
        // Navigate using the connection_id
        navigate(`/connection/${conn.connection_id}`);
        onClose(); // Close dialog after navigation
    };

    // Define colors for dark mode based on the specific colors from DBConnectionView
    const dialogBackground = '#1e1e1e'; // Matching the content container background in DBConnectionView
    const primaryTextColor = theme.palette.text.primary; // Default text color (should be light in dark mode)
    const secondaryTextColor = theme.palette.text.secondary; // Secondary text color (light grey in dark mode)
    const lightGreyText = theme.palette.grey[50]; // A very light grey

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="sm" // Adjusted maxWidth for a list view
            PaperProps={{
                sx: {
                    borderRadius: theme.shape.borderRadius * 2, // Rounded corners
                }
            }}
        >
            <DialogTitle sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: theme.spacing(2, 3),
                borderBottom: `1px solid ${theme.palette.divider}`, // Subtle divider
            }}>
                <Typography variant="h6" component="div">
                    All Connections
                </Typography>
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={{ }} // Use secondary text color for icon
                >
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent dividers sx={{ padding: theme.spacing(1, 0) }}> {/* Adjusted padding for list */}
                {loading ? (
                    <Box display="flex" justifyContent="center" py={4}>
                        <CircularProgress />
                    </Box>
                ) : error ? (
                    <Typography color="error" align="center" sx={{ px: 3 }}>{error}</Typography> 
                ) : connections.length === 0 ? (
                    <Typography align="center" color={secondaryTextColor} sx={{ px: 3 }}>No connections found.</Typography>
                ) : (
                    <List>
                        {connections.map((conn, index) => (
                            <React.Fragment key={conn.connection_id}>
                                <ListItemButton
                                    onClick={() => handleListItemClick(conn)}
                                    sx={{
                                        // Subtle background on hover for dark mode
                                        '&:hover': {
                                             backgroundColor: theme.palette.action.hover, // Use theme hover color
                                        },
                                        // Optional: Add a subtle background even when not hovered
                                        // backgroundColor: index % 2 === 0 ? 'rgba(255, 255, 255, 0.03)' : 'transparent',
                                    }}
                                >
                                    <ListItemText
                                        primary={
                                            // Use a Box or Fragment to control layout within primary text
                                            <Box>
                                                <Typography
                                                    variant="subtitle1" // Slightly larger font for name
                                                    fontWeight="bold"
                                                    sx={{ color: primaryTextColor }} // Use primary text color for name
                                                >
                                                    {conn.connection_name && conn.connection_name.trim() !== ''
                                                        ? conn.connection_name
                                                        : `Connection ${conn.connection_id}`}
                                                </Typography>
                                            </Box>
                                        }
                                        secondary={
                                            // Use a Box or Fragment to control layout within secondary text
                                            <Box sx={{ mt: 0.5 }}> {/* Add a small top margin for separation */}
                                                <Typography variant="body2" sx={{ }}> {/* Use body2 and light grey color */}
                                                    ID: {conn.connection_id}
                                                </Typography>
                                            </Box>
                                        }
                                    />
                                </ListItemButton>
                                {/* Optional: Add a divider between list items */}
                                {index < connections.length - 1 && <Divider component="li" sx={{ borderColor: theme.palette.divider }} />}
                            </React.Fragment>
                        ))}
                    </List>
                )}
            </DialogContent>
        </Dialog>
    );
};

export default ConnectionsDialog;
