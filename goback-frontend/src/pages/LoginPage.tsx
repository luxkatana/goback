import { useContext, useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom";
import { AuthContext, type AuthContextProperties } from "../components/AuthContext";



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
		{status.length > 0 ? <p>{status}</p> : null}
		<form onSubmit={onSubmitForm}>
			<p>Email:</p>
			<input type="text" onChange={(e) => setemail(e.target.value)} required />
			<p>Password:</p>
			<input type="password" onChange={(e) => setpassword(e.target.value)} required />
			<button type="submit">Log in</button>
		</form>
	</>

}
