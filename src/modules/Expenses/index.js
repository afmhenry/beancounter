import React from 'react';
import Row from 'react-bootstrap/Row';
import LineChart from '../D3'
import Container from 'react-bootstrap/Container';


const input={
  "frame":  {"width":800,"height":300, "margin": 30}, 
  "request":{"Include":"Expenses","Exclude":"Tax,Invest", "Year": "2022,2021"}
};

function Expenses(){
  return (
    <Container className="App-Container">
        <LineChart  
          {...input}
        />
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