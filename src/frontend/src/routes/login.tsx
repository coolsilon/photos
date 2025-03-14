import axios from "axios";
import type { FormEvent } from "react";
import { Form as BSForm, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

export default function Login() {
	const navigate = useNavigate();

	return (
		<>
			<h1>Login</h1>

			<BSForm
				onSubmit={async (e: FormEvent<HTMLFormElement>) => {
					e.preventDefault();

					const formData = new FormData(e.target);

					const response = await axios.post(
						(import.meta.env?.VITE_SERVER_URL ?? "").concat("/api/login"),
						formData,
					);

					if (response.status === 200) {
						navigate("/");
					}
				}}
			>
				<BSForm.Group className="mb-3" controlId="formBasicEmail">
					<BSForm.Label>Username</BSForm.Label>
					<BSForm.Control placeholder="Enter user name" name="username" />
				</BSForm.Group>

				<BSForm.Group className="mb-3" controlId="formBasicPassword">
					<BSForm.Label>Password</BSForm.Label>
					<BSForm.Control
						type="password"
						name="password"
						placeholder="Password"
					/>
				</BSForm.Group>
				<Button variant="primary" type="submit">
					Submit
				</Button>
			</BSForm>
		</>
	);
}
