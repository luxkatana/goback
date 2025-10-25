import { useContext, useState, type FormEvent } from "react";
import { AuthContext } from "../components/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button, Form } from "react-bootstrap";

export default function SignupPage() {
	const [username, setusername] = useState("");
	const [email, setemail] = useState("");
	const [password, setpassword] = useState("");
	const credentialmanager = useContext(AuthContext);
	const [errors, seterrors] = useState("");
	const navigate = useNavigate();


	const FormCallback = async (e: FormEvent) => {
		e.preventDefault();
		fetch("http://127.0.0.1:8000/api/signup", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"

			},
			body: JSON.stringify({ username: username, password: password, email: email })
		}).then((r) => r.json()).then((json_response) => {
			if (json_response.error > 0)
				seterrors(json_response.msg);
			else {
				localStorage.setItem("goback_access_token", json_response.access_token);
				credentialmanager?.setToken(json_response.access_token);
				navigate("/dashboard");
			}


		})





	};
	return <>
		{errors.length > 0 ? <h2>{errors}</h2> : null}
		<div className="d-flex justify-content-center" style={{ marginTop: "20px" }}>
			<h1>Sign up</h1>
		</div>
		<div className="d-flex justify-content-center align-items-center vh-100">
			<Form onSubmit={FormCallback}>
				<Form.Group>
					<Form.Label>Username (4-10 characters)</Form.Label>
					<Form.Control min={4} max={10} type="text" onChange={(new_value) => setusername(new_value.target.value)} name="username" />
				</Form.Group>
				<Form.Group>
					<Form.Label>Email</Form.Label>
					<Form.Control max={254} type="email" onChange={(new_value) => setemail(new_value.target.value)} name="email" />
				</Form.Group>
				<Form.Group>
					<Form.Label>Password (must have at least 8 characters)</Form.Label>
					<Form.Control max={210} min={8} type="password" onChange={(new_value) => setpassword(new_value.target.value)} name="password" />
				</Form.Group>
				<Button variant="primary" type="submit">Sign up!!</Button>
			</Form>
		</div>

	</>



}
