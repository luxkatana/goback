import { useContext, useEffect, useState } from "react"
import { AuthContext } from "../components/AuthContext"
import { Link } from "react-router-dom";
interface BackupResponseObject {
	url_requested: string,
	file_id: string,
}

export default function DashboardPage() {
	const [backups, setbackups] = useState([]);
	useEffect(() => {
	});
	return <>
		<h1>Dashboard</h1>
		{backups.length == 0 ? <p><Link to="/create">You have nothing, please go here to create something!</Link></p> : null}
	</>

}
