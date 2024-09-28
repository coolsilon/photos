import { useState } from "react";
import { RowsPhotoAlbum } from "react-photo-album";
import "react-photo-album/rows.css";
import { useLoaderData } from "react-router-dom";
import Lightbox from "yet-another-react-lightbox";
import { Download, Share } from "yet-another-react-lightbox/plugins";
import "yet-another-react-lightbox/styles.css";

export default function Album() {
	const album = useLoaderData();

	const [photo_show, setShow] = useState(undefined);

	const photos = (album?.photos ?? []).map((item) => ({
		src: (import.meta.env?.VITE_SERVER_URL ?? "").concat(item?.thumbnail ?? ""),
		width: item.size_thumbnail[0],
		height: item.size_thumbnail[1],
	}));
	const slides = (album?.photos ?? []).map((item) => ({
		src: (import.meta.env?.VITE_SERVER_URL ?? "").concat(item?.photo ?? ""),
		download: (import.meta.env?.VITE_SERVER_URL ?? "").concat(
			item?.download ?? "",
		),
		width: item.size[0],
		height: item.size[1],
	}));

	return (
		<>
			<h1>{album.name}</h1>
			<Lightbox
				open={photo_show !== undefined}
				close={() => setShow(undefined)}
				slides={slides}
				index={photo_show}
				plugins={[Download, Share]}
			/>
			<RowsPhotoAlbum
				photos={photos}
				spacing={5}
				targetRowHeight={320}
				rowConstraints={{ minPhotos: 3, maxPhotos: 4, singleRowMaxHeight: 520 }}
				onClick={({ index }) => setShow(index)}
				componentsProps={{
					image: { loading: "lazy" },
				}}
			/>
		</>
	);
}