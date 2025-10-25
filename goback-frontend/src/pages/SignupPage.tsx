import { useContext, useState, type FormEvent } from "react";
import { AuthContext } from "../components/AuthContext";
import { useNavigate } from "react-router-dom";

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
		<h1>Sign up</h1>
		<form onSubmit={FormCallback}>
			<div>
				<label htmlFor="username">Username (4-10 characters)</label>
				<input id="username" min={4} max={10} type="text" onChange={(new_value) => setusername(new_value.target.value)} name="username" />
			</div>
			<div>
				<label htmlFor="email">Email</label>
				<input id="email" max={254} type="email" onChange={(new_value) => setemail(new_value.target.value)} name="email" />
			</div>
			<div>
				<label htmlFor="password">Password (must have at least 8 characters)</label>
				<input id="password" max={210} min={8} type="password" onChange={(new_value) => setpassword(new_value.target.value)} name="password" />
			</div>
			<button type="submit">Sign up!!</button>
		</form>

	</>



}
