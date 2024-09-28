import { Container, ListGroup } from "react-bootstrap";
import { Link, Outlet, useLoaderData, useOutlet } from "react-router-dom";

function Home({ albums }) {
	return (
		<>
			<h1>超陽春相冊</h1>
			<ListGroup>
				{albums.map((album, idx) => (
					<ListGroup.Item key={idx}>
						<Link to={"/album/".concat(album.name)}>{album.name}</Link>
					</ListGroup.Item>
				))}
			</ListGroup>
		</>
	);
}

export default function Root() {
	const albums = useLoaderData();
	return (
		<>
			<Container>
				{useOutlet() == null ? <Home albums={albums} /> : <Outlet />}
			</Container>
		</>
	);
}