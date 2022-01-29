import React from 'react';
import Row from 'react-bootstrap/Row';
import LineChart from '../D3'
import Container from 'react-bootstrap/Container';

//SELECT year, value(sum(cost(position))) where account ~'Assets:Investment' and not account ~ 'Unrealized'
//SELECT month, position, cost(position) as total where account ~ 'Assets:Investment' group by month, position, total
//SELECT month, position, cost(position) as total where account ~ 'Assets:Investment' and not account ~ 'Unrealized' and not account ~'Cash' group by month, position, total
//SELECT account, position, cost(position) as total where account ~ 'Unrealized' group by account,position, total
const RequestInput={"Include":"Assets", "Year": "2022,2021"};

function Assets(){
  return (
    <Container className="App-Container">
        <LineChart  {...RequestInput}/>
    </Container>
  );
}

export default {
    routeProps: {
        path: '/assets',
        exact: true,
        element: Assets()
    },
    name: 'Assets'
};