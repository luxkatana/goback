import { Heading, Text, VStack, Link } from "@chakra-ui/react";
import { Link as RLink } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function ErrorPage() {
	return <>
		<Navbar />
		<VStack>
			<Heading size="7xl">
				404
			</Heading>
			<Text fontSize="3xl">404, page not found 😥</Text>
			<Link fontSize="3xl" colorPalette="cyan" _hover={{ color: "cyan.100" }} asChild><RLink to="/">Let's go back to the home page, shall we?</RLink></Link>
		</VStack>
	</>
}
