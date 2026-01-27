import { useState } from 'react'
import './App.css'
import LoginWithOtp from './Components/LoginO'
import Register from './Components/Register'
import { Outlet } from 'react-router-dom'

function App() {

  return (
    <div className='h-screen'>
      <Outlet />
    </div>
  )
}

export default App
