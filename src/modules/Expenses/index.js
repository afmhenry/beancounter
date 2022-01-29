import React from 'react';
import Row from 'react-bootstrap/Row';
import LineChart from '../D3'
import Container from 'react-bootstrap/Container';

const RequestInput={"Include":"Expenses","Exclude":"Tax,Invest", "Year": "2022,2021"};

function Expenses(){
  return (
    <Container className="App-Container">
        <LineChart  {...RequestInput}/>
    </Container>
  );
}

export default {
    routeProps: {
        path: '/expenses',
        exact: true,
        element: Expenses()
    },
    name: 'Expenses'
};