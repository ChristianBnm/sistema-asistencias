import React, { useState, useEffect } from 'react';
import axios from 'axios';

const URL_API_SESIONES = 'http://localhost:5000/api/sesiones';
const URL_API_MATERIAS = 'http://localhost:5000/api/materias';

function CrearSesion() {
  const [materias, setMaterias] = useState([]);
  const [idMateria, setIdMateria] = useState('');
  const [comisiones, setComisiones] = useState([]);
  const [comision, setComision] = useState('');
  const [error, setError] = useState('');
  const [exito, setExito] = useState(false);

  useEffect(() => {
    axios.get(URL_API_MATERIAS)
      .then(res => setMaterias(res.data))
      .catch(() => setError('Error al cargar materias'));
  }, []);

  const crearSesion = async () => {
    setError('');
    setExito(false);
    if (!idMateria || !comision) {
      setError('Por favor, seleccioná materia y comisión');
      return;
    }
    try {
      await axios.post(URL_API_SESIONES, { id_materia: idMateria, comision });
      setExito(true);
      // Limpiar selección para nueva creación
      setIdMateria('');
      setComision('');
      setComisiones([]);
    } catch (e) {
      setError('Error al crear sesión: ' + (e.response?.data?.error || e.message));
    }
  };

  const handleMateriaChange = (e) => {
    const seleccionada = e.target.value;
    setIdMateria(seleccionada);
    setComision('');
    const materiaEncontrada = materias.find(m => m.id_materia === seleccionada);
    setComisiones(materiaEncontrada ? materiaEncontrada.comisiones : []);
  };

  return (
    <div className="p-8 max-w-3xl mx-auto bg-white border border-black rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Crear sesión</h2>

      {error && <p className="text-red-600 mb-4">{error}</p>}
      {exito && <p className="text-green-600 mb-4">Sesión creada correctamente.</p>}

      <label className="block mb-2 font-semibold">Materia:</label>
      <select
        className="border border-black rounded p-2 mb-4 w-full"
        value={idMateria}
        onChange={handleMateriaChange}
      >
        <option value="">-- Seleccioná una materia --</option>
        {materias.map(m => (
          <option key={m.id_materia} value={m.id_materia}>{m.nombre}</option>
        ))}
      </select>

      <label className="block mb-2 font-semibold">Comisión:</label>
      <select
        className="border border-black rounded p-2 mb-4 w-full"
        value={comision}
        onChange={e => setComision(e.target.value)}
        disabled={!comisiones.length}
      >
        <option value="">-- Seleccioná comisión --</option>
        {comisiones.map(c => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>

      <button
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        onClick={crearSesion}
      >
        Crear Sesión
      </button>
    </div>
  );
}

export default CrearSesion;
