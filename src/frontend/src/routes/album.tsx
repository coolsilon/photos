import { useState } from "react";
import { Button, Image, Modal } from "react-bootstrap";
import { FileArrowDown } from "react-bootstrap-icons";
import { RowsPhotoAlbum } from "react-photo-album";
import "react-photo-album/rows.css";
import { useLoaderData } from "react-router-dom";

function PhotoAlbum({ photos, handleClick }) {
	const photo_list = photos.map((item) => ({
		src: (import.meta.env?.VITE_SERVER_URL ?? "").concat(item?.thumbnail ?? ""),
		width: item.size_thumbnail[0],
		height: item.size_thumbnail[1],
	}));
	return (
		<>
			<RowsPhotoAlbum
				photos={photo_list}
				spacing={5}
				targetRowHeight={320}
				rowConstraints={{ minPhotos: 3, maxPhotos: 4, singleRowMaxHeight: 520 }}
				onClick={({ index }) => handleClick(photos[index])}
				componentsProps={{
					image: { loading: "lazy" },
				}}
			/>
		</>
	);
}

export default function Album() {
	const album = useLoaderData();

	const [photo_show, setShow] = useState(undefined);

	return (
		<>
			<h1>{album.name}</h1>
			<Modal
				show={photo_show !== undefined}
				fullscreen={true}
				onHide={() => setShow(undefined)}
			>
				<Modal.Header closeButton>
					<Modal.Title>{photo_show?.name ?? ""}</Modal.Title>
				</Modal.Header>
				<Modal.Body>
					<Image
						fluid
						src={(import.meta.env?.VITE_SERVER_URL ?? "").concat(
							photo_show?.photo ?? "",
						)}
					/>
				</Modal.Body>
				<Modal.Footer>
					<Button
						href={(import.meta.env?.VITE_SERVER_URL ?? "").concat(
							photo_show?.download ?? "",
						)}
						size="lg"
						variant="outline-secondary"
					>
						<FileArrowDown />
						<br />
						Download
					</Button>
				</Modal.Footer>
			</Modal>
			<PhotoAlbum
				handleClick={(photo) => setShow(photo)}
				photos={album.photos}
			/>
		</>
	);
}