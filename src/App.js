import React from 'react';
import { MemoryRouter, BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import Nav from 'react-bootstrap/Nav';
import NavItem from 'react-bootstrap/NavItem';
import NavLink from 'react-bootstrap/NavLink';
import NavContext from 'react-bootstrap/NavContext';
import { LinkContainer } from 'react-router-bootstrap';
import { useState } from 'react';

import './App.css';
import modules from './modules';



function App(){
  

  return(
    <Container id="Parent" fluid className="App-NavContainer g-0">
      <Row className="g-0">
      <Router>
              <Nav className="App-NavBar">
                  {modules.map(module => ( // with a name, and routes
                    <Nav.Item key={module.name} className = "App-NavItem">
                      <Nav.Link href={module.routeProps.path} className="App-NavLink">{module.name}</Nav.Link>
                    </Nav.Item>
                  ))}
                </Nav>
              <Routes>
              {modules.map(module => (
                <Route {...module.routeProps} key={module.name} />
              ))}
            </Routes>
        </Router>
      </Row>

    </Container>
  )

}

export default App;
