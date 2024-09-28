import { createBrowserRouter } from "react-router-dom";
import Album from "./routes/album";
import Root from "./routes/root";

const router = createBrowserRouter([
	{
		path: "/",
		element: <Root />,
		loader: async () =>
			fetch((import.meta.env?.VITE_SERVER_URL ?? "").concat("/api/album")),
		children: [
			{
				path: "album/:albumName",
				element: <Album />,
				loader: async ({ params }) =>
					fetch(
						(import.meta.env?.VITE_SERVER_URL ?? "")
							.concat("/api/album/")
							.concat(params.albumName ?? ""),
					),
			},
		],
	},
]);

export default router;