import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { Provider } from 'react-redux'
import store from './app/store.js'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Registerpage from './pages/Registerpage.jsx'
import Login from './Components/login.jsx'
import AuthLayout from './Layout/authLayout.jsx'
import CreateOffer from './Components/CreateOffer.jsx'
import AuthLoader from './Layout/AuthLoader.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <AuthLoader>
        <App />
      </AuthLoader>
    ),
    children: [
      {
        path: '/',
        element: <AuthLayout authentication={false}>
          <Home />
        </AuthLayout>
      },
      {
      path: '/register',
      element: (
        <AuthLayout authentication={false}>
          <Registerpage />
        </AuthLayout>
      )
      },
      {
      path: '/login',
      element: (
        <AuthLayout authentication={false}>
          <Login />
        </AuthLayout>
      )
      },
      {
        path: '/offers/create',
        element: (
          <AuthLayout authentication={false}>
            <CreateOffer />
          </AuthLayout>
        )
      }
    ]
  }
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  </StrictMode>,
)
