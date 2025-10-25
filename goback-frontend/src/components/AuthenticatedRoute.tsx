import { useContext, useEffect } from "react";
import { AuthContext } from "./AuthContext";
import { useNavigate } from "react-router-dom";

export default function AuthenticatedRoute({children}: {children: React.ReactNode}) {
    const token = useContext(AuthContext);
    const navigate = useNavigate();
    useEffect(() => {
        if (token === null)
            navigate("/login");

    }, []);

    return children;
}
