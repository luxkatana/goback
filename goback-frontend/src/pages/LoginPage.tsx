import { useContext, useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom";
import { AuthContext, type AuthContextProperties } from "../components/AuthContext";
import { Alert, Button, Form } from "react-bootstrap";



export default function LoginPage() {
	const [email, setemail] = useState("");
	const [password, setpassword] = useState("");
	const credentials_manager: AuthContextProperties = useContext(AuthContext) as AuthContextProperties;
	const [status, setstatus] = useState("");
	const navigate = useNavigate();
	const onSubmitForm = async (e: FormEvent) => {
		e.preventDefault();
		const body_json = await fetch("http://127.0.0.1:8000/api/login", {
			method: "POST",
			body: JSON.stringify({ email: email, password: password }),
			headers: {
				"Content-Type": "application/json",
			}

		}).then((rep) => rep.json());
		if (body_json.error > 0)
			setstatus(body_json.msg);
		else {
			localStorage.setItem("goback_access_token", body_json.access_token);
			credentials_manager.setToken(body_json.access_token);
			navigate("/dashboard");
		}


	};


	return <>
		{status.length > 0 ? <Alert variant="warning">{status}</Alert> : null}
		<div className="d-flex justify-content-center align-items-center vh-100">
			<Form onSubmit={onSubmitForm}>
				<Form.Group>
					<Form.Label>Email Address: </Form.Label>
					<Form.Control type="text" onChange={(e) => setemail(e.target.value)} placeholder="Email here" required />
				</Form.Group>
				<Form.Group>
					<Form.Label>Password: </Form.Label>
					<Form.Control type="password" onChange={(e) => setpassword(e.target.value)} placeholder="Your super secret password here: " required />
				</Form.Group>
				<Button variant="primary" type="submit">Log in</Button>
			</Form>
		</div>
	</>
}

