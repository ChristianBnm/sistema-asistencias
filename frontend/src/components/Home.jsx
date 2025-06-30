import React from 'react'
import { useNavigate } from 'react-router-dom'

function Home() {
  const navegar = useNavigate()

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Bienvenido a la Página Principal</h1>

      {/* Mensaje de aviso */}
      <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded mb-6 shadow-sm">
        <p className="font-medium">📢 Página en desarrollo</p>
        <p className="text-sm">Sistema para registro de asistencias de los estudiantes</p>
      </div>

      {/* Botones */}
      <div className="flex flex-col gap-4">
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
          onClick={() => navegar('/cursos')}
        >
          Ir al Listado de Cursos
        </button>

        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
          onClick={() => navegar('/crear-sesion')}
        >
          Crear sesión
        </button>

        <button
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
          onClick={() => navegar('/sesiones')}
        >
          Ver sesiones y QRs
        </button>
      </div>
    </div>
  )
}

export default Home
