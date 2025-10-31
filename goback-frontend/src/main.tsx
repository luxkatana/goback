import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Home from './routes/Home'
import Login from './routes/Login'
import Signup from './routes/Signup'
import { Provider } from './components/ui/provider'
import Dashboard from "./routes/Dashboard";
import ProtectedComponent from './components/ProtectedComponent'


const router = createBrowserRouter([
	{ path: "/", element: <Home /> },
	{ path: "/login", element: <Login /> },
	{ path: "/signup", element: <Signup /> },
	{ path: "/dashboard", element: <ProtectedComponent><Dashboard /></ProtectedComponent> }

])

createRoot(document.getElementById('root')!).render(
	<StrictMode>
		<Provider>
			<RouterProvider router={router} />
		</Provider>
	</StrictMode>,
)
