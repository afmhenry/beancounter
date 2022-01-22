import React from 'react';
import Row from 'react-bootstrap/Row';
import BarChart from '../D3'
import Container from 'react-bootstrap/Container';

function Income(){
  return (
    <Container className="App-Container">
        <BarChart/>
    </Container>
  );
}

export default {
    routeProps: {
        path: '/income',
        exact: true,
        element: Income()
    },
    name: 'Income'
};