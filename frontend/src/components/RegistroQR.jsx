import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const URL_API_REGISTRO = `${process.env.REACT_APP_API_URL}/asistencias`;

function RegistroQR() {
  const [searchParams] = useSearchParams();
  const [idInscripcion, setIdInscripcion] = useState('');
  const [registrado, setRegistrado] = useState(false);
  const [error, setError] = useState('');
  const [nomMateria, setNomMateria] = useState('');
  const [comision, setComision] = useState('');

  const token = searchParams.get('token');
  const idSesion = searchParams.get('id_sesion');
  const navegar = useNavigate();

  useEffect(() => {
  if (idSesion) {
    axios.get(`${process.env.REACT_APP_API_URL}/sesiones/${idSesion}/datos_materia`)
      .then(res => {
        setNomMateria(res.data.nombre_materia);
        setComision(res.data.comision);
      })
      .catch(() => {
        setNomMateria('');
        setComision('');
      });
  }
}, [idSesion]);



  const registrar = async () => {
    setError('');
    setRegistrado(false);

    if (!idInscripcion || !idSesion) {
      setError('Falta el ID de inscripción o sesión');
      return;
    }

    const body = {
      id_sesion: parseInt(idSesion, 10),
      id_inscripcion: parseInt(idInscripcion, 10),
      token
    };

    try {
      await axios.post(URL_API_REGISTRO, body);
      setRegistrado(true);
      setIdInscripcion('');
    } catch (e) {
      setError('Error al registrar: ' + (e.response?.data?.error || e.message));
    }
  };

  return (
    <div className="p-8 max-w-xl mx-auto bg-white border border-black rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Registro de Asistencia</h2>

      {idSesion ? (
        <>
          <p className="mb-4 text-gray-700">
            Estás registrando asistencia para la sesión <strong>#{idSesion}</strong>
          </p>
          <p className="mb-4 text-gray-700">
            <strong>{nomMateria} (Comisión {comision})</strong>
          </p>

          <label className="block mb-2 font-semibold">ID de inscripción:</label>
          <input
            type="number"
            value={idInscripcion}
            onChange={e => setIdInscripcion(e.target.value)}
            className="border border-black rounded p-2 mb-4 w-full"
            placeholder="Ingresá tu ID de inscripción"
          />

          <button
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            onClick={registrar}
          >
            Registrar Asistencia
          </button>

          {registrado && (
            <div className="mt-4 text-green-600 font-semibold">
              ✅ Asistencia registrada con éxito.
            </div>
          )}
        </>
      ) : (
        <p className="text-red-600">Error: faltan datos en la URL</p>
      )}

      {error && <p className="text-red-600 mt-4">{error}</p>}

      <button
        className="mt-6 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        onClick={() => navegar(-1)}
      >
        Volver
      </button>
    </div>
  );
}

export default RegistroQR;
