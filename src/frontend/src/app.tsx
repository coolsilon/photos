import axios from "axios";
import {
	RouterProvider,
	createBrowserRouter,
	redirect,
} from "react-router-dom";
import Album from "./routes/album";
import Login from "./routes/login";
import Root, { Home } from "./routes/root";

function setup_axios() {
	const http = axios.create();

	http.interceptors.response.use(
		(response) => response,
		(error) => {
			if (error.response && error.response.status === 401) {
				// Redirect to login on 401
				return Promise.reject(redirect("/login"));
			}
			return Promise.reject(error);
		},
	);

	return http;
}

export default function App() {
	const http = setup_axios();

	const router = createBrowserRouter([
		{
			path: "/",
			element: <Root />,
			children: [
				{
					index: true,
					element: <Home />,
					loader: async () => {
						try {
							return (
								await http.get(
									(import.meta.env?.VITE_SERVER_URL ?? "").concat("/api/album"),
								)
							).data;
						} catch (error) {
							console.error(error);
							throw error;
						}
					},
				},
				{
					path: "album/:albumName",
					element: <Album />,
					loader: async ({ params }) => {
						try {
							return (
								await http.get(
									(import.meta.env?.VITE_SERVER_URL ?? "")
										.concat("/api/album/")
										.concat(params.albumName ?? ""),
								)
							).data;
						} catch (error) {
							console.error(error);
							throw error;
						}
					},
				},
				{
					path: "login",
					element: <Login />,
				},
			],
		},
	]);

	return <RouterProvider router={router} />;
}
