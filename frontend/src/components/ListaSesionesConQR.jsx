import React, { useEffect, useState } from 'react';
import axios from 'axios';

const URL_API_SESIONES = 'http://localhost:5000/api/sesiones/listar';

function ListaSesionesConQR() {
  const [sesiones, setSesiones] = useState([]);
  const [error, setError] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [qrUrl, setQrUrl] = useState('');
  const [asistenciasDetalle, setAsistenciasDetalle] = useState({});
  const [mostrarDetalle, setMostrarDetalle] = useState(null);

  useEffect(() => {
    axios.get(URL_API_SESIONES)
      .then(res => setSesiones(res.data))
      .catch(() => setError('Error al cargar sesiones'));
  }, []);

  const abrirModalQR = (sesion) => {
    const nombreArchivoQR = `qr_${sesion.id_materia}_${sesion.comision}_${sesion.id_sesion}.png`;
    const url = `http://localhost:5000/api/qr/${nombreArchivoQR}`;
    setQrUrl(`${url}?t=${Date.now()}`);
    setModalVisible(true);
  };

  const cerrarModal = () => {
    setModalVisible(false);
    setQrUrl('');
  };

  const regenerarQR = async (idSesion) => {
    try {
      const resp = await axios.put(`http://localhost:5000/api/sesiones/${idSesion}/regenerar_qr`);
      alert(resp.data.message);
      setQrUrl(prevUrl => prevUrl.split('?')[0] + `?t=${Date.now()}`);
    } catch (e) {
      alert('Error al regenerar QR: ' + (e.response?.data?.error || e.message));
    }
  };

  const toggleDetalle = async (idSesion) => {
    if (mostrarDetalle === idSesion) {
      setMostrarDetalle(null);
      return;
    }
    try {
      const resp = await axios.get(`http://localhost:5000/api/sesiones/${idSesion}/detalle_asistencias`);
      setAsistenciasDetalle(prev => ({ ...prev, [idSesion]: resp.data }));
      setMostrarDetalle(idSesion);
    } catch (e) {
      alert('Error al obtener detalles de asistencia');
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Sesiones creadas</h2>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      <div className="bg-white border border-black rounded-lg shadow-md overflow-x-auto">
        <table className="min-w-full border-collapse">
          <thead>
            <tr>
              <th className="border border-black p-2">ID Sesión</th>
              <th className="border border-black p-2">Materia</th>
              <th className="border border-black p-2">Comisión</th>
              <th className="border border-black p-2">Fecha y Hora</th>
              <th className="border border-black p-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {sesiones.map(sesion => (
              <React.Fragment key={sesion.id_sesion}>
                <tr>
                  <td className="border border-black p-2">{sesion.id_sesion}</td>
                  <td className="border border-black p-2">{sesion.id_materia} ({sesion.nombre_materia})</td>
                  <td className="border border-black p-2">{sesion.comision}</td>
                  <td className="border border-black p-2">{new Date(sesion.fecha_hora).toLocaleString()}</td>
                  <td className="border border-black p-2 space-y-1 flex flex-col items-center">
                    <button
                      onClick={() => abrirModalQR(sesion)}
                      className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                    >
                      Ver QR
                    </button>
                    <button
                      onClick={() => regenerarQR(sesion.id_sesion)}
                      className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600"
                    >
                      Regenerar QR
                    </button>
                    <button
                      onClick={() => toggleDetalle(sesion.id_sesion)}
                      className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                    >
                      Ver Asistencias
                    </button>
                  </td>
                </tr>
                {mostrarDetalle === sesion.id_sesion && asistenciasDetalle[sesion.id_sesion] && (
                  <tr>
                    <td colSpan="5" className="border-t border-black p-4 bg-gray-100">
                      <h4 className="font-semibold mb-2">Estudiantes y asistencia:</h4>
                      <table className="w-full mt-2 border border-gray-400">
                        <thead>
                          <tr className="bg-gray-200 text-left">
                            <th className="border p-2">Estudiante</th>
                            <th className="border p-2 text-center">ID Inscripción</th>
                            <th className="border p-2 text-center">Estado</th>
                            <th className="border p-2 text-center">Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {asistenciasDetalle[sesion.id_sesion].map(alumno => (
                            <tr key={alumno.id_inscripcion} className="bg-white">
                              <td className="border p-2">{alumno.alumno}</td>
                              <td className="border p-2 text-center">{alumno.id_inscripcion}</td>
                              <td className="border p-2 text-center font-bold">
                                {alumno.tiene_asistencia ? 'Presente' : 'Ausente'}
                              </td>
                              <td className="border p-2 text-center">{alumno.total_asistencias}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {modalVisible && (
        <div
          onClick={cerrarModal}
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            zIndex: 10000
          }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              maxWidth: '320px',
              textAlign: 'center',
              boxShadow: '0 2px 10px rgba(0,0,0,0.3)'
            }}
          >
            <h3 className="mb-4 font-bold">Código QR de la sesión</h3>
            <img
              src={qrUrl}
              alt="Código QR"
              style={{ maxWidth: '100%' }}
              onError={(e) => e.target.src = ''}
            />
            <button
              onClick={cerrarModal}
              className="mt-4 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ListaSesionesConQR;
