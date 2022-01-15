import React from 'react';
import Row from 'react-bootstrap/Row';


const Dashboard = () => (
    <div>Dashboard Module</div>
);

export default {
    routeProps: {
        path: '/dashboard',
        exact: true,
        element: Dashboard(),
    },
    name: 'Dashboard',
};


