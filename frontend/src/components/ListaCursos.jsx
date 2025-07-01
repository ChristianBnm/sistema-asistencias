import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const URL_API = 'http://localhost:5000/api/cursos'

function CursosView() {
  const [materias, setMaterias] = useState([])
  const [cargando, setCargando] = useState(true)
  const navegar = useNavigate()

  useEffect(() => {
    axios.get(URL_API)
      .then(respuesta => {
        setMaterias(respuesta.data)
        setCargando(false)
      })
      .catch(error => {
        console.error('Error al cargar cursos:', error)
        setCargando(false)
      })
  }, [])

  if (cargando) return <p className="text-center mt-10">Cargando cursos...</p>

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <button
        className="mb-6 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition"
        onClick={() => navegar(-1)}
      >
        ← Volver
      </button>

      <h1 className="text-2xl font-bold mb-6">Listado de materias y estudiantes</h1>

      {materias.map((materia, indice) => (
        <div
          key={indice}
          className="mb-8 bg-white rounded-xl shadow p-6"
        >
          <h2 className="text-xl font-semibold mb-4">{materia.nombre_materia}</h2>

          {/* Contenedor de scroll solo vertical */}
          <div className="relative max-h-96 overflow-y-auto rounded border border-gray-300 scroll-smooth">
            <table className="min-w-full text-left border-collapse">
              <thead className="sticky top-0 bg-gray-100 z-10">
                <tr>
                  <th className="p-2 border border-gray-300">Alumno</th>
                  <th className="p-2 border border-gray-300">Identificación</th>
                  <th className="p-2 border border-gray-300">Legajo</th>
                  <th className="p-2 border border-gray-300">Comisión</th>
                  <th className="p-2 border border-gray-300">Estado</th>
                  <th className="p-2 border border-gray-300">Instancia</th>
                </tr>
              </thead>
              <tbody>
                {materia.alumnos.map(alumno => (
                  <tr key={alumno.id_inscripcion} className="border-t border-gray-300">
                    <td className="p-2 border border-gray-300">{alumno.alumno}</td>
                    <td className="p-2 border border-gray-300">{alumno.identificacion}</td>
                    <td className="p-2 border border-gray-300">{alumno.legajo}</td>
                    <td className="p-2 border border-gray-300">{alumno.comision}</td>
                    <td className="p-2 border border-gray-300">{alumno.estado_ins}</td>
                    <td className="p-2 border border-gray-300">{alumno.instancia}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}

export default CursosView
