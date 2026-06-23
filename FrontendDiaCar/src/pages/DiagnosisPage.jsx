import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/DiagnosisPage.css';

function DiagnosisPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const [userMessage, setUserMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionData, setSessionData] = useState(null);
  const [carInfo, setCarInfo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sessionStatus, setSessionStatus] = useState('ACTIVE');
  const [isTyping, setIsTyping] = useState(false);

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const token = checkAuth();
    if (!token) return;

    const sessionId = location.state?.sessionData?.sessionId;
    if (!sessionId) {
      navigate('/diagnosis-setup');
      return;
    }

    const fetchSessionData = async () => {
      try {
        const response = await apiRequest({
          method: 'get',
          url: `http://localhost:8080/api/cars/sessions/${sessionId}`,
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = response.data;
        setSessionData(data);
        setCarInfo({
          carBrand: data.carBrand,
          carModel: data.carModel,
          carYear: data.carYear,
          carEngine: data.carEngine || 'Не указан',
          carEquipment: data.carEquipment || 'Не указана',
          carGeneration: data.carGeneration || 'Не указано',
          manualAvailable: data.manualAvailable || false,
          manualType: data.manualType || 'NONE',
          carImage: data.carImage || '/images/car.png',
          manualStatus: data.manualStatus || getManualStatusText(data.manualType),
          manualPath: data.manualPath
        });
        setSessionStatus(data.status || 'ACTIVE');
        loadMessageHistory(data.sessionId, token);
      } catch (err) {
        console.error('Ошибка загрузки сессии:', err);
        navigate('/diagnosis-setup');
      }
    };

    fetchSessionData();
  }, [location, navigate]);

  const loadMessageHistory = async (sessionId, token) => {
    try {
      const res = await apiRequest({
        method: 'get',
        url: `http://localhost:8080/api/cars/sessions/${sessionId}/messages`,
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const formattedMessages = res.data.map(msg => ({
        messageId: msg.messageId,
        role: msg.role,
        text: msg.content,
        createdAt: msg.createdAt,
        imageUrl: msg.imageUrl,
        pageNumber: msg.pageNumber,
        messageType: msg.messageType || 'TEXT',
        suggestedPages: msg.suggestedPages || []
      }));
      setMessages(formattedMessages);
    } catch (err) {
      console.error('Ошибка загрузки истории:', err);
      if (err.response?.status === 404 && carInfo) {
        setMessages([{
          role: 'ai',
          text: `Сессия начата для автомобиля ${carInfo.carBrand} ${carInfo.carModel} (${carInfo.carYear}). ${carInfo.manualAvailable ? 'Буду использовать техническую документацию.' : 'Буду использовать общие знания.'} Опишите проблему.`,
          suggestedPages: []
        }]);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userMessage.trim() || !sessionData || sessionStatus !== 'ACTIVE') return;
    const token = checkAuth();
    if (!token) return;

    const newUserMessage = userMessage.trim();
    setUserMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await apiRequest({
        method: 'post',
        url: `http://localhost:8080/api/cars/sessions/${sessionData.sessionId}/message`,
        data: { message: newUserMessage },
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setMessages(prev => [...prev, {
        role: 'user',
        text: newUserMessage,
        createdAt: new Date().toISOString(),
        messageType: 'TEXT'
      }]);

      const aiMessageObj = {
        role: 'ai',
        text: response.data.aiResponse,
        createdAt: new Date().toISOString(),
        messageType: 'TEXT',
        suggestedPages: response.data.suggestedPages || []
      };
      setMessages(prev => [...prev, aiMessageObj]);

    } catch (err) {
      console.error('Ошибка отправки сообщения:', err);
      alert('Ошибка при отправке сообщения: ' + err.message);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleRequestPage = async (pageNumber) => {
    if (!sessionData || sessionStatus !== 'ACTIVE') return;
    const token = checkAuth();
    if (!token) return;

    setIsLoading(true);
    try {
      const response = await apiRequest({
        method: 'post',
        url: `http://localhost:8080/api/cars/sessions/${sessionData.sessionId}/send-page`,
        data: { pageNumber: pageNumber },
        headers: { 'Authorization': `Bearer ${token}` }
      });

      setMessages(prev => [...prev, {
        role: 'ai',
        text: `Вот страница ${pageNumber} из технической документации:`,
        createdAt: new Date().toISOString(),
        imageUrl: response.data.imageUrl,
        pageNumber: pageNumber,
        messageType: 'PDF_PAGE'
      }]);
    } catch (err) {
      console.error('Ошибка запроса страницы:', err);
      alert('Ошибка при загрузке страницы: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompleteSession = async () => {
    if (!window.confirm('Завершить текущую сессию диагностики?')) return;
    const token = checkAuth();
    if (!token) return;
    try {
      await apiRequest({
        method: 'post',
        url: `http://localhost:8080/api/cars/sessions/${sessionData.sessionId}/complete`,
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setSessionStatus('COMPLETED');
      alert('Сессия завершена! Диагностическая карта сохранена.');
      navigate('/account');
    } catch (err) {
      alert('Ошибка при завершении сессии: ' + err.message);
    }
  };

  const handleDownload = async () => {
    const token = checkAuth();
    if (!token) return;
    try {
      const res = await apiRequest({
        method: 'get',
        url: `http://localhost:8080/api/cars/sessions/${sessionData.sessionId}/download`,
        headers: { 'Authorization': `Bearer ${token}` },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `diagnosis_${sessionData.sessionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Ошибка при скачивании: ' + err.message);
    }
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

  const formatMessageTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  if (!carInfo) {
    return (
      <>
        <Navbar />
        <div className="container" style={{marginTop: '100px', textAlign: 'center'}}>
          Загрузка данных сессии...
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="diagnosis-page">
        <div className="diagnosis-container">
          {}
          <div className="car-info-card">
            <div className="car-info-header">
              <h2>Ваш Автомобиль</h2>
              <div style={{display: 'inline-block', padding: '5px 12px', backgroundColor: sessionStatus === 'ACTIVE' ? '#4caf50' : '#9e9e9e', color: 'white', borderRadius: '15px', fontSize: '12px', fontWeight: 'bold', marginLeft: '10px'}}>
                {sessionStatus === 'ACTIVE' ? '🟢 АКТИВНА' : '🔵 ЗАВЕРШЕНА'}
              </div>
            </div>
            <div className="car-image-wrapper">
              <img src={carInfo.carImage} alt={carInfo.carBrand} className="car-image-rounded" onError={(e) => { e.target.src = '/images/car.png'; }} />
            </div>
            <div className="car-specs">
              <div className="spec-item"><span className="spec-label">Марка:</span><span className="spec-value">{carInfo.carBrand}</span></div>
              <div className="spec-item"><span className="spec-label">Модель:</span><span className="spec-value">{carInfo.carModel}</span></div>
              <div className="spec-item"><span className="spec-label">Двигатель:</span><span className="spec-value">{carInfo.carEngine}</span></div>
              <div className="spec-item"><span className="spec-label">Комплектация:</span><span className="spec-value">{carInfo.carEquipment}</span></div>
              <div className="spec-item"><span className="spec-label">Год выпуска:</span><span className="spec-value">{carInfo.carYear}</span></div>
              {carInfo.carGeneration && carInfo.carGeneration !== 'Не указано' && (
                <div className="spec-item"><span className="spec-label">Поколение:</span><span className="spec-value">{carInfo.carGeneration}</span></div>
              )}
            </div>
            <div className="car-description"><p><strong>Статус:</strong> {carInfo.manualStatus || 'Загрузка...'}</p></div>
            <div className="car-buttons">
              <button className="btn-download" onClick={handleDownload} disabled={sessionStatus !== 'ACTIVE'} style={{opacity: sessionStatus !== 'ACTIVE' ? 0.5 : 1, cursor: sessionStatus !== 'ACTIVE' ? 'not-allowed' : 'pointer'}}>Скачать диаг. карту</button>
              <button className="btn-finish" onClick={handleCompleteSession} disabled={sessionStatus !== 'ACTIVE'} style={{opacity: sessionStatus !== 'ACTIVE' ? 0.5 : 1, cursor: sessionStatus !== 'ACTIVE' ? 'not-allowed' : 'pointer', backgroundColor: '#f44336'}}>Завершить</button>
            </div>
            <div className="message-stats" style={{marginTop: '20px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '5px', fontSize: '12px', color: '#666'}}>
              <strong>Сообщений в сессии:</strong> {messages.length}
            </div>
          </div>

          {}
          <div className="chat-card">
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={msg.messageId || index} className={`message ${msg.role === 'ai' ? 'ai-message' : 'user-message'}`}>
                  <p><strong>{msg.role === 'ai' ? '🤖 AI DiaCar:' : '👤 Вы:'}</strong><span style={{fontSize: '11px', color: '#999', marginLeft: '10px'}}>{formatMessageTime(msg.createdAt)}</span></p>
                  <p style={{marginTop: '5px', whiteSpace: 'pre-wrap'}}>{msg.text}</p>
                  {msg.suggestedPages && msg.suggestedPages.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
                      <p><strong>📄 Страницы из мануала (по вашему запросу):</strong></p>
                      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                        {msg.suggestedPages.map((page, idx) => (
                          <button 
                            key={idx} 
                            onClick={() => handleRequestPage(page.page)} 
                            style={{ padding: '5px 10px', fontSize: '12px', cursor: 'pointer' }}
                          >
                            Стр. {page.page}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {msg.messageType === 'PDF_PAGE' && msg.imageUrl && (
                    <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#fff', borderRadius: '5px', border: '1px solid #ddd' }}>
                      <p style={{fontSize: '12px', color: '#666', marginBottom: '5px'}}>📄 Страница {msg.pageNumber} из технической документации</p>
                      <img src={msg.imageUrl} alt={`Страница ${msg.pageNumber}`} style={{ maxWidth: '100%', height: 'auto', border: '1px solid #ccc', borderRadius: '3px' }} onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }} />
                      <p style={{ display: 'none', fontSize: '12px', color: '#999', fontStyle: 'italic' }}>(Изображение временно недоступно)</p>
                    </div>
                  )}
                </div>
              ))}
              {isTyping && <div className="message ai-message"><p><strong>🤖 AI DiaCar:</strong> Печатает...</p></div>}
              <div ref={messagesEndRef} />
            </div>
            <form className="chat-input-form" onSubmit={handleSubmit}>
              <input 
                type="text" 
                className="chat-input" 
                placeholder={sessionStatus === 'ACTIVE' ? "Введите ваш запрос" : "Сессия завершена"} 
                value={userMessage} 
                onChange={(e) => setUserMessage(e.target.value)} 
                disabled={isLoading || sessionStatus !== 'ACTIVE'} 
                onKeyPress={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(e); } }} 
              />
              <button type="submit" className="btn-send" disabled={isLoading || sessionStatus !== 'ACTIVE'}>{isLoading ? '...' : '➤'}</button>
            </form>
          </div>
        </div>
        <footer className="diagnosis-footer"><div className="footer-content"><p>Сессия #{sessionData?.sessionId} • Сообщений: {messages.length}</p></div></footer>
      </div>
    </>
  );
}

export default DiagnosisPage;
