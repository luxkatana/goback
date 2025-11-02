import { useContext, useEffect } from "react";
import { AuthContext, type AuthInfo } from "../utils/AuthContext";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export default function LogoutRoute() {
	const auth_config: AuthInfo = useContext(AuthContext);
	const navigate = useNavigate();
	useEffect(() => {
		if (auth_config.loading === false) {
			toast(`Logged out, bye ${auth_config.username}!`);
			localStorage.removeItem("goback_access_token");
			auth_config.setisValid!(false);
			navigate("/");
		}
	}, [auth_config.setisValid, auth_config.username, navigate, auth_config.loading]);
	return <>Bye</>
}
