import { useContext } from "react"
import { AuthContext, type AuthInfo } from "../utils/AuthContext"
import { Heading } from "@chakra-ui/react";

export default function Dashboard() {
	const auth_holder: AuthInfo = useContext(AuthContext);
	return <>
		<Heading size="6xl">Welcome {auth_holder.username}!!</Heading>
	</>
}
