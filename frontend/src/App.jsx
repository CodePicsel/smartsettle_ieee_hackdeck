import { useState } from 'react'
import './App.css'
import Login from './Components/login'
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
