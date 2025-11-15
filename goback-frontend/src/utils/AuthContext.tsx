import React, { createContext, useEffect, useState } from "react";
import axios, { AxiosError } from "axios";
import toast from "react-hot-toast";

export type AuthInfo = {
	access_token: string | null,
	set_access_token: React.Dispatch<React.SetStateAction<string | null>> | null,
	isValid: boolean,
	setisValid: React.Dispatch<React.SetStateAction<boolean>> | null,
	username: string | null,
	loading?: boolean
}

export const AuthContext = createContext<AuthInfo>({ access_token: null, isValid: false, set_access_token: null, setisValid: null, username: null });
console.info(import.meta.env);
const AxiosClient = axios.create({
	baseURL: import.meta.env.DEV === true ? "http://127.0.0.1:8000" : ""
});

export async function GetJobs(context: AuthInfo) {
	try {
		const response = await AxiosClient.get("/api/jobs", {
			headers: {
				"Authorization": `Bearer ${context.access_token}`
			}
		});
		return {
			success: true,
			...response.data
		}
	} catch (e: any) {
		toast.error(`Error when getting jobs: ${e}`);
		return {
			success: false,
		};
	}

}

export async function RegisterUser(username: string, email: string, password: string, context: AuthInfo) {
	try {
		const response = await AxiosClient.post("/api/signup", {
			"username": username,
			"password": password,
			"email": email
		}, {
			headers: {
				"Content-Type": "application/json"
			}

		});
		const access_token = response.data.access_token;
		context.set_access_token!(access_token);
		context.setisValid!(true);
		return true;

	} catch (e: AxiosError | any) {
		if (e.status === 400) {
			toast.error("Error, Username already exists :(");

		} else
			toast.error(`Error when registering: ${e}`);
		return false;
	}


}
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
	} catch (_: AxiosError | any) {
		return false
	}
}
export async function CreateBackupCall(url: string, context: AuthInfo) {
	const response = await AxiosClient.post("/api/scrape", {
		"url": url
	}, {
		headers: {
			"Authorization": `Bearer ${context.access_token!}`
		}
	});
	return response.data.job_id
}
export async function FetchJobInfo(job_id: number, auth_context: AuthInfo) {
	const response = await AxiosClient.get(`/api/job?job_id=${job_id}`, {
		headers: {
			"Authorization": `Bearer ${auth_context.access_token!}`
		}
	})
	return response.data;
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
	const [access_token, set_access_token] = useState<string | null>(() => localStorage.getItem("goback_access_token"));
	const [username, setusername] = useState<string | null>(null);
	const [isValid, setisValid] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(true);
	useEffect(() => {
		const validateToken = async () => {
			if (access_token !== null) {
				try {
					const response = await AxiosClient.get("/api/validate", {
						method: "GET",
						headers: {
							"Authorization": `Bearer ${access_token}`
						}
					});
					localStorage.setItem("goback_access_token", access_token);
					setusername(response.data.username);
					setisValid(true)
				} catch (e: AxiosError | any) {
					localStorage.removeItem("goback_access_token");
					setisValid(false);
				}
			}
			setLoading(false);
		}
		validateToken();

	}, [access_token]);

	return <>
		<AuthContext.Provider value={{
			access_token:
				access_token,
			isValid: isValid,
			setisValid: setisValid,
			set_access_token: set_access_token,
			username: username, loading: loading
		}}>
			{children}
		</AuthContext.Provider>

	</>



}
