import React, { createContext } from "react";

type AuthInfo = {
	access_token: string | undefined,
	expire: number | undefined
}

const AuthContext = createContext<AuthInfo>({ access_token: undefined, expire: undefined });


export default function AuthProvider({ children }: { children: React.ReactNode }) {
	return <>
		<AuthContext.Provider value={{ access_token: "something", expire: 123 }}>
			{children}
		</AuthContext.Provider>

	</>



}
