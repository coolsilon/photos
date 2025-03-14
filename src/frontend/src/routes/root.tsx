import { Container, ListGroup, Nav, Navbar, Stack } from "react-bootstrap";
import { Link, Outlet, useLoaderData } from "react-router-dom";

export function Home() {
	const albums = useLoaderData();
	return (
		<>
			<ListGroup>
				{albums.map((album, idx) => (
					<ListGroup.Item key={idx}>
						<Link to={"/album/".concat(album.name)}>{album.display}</Link>
					</ListGroup.Item>
				))}
			</ListGroup>
		</>
	);
}

export default function Root() {
	return (
		<>
			<Navbar bg="light" data-bs-theme="light">
				<Container>
					<Navbar.Brand as={Link} to="/">
						超陽春相冊
					</Navbar.Brand>
					<Nav className="me-auto">
						<Nav.Link to="/" as={Link}>
							Home
						</Nav.Link>
						<Nav.Link to="/login" as={Link}>
							Login
						</Nav.Link>
					</Nav>
				</Container>
			</Navbar>
			<Container className="my-5">
				<Stack gap="3">
					<Outlet />
				</Stack>
			</Container>
		</>
	);
}