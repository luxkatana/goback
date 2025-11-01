import React, { createContext, useEffect, useState } from "react";
import axios, { AxiosError } from "axios";

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


export async function AuthenticateUser(username: string, password: string, context: AuthInfo) {
	try {
		const response = await AxiosClient.post("/api/login", {
			"username": username,
			"password": password,
		}, {
			headers: {
				"Content-Type": "application/x-www-form-urlencoded"
			}

		});
		context.set_access_token!(response.data.access_token);
		context.setisValid!(true);
		return true;
	} catch (error: AxiosError | any) {
		return false
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
			}).then(() => setisValid(true))
				.catch(() => setisValid(false));

		}
	}, [access_token]);

	return <>
		<AuthContext.Provider value={{ access_token: access_token, isValid: isValid, setisValid: setisValid, set_access_token: set_access_token }}>
			{children}
		</AuthContext.Provider>

	</>



}
