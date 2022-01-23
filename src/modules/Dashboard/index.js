import React from 'react';
import Row from 'react-bootstrap/Row';

import Helpers from '../API'

class QueryForm1 extends React.Component {


    constructor(props) {
        super(props);
        this.state = {
          Include1: "",
          Exclude1: ""
        };
    
        this.handleInputChange = this.handleInputChange.bind(this);
      }
    
      handleInputChange(event) {
        const target = event.target;
        const value = target.value;
        const name = target.name;
    
        this.setState({
          [name]: value
        });
      }
      handleSubmit = (event) => {
        event.preventDefault();
        Helpers.RequestData(this.state)
      }

  
    render(){ 
        return (
            <form onSubmit={this.handleSubmit}>
            <label>
                Include:
                <input type="text" name="Include" value={this.state.Include1} onChange={this.handleInputChange} />
            </label>
            <label>
                Exclude:
                <input type="text" name="Exclude" value={this.state.Exclude1} onChange={this.handleInputChange} />
            </label>
            <input type="submit" value="Submit" />
            </form>
        )
    }
}

const Dashboard = () => (
    <Row>    
        <QueryForm1 />
    </Row>
);

export default {
    routeProps: {
        path: '/dashboard',
        exact: true,
        element: Dashboard(),
    },
    name: 'Dashboard',
};