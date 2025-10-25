import { useContext, useState, type FormEvent } from "react"
import { AuthContext, type AuthContextProperties } from "../components/AuthContext"

export default function CreationPage() {
	const [url, seturl] = useState("");
	const credentials: AuthContextProperties = useContext(AuthContext)!;
	const FormCallback = (e: FormEvent) => {
		e.preventDefault();
		fetch("http://127.0.0.1:8000/api/scrape", {
			method: "POST",
			body: JSON.stringify({ url: url })
		}).then(r => r.json())
			.then(json_object => {
				const job_task_id = json_object.job_task_id;

			});

	};
	return <>
		<h1>Create here a backup</h1>
		<form onSubmit={FormCallback}>
			<div>
				<label htmlFor="url">The url:</label>
				<input type="url" name="url" onChange={(e) => seturl(e.target.value)} required />
			</div>
			<button type="submit">Submit</button>
		</form>
	</>
}
