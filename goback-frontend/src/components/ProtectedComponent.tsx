import type React from "react";
import { useContext, useEffect } from "react";
import { AuthContext, type AuthInfo } from "../utils/AuthContext";
import { useNavigate } from "react-router-dom";

export default function ProtectedComponent({ children }: { children: React.ReactNode }) {
	const auth: AuthInfo = useContext(AuthContext);
	const navigate = useNavigate();
	useEffect(() => {
		auth.isValid == false ? navigate("/login") : null;
	}, [auth.isValid, navigate]);
	return <>
		{children}
	</>

}
