import { useEffect, useRef, useState } from "react";
import { Button, Col, Image, Modal, Row } from "react-bootstrap";
import { FileArrowDown } from "react-bootstrap-icons";
import { useLoaderData } from "react-router-dom";

const TYPE_ALL_PORTRAITS = 1;
const TYPE_ONE_LANDSCAPE = 2;
const TYPE_TWO_LANDSCAPE = 3;

function row_get_type(row) {
	const check_is_landscape = (photo) => photo.is_portrait === false;
	let result = TYPE_ALL_PORTRAITS;

	if (row.filter(check_is_landscape).length === 1) {
		result = TYPE_ONE_LANDSCAPE;
	} else if (row.filter(check_is_landscape).length === 2) {
		result = TYPE_TWO_LANDSCAPE;
	}

	return result;
}

function portrait_get_size(container_width, row_type) {
	let width = 0;

	if (row_type === TYPE_ALL_PORTRAITS) {
		width = Math.floor(container_width / 4);
	} else if (row_type === TYPE_ONE_LANDSCAPE) {
		width = Math.floor(container_width * 0.2092);
	} else {
		width = Math.floor(container_width * 0.2195);
	}

	return [width, Math.floor((width / 3) * 4)];
}

function landscape_get_size(container_width, row_type) {
	let width = 0;

	if (row_type === TYPE_ONE_LANDSCAPE) {
		width = Math.floor(container_width * 0.3721);
	} else {
		width = Math.floor(container_width * 0.3901);
	}

	return [width, Math.floor((width / 4) * 3)];
}

function PhotoRow({ row, handleClick }) {
	const row_type = row_get_type(row);
	const [portraitSize, setPortraitSize] = useState([0, 0]);
	const [landscapeSize, setLandscapeSize] = useState([0, 0]);

	const rowRef = useRef();

	useEffect(() => {
		const resizeObserver = new ResizeObserver((event) => {
			const container_width = event[0].contentBoxSize[0].inlineSize;

			setPortraitSize(portrait_get_size(container_width, row_type));
			setLandscapeSize(landscape_get_size(container_width, row_type));
		});

		if (rowRef) {
			resizeObserver.observe(rowRef.current);
		}
	}, [rowRef]);

	return (
		<Row ref={rowRef} className="g-0">
			{row.map((photo, photo_idx) => (
				<Col
					key={photo_idx}
					xs="auto"
					md="auto"
					sm="auto"
					lg="auto"
					style={{
						height: photo.is_portrait ? portraitSize[1] : landscapeSize[1],
					}}
				>
					<Image
						thumbnail
						onClick={() => handleClick(photo)}
						src={(import.meta.env?.VITE_SERVER_URL ?? "").concat(
							photo.thumbnail,
						)}
						width={photo.is_portrait ? portraitSize[0] : landscapeSize[0]}
						//height={photo.is_portrait ? portraitSize[1] : landscapeSize[1]}
						alt={photo.photo}
					/>
				</Col>
			))}
		</Row>
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
			{album.photos.map((row, row_idx) => (
				<PhotoRow
					handleClick={(photo) => setShow(photo)}
					row={row}
					key={row_idx}
				/>
			))}
		</>
	);
}