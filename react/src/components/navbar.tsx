import React from 'react';
import { LinkContainer } from 'react-router-bootstrap';
import { Navbar, Nav, Container, Button, NavDropdown } from 'react-bootstrap';
import { useAuth } from '../AuthContext';

type NavbarProps = {
  admin: boolean;
};

const AppNavbar: React.FC<NavbarProps> = ({ admin }) => {
  const { user, logout } = useAuth();

  return (
    <Navbar bg="light" expand="lg" className="mb-3">
      <Container>
        <LinkContainer to={admin ? "/admin" : "/"}>
          <Navbar.Brand>{admin ? "Admin Panel" : "Scoreboard"}</Navbar.Brand>
        </LinkContainer>
        {user && (<span className="mx-3 text-muted">|</span>)}
        {user && !user?.is_blue_team && (
                <LinkContainer to="/details">
                <Navbar.Brand>Blue Team Details</Navbar.Brand>
              </LinkContainer>
        )}
        {user && user?.is_blue_team && (
                <LinkContainer to="/details">
                <Navbar.Brand>{`Team ${user?.blue_team_num} Scoring`}</Navbar.Brand>
              </LinkContainer>
        )}
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            {user ? (
              <>
                <NavDropdown title={`Hello, ${user.username}`} id="user-dropdown" align="end">
                  <NavDropdown.Item onClick={logout}>Logout</NavDropdown.Item>
                </NavDropdown>
              </>
            ) : (
              <LinkContainer to="/login">
                <Nav.Link>Login</Nav.Link>
              </LinkContainer>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;
