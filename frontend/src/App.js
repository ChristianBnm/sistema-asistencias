import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Home from './components/Home'
import ListaCursos from './components/ListaCursos'
import RegistroQR from './components/RegistroQR'
import CrearSesion from './components/CrearSesion'
import ListaSesionesConQR from './components/ListaSesionesConQR'

function App() {
  return (
    <Router>
      {/* Fondo celeste claro para toda la app */}
      <div className="bg-blue-100 min-h-screen">
        
        {/* Header azul oscuro con logo a la derecha */}
        <header className="bg-blue-800 shadow-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto flex justify-end items-center px-6 py-3">
            <Link to="/">
              <img
                src="https://www.undav.edu.ar/landing/img/logo1.png"
                alt="Logo UNDAv"
                className="h-16 cursor-pointer"
              />
            </Link>
          </div>
        </header>

        {/* Contenido principal */}
        <main className="p-8 max-w-5xl mx-auto">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/cursos" element={<ListaCursos />} />
            <Route path="/registro-qr" element={<RegistroQR />} />
            <Route path="/crear-sesion" element={<CrearSesion />} />
            <Route path="/sesiones" element={<ListaSesionesConQR />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
