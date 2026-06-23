import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/AccountPage.css';

function AccountPage() {
  const navigate = useNavigate();
  
  const [user, setUser] = useState({
    name: '',
    enterprise: '',
    email: '',
    createdAt: '',
    phone: '',
    carsCount: 0
  });
  
  const [diagnostics, setDiagnostics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [activeSessions, setActiveSessions] = useState([]);
  const [completedSessions, setCompletedSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({ ...user });
  const [saveLoading, setSaveLoading] = useState(false);
  
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');

  const checkAuth = () => {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    if (!token) {
      navigate('/login', { replace: true });
      return null;
    }
    return token;
  };

  const apiRequest = async (config) => {
    try {
      const response = await axios(config);
      return response;
    } catch (err) {
      if (err.response && err.response.status === 401) {
        console.warn('Токен истёк! Перенаправление на логин...');
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        navigate('/login', { replace: true });
        throw new Error('Token expired');
      }
      throw err;
    }
  };

  useEffect(() => {
    fetchUserData();
    fetchSessions();
  }, [navigate]);

  const fetchUserData = async () => {
    const token = checkAuth();
    if (!token) return;

    try {
      const response = await apiRequest({
        method: 'get',
        url: 'http://localhost:8080/api/account/me',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const dateObj = new Date(response.data.createdAt);
      const formattedDate = dateObj.toLocaleDateString('ru-RU');

      let formattedPhone = response.data.phone || "не указан";
      if (formattedPhone !== "не указан" && formattedPhone.length >= 10) {
        const digits = formattedPhone.replace(/\D/g, '');
        if (digits.startsWith('7') || digits.startsWith('8')) {
          const d = digits.substring(1);
          if (d.length >= 10) {
            formattedPhone = `+7 (${d.substring(0, 3)}) ${d.substring(3, 6)}-${d.substring(6, 8)}-${d.substring(8, 10)}`;
          }
        } else {
          formattedPhone = `+${digits}`;
        }
      }

      const userData = {
        name: response.data.name,
        enterprise: response.data.enterprise,
        email: response.data.email,
        createdAt: formattedDate,
        phone: formattedPhone,
        carsCount: response.data.carsCount || 0
      };

      setUser(userData);
      setEditData(userData);
      setError(null);
    } catch (err) {
      console.error('Ошибка загрузки данных:', err);
      if (err.message !== 'Token expired') {
        setError('Не удалось загрузить данные профиля.');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchSessions = async () => {
    const token = checkAuth();
    if (!token) return;

    setSessionsLoading(true);

    try {
      const activeRes = await apiRequest({
        method: 'get',
        url: 'http://localhost:8080/api/cars/sessions/active',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setActiveSessions(activeRes.data || []);

      const completedRes = await apiRequest({
        method: 'get',
        url: 'http://localhost:8080/api/cars/sessions/completed',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setCompletedSessions(completedRes.data || []);

    } catch (err) {
      console.error('Ошибка загрузки сессий:', err);
    } finally {
      setSessionsLoading(false);
    }
  };

  const handleEditStart = () => {
    setEditData({ ...user });
    setIsEditing(true);
  };

  const handleEditCancel = () => {
    setEditData({ ...user });
    setIsEditing(false);
  };

  const handleEditSave = async () => {
    const token = checkAuth();
    if (!token) return;

    setSaveLoading(true);
    setPasswordError('');

    try {
      await apiRequest({
        method: 'put',
        url: 'http://localhost:8080/api/account/me',
        data: {
          name: editData.name,
          enterprise: editData.enterprise,
          phone: editData.phone
        },
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setUser({ ...editData });
      setIsEditing(false);
      alert('Данные профиля успешно обновлены!');
    } catch (err) {
      setPasswordError('Ошибка при сохранении: ' + err.message);
    } finally {
      setSaveLoading(false);
    }
  };

  const handlePasswordChangeStart = () => {
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setPasswordError('');
    setPasswordSuccess('');
    setIsChangingPassword(true);
  };

  const handlePasswordChangeCancel = () => {
    setIsChangingPassword(false);
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setPasswordError('');
    setPasswordSuccess('');
  };

  const handlePasswordSave = async () => {
    const token = checkAuth();
    if (!token) return;

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError('Новые пароли не совпадают!');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      setPasswordError('Пароль должен быть не менее 6 символов!');
      return;
    }

    setSaveLoading(true);
    setPasswordError('');

    try {
      await apiRequest({
        method: 'put',
        url: 'http://localhost:8080/api/account/update-security',
        data: {
          currentPassword: passwordData.currentPassword,
          newPassword: passwordData.newPassword
        },
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setPasswordSuccess('Пароль успешно изменён!');
      setIsChangingPassword(false);
      setTimeout(() => setPasswordSuccess(''), 3000);
    } catch (err) {
      setPasswordError('Ошибка при смене пароля: ' + err.response?.data || err.message);
    } finally {
      setSaveLoading(false);
    }
  };

const handleContinueSession = async (session) => {
  const token = checkAuth();
  if (!token) return;
  
  try {
    const sessionRes = await apiRequest({
      method: 'get',
      url: `http://localhost:8080/api/cars/sessions/${session.sessionId}`,
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const sessionData = sessionRes.data;

    console.log('Продолжение сессии:', sessionData);

    navigate('/diagnosis', { 
      state: { 
        sessionData: {
          sessionId: sessionData.sessionId,
          carId: sessionData.carId,
          carBrand: sessionData.carBrand,
          carModel: sessionData.carModel,
          carYear: sessionData.carYear,
          carEngine: sessionData.carEngine || 'Не указан',
          carEquipment: sessionData.carEquipment || 'Не указана',
          carGeneration: sessionData.carGeneration || 'Не указано',
          manualAvailable: sessionData.manualAvailable || false,
          manualType: sessionData.manualType || 'NONE',
          manualStatus: sessionData.manualStatus || getManualStatusText(sessionData.manualType),
          status: sessionData.status || 'ACTIVE'
        }
      } 
    });
  } catch (err) {
    console.error('Ошибка загрузки сессии:', err);
    alert('Ошибка при загрузке сессии: ' + err.message);
  }
};

  const handleCompleteSession = async (sessionId) => {
    if (!window.confirm('Завершить эту сессию диагностики?')) return;
    
    const token = checkAuth();
    if (!token) return;

    try {
      await apiRequest({
        method: 'post',
        url: `http://localhost:8080/api/cars/sessions/${sessionId}/complete`,
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      alert('Сессия завершена!');
      fetchSessions();
    } catch (err) {
      alert('Ошибка при завершении сессии: ' + err.message);
    }
  };

  const handleDownloadReport = async (sessionId) => {
    const token = checkAuth();
    if (!token) return;

    try {
      const res = await apiRequest({
        method: 'get',
        url: `http://localhost:8080/api/cars/sessions/${sessionId}/download`,
        headers: { 'Authorization': `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `diagnosis_${sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Ошибка при скачивании: ' + err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    navigate('/login', { replace: true });
  };

  const getManualStatusText = (manualType) => {
    if (!manualType || manualType === 'NONE') {
      return 'Специализированный мануал не найден. Диагностика проводится по общим техническим регламентам.';
    }
    switch (manualType) {
      case 'SPECIFIC':
        return 'Загружен мануал для конкретной модели. Диагностика проводится с учетом спецификации производителя.';
      case 'BRAND_COMMON':
        return 'Загружен общий мануал бренда. Диагностика проводится с учетом технических данных марки.';
      case 'GENERAL':
        return 'Используется общий мануал для всех автомобилей. Диагностика проводится по базовым регламентам.';
      default:
        return 'Мануал не найден';
    }
  };

  if (loading || sessionsLoading) {
    return (
      <>
        <Navbar />
        <div className="container" style={{ marginTop: '100px', textAlign: 'center' }}>
          Загрузка данных профиля...
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="container" style={{ marginTop: '100px', textAlign: 'center', color: '#dc3545' }}>
          <h3>Ошибка загрузки</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Попробовать снова
          </button>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="account-page">
        <div className="account-container">
          
          {}
          <div className="account-card">
            <div className="account-header">
              <div className="account-info">
                <dl className="account-dl">
                  <div className="dl-row">
                    <dt>Аккаунт:</dt>
                    <dd>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editData.name}
                          onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                          className="form-control"
                          style={{ width: '200px' }}
                        />
                      ) : (
                        user.name || 'Не указано'
                      )}
                    </dd>
                  </div>
                  <div className="dl-row">
                    <dt>Предприятие:</dt>
                    <dd>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editData.enterprise}
                          onChange={(e) => setEditData({ ...editData, enterprise: e.target.value })}
                          className="form-control"
                          style={{ width: '200px' }}
                        />
                      ) : (
                        user.enterprise || 'Не указано'
                      )}
                    </dd>
                  </div>
                  <div className="dl-row">
                    <dt>Эл. почта:</dt>
                    <dd>{user.email || 'Не указано'}</dd>
                  </div>
                  <div className="dl-row">
                    <dt>Дата регистрации:</dt>
                    <dd>{user.createdAt || 'Не указано'}</dd>
                  </div>
                  <div className="dl-row">
                    <dt>Количество а/м:</dt>
                    <dd>{user.carsCount}</dd>
                  </div>
                  <div className="dl-row">
                    <dt>Номер телефона:</dt>
                    <dd>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editData.phone}
                          onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                          className="form-control"
                          style={{ width: '200px' }}
                        />
                      ) : (
                        user.phone
                      )}
                    </dd>
                  </div>
                </dl>
              </div>
              <div className="account-avatar-wrapper">
                <img src="/images/account.png" alt="Avatar" className="account-avatar" />
              </div>
            </div>
            <div className="account-buttons">
              {isEditing ? (
                <>
                  <button 
                    className="btn-edit" 
                    onClick={handleEditSave}
                    disabled={saveLoading}
                    style={{ backgroundColor: '#28a745', color: 'white' }}
                  >
                    {saveLoading ? 'Сохранение...' : 'Сохранить'}
                  </button>
                  <button 
                    className="btn-edit" 
                    onClick={handleEditCancel}
                    disabled={saveLoading}
                    style={{ backgroundColor: '#6c757d', color: 'white' }}
                  >
                    Отмена
                  </button>
                </>
              ) : (
                <>
                  <button className="btn-edit" onClick={handleEditStart}>
                    Изменить данные
                  </button>
                  <button 
                    className="btn-edit" 
                    onClick={handlePasswordChangeStart}
                    style={{ backgroundColor: '#17a2b8', color: 'white' }}
                  >
                    Безопасность
                  </button>
                </>
              )}
              <button 
                className="btn-logout" 
                onClick={handleLogout}
                style={{ backgroundColor: '#dc3545', color: 'white' }}
              >
                Выйти
              </button>
            </div>

            {}
            {isChangingPassword && (
              <div style={{
                marginTop: '20px',
                padding: '20px',
                backgroundColor: '#f8f9fa',
                borderRadius: '5px'
              }}>
                <h4 style={{ marginTop: 0 }}>Смена пароля</h4>
                {passwordError && (
                  <div style={{ color: '#dc3545', marginBottom: '10px' }}>{passwordError}</div>
                )}
                {passwordSuccess && (
                  <div style={{ color: '#28a745', marginBottom: '10px' }}>{passwordSuccess}</div>
                )}
                <div style={{ marginBottom: '10px' }}>
                  <label>Текущий пароль:</label>
                  <input
                    type="password"
                    value={passwordData.currentPassword}
                    onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                    className="form-control"
                    style={{ width: '100%', marginTop: '5px' }}
                  />
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <label>Новый пароль:</label>
                  <input
                    type="password"
                    value={passwordData.newPassword}
                    onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                    className="form-control"
                    style={{ width: '100%', marginTop: '5px' }}
                  />
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <label>Подтверждение пароля:</label>
                  <input
                    type="password"
                    value={passwordData.confirmPassword}
                    onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                    className="form-control"
                    style={{ width: '100%', marginTop: '5px' }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    onClick={handlePasswordSave}
                    disabled={saveLoading}
                    style={{
                      padding: '8px 15px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer'
                    }}
                  >
                    {saveLoading ? 'Сохранение...' : 'Сохранить пароль'}
                  </button>
                  <button 
                    onClick={handlePasswordChangeCancel}
                    style={{
                      padding: '8px 15px',
                      backgroundColor: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer'
                    }}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}
          </div>

          {}
          <div className="account-card">
            <h3 className="card-title">🟢 Активные сессии ({activeSessions.length})</h3>
            {activeSessions.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#777', padding: '20px' }}>
                Нет активных сессий диагностики.
              </p>
            ) : (
              activeSessions.map(session => (
                <div key={session.sessionId} className="session-item" style={{
                  padding: '15px',
                  borderBottom: '1px solid #eee',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '10px'
                }}>
                  <div>
                    <strong>{session.carBrand} {session.carModel}</strong> ({session.carYear})
                    <br />
                    <small style={{color: '#666'}}>
                      Сессия #{session.sessionId} • 
                      Создана: {new Date(session.createdAt).toLocaleDateString('ru-RU')}
                    </small>
                    {session.manualAvailable && (
                      <div style={{color: '#4caf50', fontSize: '12px', marginTop: '5px'}}>
                        ✓ Мануал подключен
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                      onClick={() => handleContinueSession(session)}
                      style={{
                        padding: '8px 15px',
                        backgroundColor: '#4caf50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                      }}
                    >
                      Продолжить
                    </button>
                    <button 
                      onClick={() => handleCompleteSession(session.sessionId)}
                      style={{
                        padding: '8px 15px',
                        backgroundColor: '#2196f3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                      }}
                    >
                      Завершить
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {}
          <div className="account-card">
            <h3 className="card-title">🔵 Диагностические карты ({completedSessions.length})</h3>
            {completedSessions.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#777', padding: '20px' }}>
                Диагностических карт нет. Пройдите диагностику, чтобы они появились здесь.
              </p>
            ) : (
              completedSessions.map(session => (
                <div key={session.sessionId} className="session-item" style={{
                  padding: '15px',
                  borderBottom: '1px solid #eee',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '10px'
                }}>
                  <div>
                    <strong>{session.carBrand} {session.carModel}</strong> ({session.carYear})
                    <br />
                    <small style={{color: '#666'}}>
                      Сессия #{session.sessionId} • 
                      Завершена: {session.completedAt ? new Date(session.completedAt).toLocaleDateString('ru-RU') : 'Неизвестно'}
                    </small>
                  </div>
                  <button 
                    onClick={() => handleDownloadReport(session.sessionId)}
                    style={{
                      padding: '8px 15px',
                      backgroundColor: '#607d8b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer'
                    }}
                  >
                    📥 Скачать отчёт
                  </button>
                </div>
              ))
            )}
          </div>

          {}
          <div className="account-card car-list">
            <h3 className="card-title">Список автомобилей:</h3>
            {user.carsCount === 0 ? (
              <p style={{ textAlign: 'center', color: '#777', padding: '20px' }}>
                У вас пока нет добавленных автомобилей.
              </p>
            ) : (
              <div className="car-item">
                <span className="car-name">Toyota Mark 2 (Пример)</span>
                <div className="car-buttons">
                  <button className="btn-small btn-small-edit">Изменить</button>
                  <button className="btn-small btn-small-delete">Удалить</button>
                </div>
              </div>
            )}
          </div>

          <div className="footer-text">
            Стань одним из тех, кто изменит мир.
          </div>
        </div>
      </div>
    </>
  );
}

export default AccountPage;
