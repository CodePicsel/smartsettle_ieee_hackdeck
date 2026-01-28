import { useState } from 'react'
import './App.css'
import Register from './Components/Register'
import { Outlet } from 'react-router-dom'

function App() {

//   useEffect(() => {
//   const token = sessionStorage.getItem("access_token");
//   if (!token) return;

//   fetch("http://localhost:8000/auth/me", {
//     headers: { Authorization: `Bearer ${token}` }
//   })
//     .then(res => res.json())
//     .then(data => {
//       dispatch(authLogin({ user: data.user }));
//     });
// }, []);


  return (
    <div className='h-screen'>
      <Outlet />
    </div>
  )
}

export default App
