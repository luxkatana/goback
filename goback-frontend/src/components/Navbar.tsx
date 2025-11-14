import { Box, Flex, Link } from "@chakra-ui/react";
import { useContext } from "react";
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { AuthContext } from "../utils/AuthContext";
import { routes } from "../main";
import ProtectedComponent from "./ProtectedComponent";
import { ColorModeButton } from "./ui/color-mode";
interface NavbarProps {
	to: string,
	current_url: boolean,
	children: React.ReactNode
}
function NavbarLink(props: NavbarProps) {
	return <>
		<Link asChild fontSize="3xl" fontWeight="bold" _hover={{ color: "cyan.300" }} textDecoration={props.current_url === true ? "underline" : "none"}>
			<RouterLink to={props.to}>
				{props.children}</RouterLink>
		</Link>

	</>

}
export default function Navbar() {
	const auth_holder = useContext(AuthContext);
	const location = useLocation();
	return <>
		<Box padding={5} marginBottom={5}>
			<ColorModeButton />
			<Flex gap="4" justifyContent="center">
				{routes.map((route) => {
					var is_current_url: boolean = false;
					if (route.path == '/' && route.path === location.pathname) {
						is_current_url = true;
					} else if (route.path != "/" && location.pathname.startsWith(route.path)) { // can be simplified in one if statement but that'll be too ugly
						is_current_url = true;
					}

					if (route.name == null) { return <></> }
					if (route.element.type === ProtectedComponent && auth_holder.isValid == false) {
						return <></>
					}
					if (route.element.type !== ProtectedComponent && auth_holder.isValid == true) {
						return <></>
					}
					return <NavbarLink current_url={is_current_url} to={route.path}>{route.name}</NavbarLink>

				})}
			</Flex>
		</Box>
	</>

}
