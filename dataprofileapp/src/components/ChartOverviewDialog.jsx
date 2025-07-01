import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Typography,
    Box,
    Divider
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const ChartOverviewDialog = ({ open, onClose, title, content }) => {
    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="sm"
            PaperProps={{
                sx: {
                    backgroundColor: '#1e1e1e',
                    color: '#fff',
                    borderRadius: 4,
                }
            }}
        >
            <DialogTitle
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: 2,
                    borderBottom: '1px solid #444',
                    color: '#fff',
                }}
            >
                <Typography variant="h6" component="div" sx={{ color: '#fff' }}>
                    {title}
                </Typography>
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={{ color: '#fff' }}
                >
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent dividers sx={{ padding: 3, color: '#fff' }}>
                {typeof content === 'string' ? (
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', color: '#fff' }}>
                        {content}
                    </Typography>
                ) : (
                    <Box sx={{ color: '#fff' }}>
                        {content}
                    </Box>
                )}
            </DialogContent>
        </Dialog>
    );
};

export default ChartOverviewDialog;
