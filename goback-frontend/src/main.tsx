import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Home from './routes/Home'
import Login from './routes/Login'
import Signup from './routes/Signup'
import Dashboard from "./routes/Dashboard";
import ProtectedComponent from './components/ProtectedComponent'
import AuthProvider from './utils/AuthContext'
import { Toaster } from 'react-hot-toast'
import ErrorPage from './routes/ErrorPage'
import CreateBackupPage from './routes/CreateBackupPage'
import LogoutRoute from './routes/LogoutRoute'
import JobViewer from './routes/JobViewer'
import ListJobs from './routes/ListJobs'
import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import { ColorModeProvider } from './components/ui/color-mode'

export const routes = [
	{ path: "/", element: <Home />, name: "Home" },
	{ path: "/login", element: <Login />, name: "Login" },
	{ path: "/signup", element: <Signup />, name: "Sign up" },
	{ path: "/dashboard", element: <ProtectedComponent><Dashboard /></ProtectedComponent>, name: "Dashboard" },
	{ path: "/create", element: <ProtectedComponent><CreateBackupPage /></ProtectedComponent>, name: "Create an archive" },
	{ path: "/logout", element: <ProtectedComponent><LogoutRoute /></ProtectedComponent>, name: "Logout" },
	{ path: "/job", element: <ProtectedComponent><JobViewer /></ProtectedComponent> },
	{ path: "/jobs", element: <ProtectedComponent><ListJobs /></ProtectedComponent>, name: "My jobs" },
	{ path: "*", element: <ErrorPage /> }
]

const router = createBrowserRouter(routes);
function Layout({ children }: { children: React.ReactNode }) {
	return <>
		<ChakraProvider value={defaultSystem}>
			<ColorModeProvider>{children}</ColorModeProvider>

		</ChakraProvider>

	</>

}

createRoot(document.getElementById('root')!).render(
	<StrictMode>
		<AuthProvider>
			<Layout>
				<Toaster />
				<RouterProvider router={router} />
			</Layout>
		</AuthProvider>
	</StrictMode>,
)
