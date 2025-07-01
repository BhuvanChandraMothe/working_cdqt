import './App.css';
import * as React from 'react';
import { styled, useTheme } from '@mui/material/styles';
import {
  Box, Drawer, CssBaseline, Toolbar, List, ButtonBase, Typography, Divider,
  IconButton, Accordion, AccordionSummary, AccordionDetails,
  ListItem, ListItemButton, ListItemText, ListItemIcon,
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  AppBar as MuiAppBar
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { Routes, Route, useNavigate, Link } from "react-router-dom";
import logo from './assets/WhiteCovasant.svg';
import Home from './components/Home';
import DBConnection from './components/DBconnection';
import DBConnectionView from './components/DBConnectionView';
import { getAllConnections, deleteConnection } from './api/dbapi';
import HomepageLayout from './components/HomepageLayout';
import useAuth from './components/keycloaks/useAuth';

const drawerWidth = 240;

const Main = styled('main', {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  flexGrow: 1,
  backgroundColor: '#000',
  padding: theme.spacing(3),
  paddingTop: `64px`,
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
  marginLeft: `-${drawerWidth}px`,
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: 0,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  backgroundColor: '#1E1E1E',
  color: '#fff',
  boxShadow: 'none',
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),

  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const LogoImage = styled('img')({
  width: '80%',
  margin: '0 auto 16px auto',
  display: 'block',
});

const App = () => {
  const theme = useTheme();
  const [open, setOpen] = React.useState(true);
  const navigate = useNavigate();
  const [connections, setConnections] = React.useState([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [selectedConnectionId, setSelectedConnectionId] = React.useState(null);


  const handleDrawerOpen = () => setOpen(true);

  const handleDrawerClose = () => setOpen(false);


  const handleAddNewDatabaseClick = () => {
    navigate('/addnewdatabase');
    setOpen(false);
  };


  const fetchConnections = async () => {
    try {
      const data = await getAllConnections();
      setConnections(data);
    } catch (error) {
      console.error("Error fetching connections:", error);

    }
  };


  React.useEffect(() => {
    fetchConnections();
  }, []);


  const handleConnectionSaved = (newConnection) => {

    setConnections((prev) => [...prev, newConnection]);


  };


  const handleDeleteClick = (id) => {
    setSelectedConnectionId(id);
    setDeleteDialogOpen(true);
  };


  const confirmDelete = async () => {
    try {

      await deleteConnection(selectedConnectionId);

      setConnections(prev => prev.filter(conn => conn.connection_id !== selectedConnectionId));



    } catch (error) {
      console.error("Error deleting connection:", error);

    } finally {

      setDeleteDialogOpen(false);
      setSelectedConnectionId(null);
    }
  };

//   const { isLogin, keycloak } = useAuth();
//   React.useEffect(() => {
//   if (isLogin && keycloak?.idToken) {
//     localStorage.setItem('token', keycloak.idToken);
//   }
// }, [isLogin, keycloak]);
//   if (!isLogin) return <div>Loading authentication...</div>;
 


  return (
    <Box sx={{ display: 'flex' }} >
      <CssBaseline />
      <AppBar position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            <ButtonBase
              component={Link}
              to="/"
              className='link'
              sx={{ textDecoration: 'none', color: 'white', width: 'fit-content' }}
            >
              DB Inspector
            </ButtonBase>
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Drawer (Sidebar) */}
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: '#121212',
            color: '#fff',
          },
        }}
        variant="persistent"
        anchor="left"
        open={open}
      >

        <DrawerHeader>
          <IconButton onClick={handleDrawerClose} sx={{ color: '#fff' }}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </DrawerHeader>


        <LogoImage src={logo} alt="Logo" />
        <Divider sx={{ backgroundColor: '#333' }} />
        <Accordion defaultExpanded disableGutters sx={{ backgroundColor: '#1e1e1e', color: '#fff' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#fff' }} />}>
            <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
              DB Connections
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <List dense>
              {connections.map((conn) => (
                <ListItem
                  key={conn.connection_id}
                  secondaryAction={

                    <IconButton edge="end" onClick={(e) => {
                      e.stopPropagation();

                      handleDeleteClick(conn.connection_id);
                    }}>
                      <DeleteIcon sx={{ color: '#fff', fontSize: '18px' }} />
                    </IconButton>
                  }
                  disablePadding
                >
                  {/* Button for navigating to the connection view */}
                  <ListItemButton
                    sx={{ px: 2, py: 0.5 }}
                    onClick={() => navigate(`/connection/${conn.connection_id}`)}
                  >
                    <ListItemText

                      primary={conn.connection_name}
                      primaryTypographyProps={{ fontSize: '0.85rem' }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
              {/* Button to add a new database */}
              <ListItem disablePadding>
                <ListItemButton onClick={handleAddNewDatabaseClick} sx={{ px: 2, py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}> {/* Adjust icon spacing */}
                    <AddIcon style={{ color: '#fff', fontSize: '18px' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary="Add New Database"
                    primaryTypographyProps={{ fontSize: '0.85rem' }}
                  />
                </ListItemButton>
              </ListItem>
              <ButtonBase
                component={Link}
                to="/newhome"
                className='link'
                sx={{ textDecoration: 'none', color: 'white', width: 'fit-content' }}
              >
                New home
              </ButtonBase>
            </List>
          </AccordionDetails>
        </Accordion>
      </Drawer>

      {/* Main content area */}
      <Main open={open}>
        {/* Define routes for different pages */}
        <Routes>
          <Route path="/" element={<Home />} /> {/* Home page */}
          {/* DBConnection page for adding new connections, pass handleConnectionSaved */}
          <Route path="/addnewdatabase" element={<DBConnection onConnectionSaved={handleConnectionSaved} />} />
          {/* DBConnectionView page for viewing/editing a specific connection */}
          <Route path="/connection/:connection_id" element={<DBConnectionView />} />
          <Route path="/newhome" element={<HomepageLayout />} />
        </Routes>
      </Main>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Connection</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete this database connection?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default App;
