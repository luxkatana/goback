import { useContext } from "react"
import { AuthContext, type AuthInfo } from "../utils/AuthContext"

export default function Dashboard() {
	const auth_holder: AuthInfo = useContext(AuthContext);
	return <>
		Welcome, your token is {auth_holder.access_token}
	</>
}
