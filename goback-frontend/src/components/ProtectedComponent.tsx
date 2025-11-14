import type React from "react";
import { useContext, useEffect } from "react";
import { AuthContext, type AuthInfo } from "../utils/AuthContext";
import { useLocation, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export default function ProtectedComponent({ children }: { children: React.ReactNode }) {
	const auth: AuthInfo = useContext(AuthContext);
	const location = useLocation();
	const navigate = useNavigate();
	useEffect(() => {
		if (auth.isValid === false && auth.loading === false) {
			console.log(auth.isValid);
			toast("Please login to continue")
			navigate(`/login?n=${location.pathname}`);
		}
	}, [auth.loading]);
	return <>
		{children}
	</>

}
