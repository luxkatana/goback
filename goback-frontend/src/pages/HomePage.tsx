import { Link } from "react-router-dom";
import "./HomePage.css";
import { useContext, useEffect } from "react";
import { AuthContext, type AuthContextProperties } from "../components/AuthContext";
export default function HomePage() {
	const credentialsman: AuthContextProperties = useContext(AuthContext)!;
	useEffect(() => {
		console.log(`zeg maar, je credentials zijn '${credentialsman.token}'`);
	}, [credentialsman]);

	return <>
		<h1>Goback</h1>
		{credentialsman.token?.length == null ?
			<>
				<h2> <Link to="/login">Click here to login</Link></h2>
				<h2><Link to="/signup">Click here to signup</Link></h2>
			</>
			:
			<h2><Link to="/dashboard">Hey!! Welcome back, click here to go to the dashboard</Link></h2>
		}
	</>
}
