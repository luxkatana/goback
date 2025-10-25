import { createContext, useState } from "react";


export interface AuthContextProperties {
	token: string | null,
	setToken: React.Dispatch<React.SetStateAction<string | null>>
}
export const AuthContext: React.Context<AuthContextProperties | null> = createContext<AuthContextProperties | null>(null);



export default function AuthProvider({ children }: { children: React.ReactNode }) {
	const [token, setToken] = useState(() => localStorage.getItem("goback_access_token"));
	return <AuthContext.Provider value={{ token: token, setToken: setToken }}>
		{children}
	</AuthContext.Provider>

}


