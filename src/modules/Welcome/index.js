import React from 'react';

const Welcome = () => (
    <div>Welcome Module</div>
);

export default {
    routeProps: {
        path: '/',
        element: Welcome(),
    },
    name: 'Welcome',
};
