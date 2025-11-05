import { useContext } from "react"
import { AuthContext, type AuthInfo } from "../utils/AuthContext"
import { Heading, Link as CLink, VStack, Text } from "@chakra-ui/react";
import { Link } from "react-router-dom";

export default function Dashboard() {
	const auth_holder: AuthInfo = useContext(AuthContext);
	return <>
		<VStack>
			<Heading size="6xl">Welcome {auth_holder.username}!!</Heading>
			<Text fontSize="6xl"><CLink asChild colorPalette="green" _hover={{ color: "cyan.50" }}><Link to="/create">Click here to create a new backup</Link></CLink></Text>
		</VStack>
	</>
}
