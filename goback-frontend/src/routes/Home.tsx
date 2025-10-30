import { Heading, Highlight, Link, Text, VStack } from "@chakra-ui/react";
import { Link as RLink } from "react-router-dom";

export default function Home() {

	return <>
		<VStack>

			<Heading textStyle="6xl">

				<Highlight query="4ever (forever)!!" styles={{ color: "cyan.200" }}>
					Goback - make sites last 4ever (forever)!!
				</Highlight></Heading>

			<ul>
				<li>
					<Link variant="underline" colorPalette="green" asChild _hover={{ color: "cyan.400" }} marginTop={10}>
						<RLink to="/login">
							<Text textStyle="5xl">
								Already a member? Log in here!
							</Text>
						</RLink>
					</Link>
				</li>
				<li>
					<Link variant="underline" colorPalette="green" asChild _hover={{ color: "cyan.400" }} marginTop={5}>
						<Text textStyle="5xl">
							<RLink to="/signup">
								Not a member yet? Signup here!
							</RLink>
						</Text>
					</Link>
				</li>
			</ul>
		</VStack>
	</>

}
