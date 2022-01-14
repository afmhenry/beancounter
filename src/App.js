
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import './App.css';

const Header = (props) => (
      <header>
        <h1>{props.title}</h1>
      </header>
);

const App = () => (
  <Container>
    <Row>
      <Header title="Beancounter" />
    </Row>
    <Row>
    <Header title="Beancounter2" />
    </Row>
  </Container>
);

export default App;