import React, { createContext, useEffect, useState } from "react";
import axios from "axios";

export type AuthInfo = {
	access_token: string | null,
	set_access_token: React.Dispatch<React.SetStateAction<string | null>> | null,
	isValid: boolean,
	setisValid: React.Dispatch<React.SetStateAction<boolean>> | null,
}

export const AuthContext = createContext<AuthInfo>({ access_token: null, isValid: false, set_access_token: null, setisValid: null });
const AxiosClient = axios.create({
	baseURL: "http://127.0.0.1:8000"
});


async function AuthenticateUser(username: string, password: string) {
	// TODO: Create custom hook?
	const response = await AxiosClient.post("/api/login", {
		"username": username,
		"password": password,
	});
	if (response.status == 200) {

		return true;
	}

}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
	const [access_token, set_access_token] = useState<string | null>(() => localStorage.getItem("goback_access_token"));
	const [isValid, setisValid] = useState<boolean>(false);
	useEffect(() => {
		if (access_token !== null) {
			localStorage.setItem("goback_access_token", access_token);
			AxiosClient.get("/api/validate", {
				method: "GET",
				headers: {
					"Authorization": `Bearer ${access_token}`
				}
			}).then((response) => setisValid(response.status == 204));

		}
	}, [access_token]);

	return <>
		<AuthContext.Provider value={{ access_token: access_token, isValid: isValid, setisValid: setisValid, set_access_token: set_access_token }}>
			{children}
		</AuthContext.Provider>

	</>



}
