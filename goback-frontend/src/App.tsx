import { BrowserRouter, Routes, Route } from "react-router-dom"
import "./App.css";
import HomePage from "./pages/HomePage.tsx";
import SignupPage from "./pages/SignupPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import DashboardPage from "./pages/DashboardPage.tsx";
import AuthProvider from "./components/AuthContext.tsx";
import AuthenticatedRoute from "./components/AuthenticatedRoute.tsx";
import CreationPage from "./pages/CreationPage.tsx";


function App() {
	return <>

		<BrowserRouter>
			<AuthProvider>
				<Routes>
					<Route path="/" element={<HomePage />} />
					<Route path="/login" element={<LoginPage />} />
					<Route path="/signup" element={<SignupPage />} />
					<Route path="/dashboard" element={<AuthenticatedRoute><DashboardPage /></AuthenticatedRoute>} />
					<Route path="/create" element={<AuthenticatedRoute><CreationPage /></AuthenticatedRoute>} />
				</Routes>
			</AuthProvider>
		</BrowserRouter>
	</>

}

export default App
