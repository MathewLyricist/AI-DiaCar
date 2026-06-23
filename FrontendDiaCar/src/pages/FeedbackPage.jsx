import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/FeedbackPage.css';

function FeedbackPage() {
  const navigate = useNavigate();
  const [userEmail, setUserEmail] = useState('');
  const [limitInfo, setLimitInfo] = useState({ count: 0, limit: 2, canSubmit: true });
  const [formData, setFormData] = useState({
    type: 'Баг',
    subject: '',
    message: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  const apiRequest = async (config) => {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    if (!token) {
      navigate('/login');
      throw new Error('No token');
    }
    if (!config.headers) config.headers = {};
    config.headers.Authorization = `Bearer ${token}`;
    try {
      return await axios(config);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        navigate('/login');
      }
      throw err;
    }
  };

  const fetchUserAndLimit = async () => {
    try {
      const userRes = await apiRequest({ method: 'get', url: 'http://localhost:8080/api/account/me' });
      setUserEmail(userRes.data.email);
      const limitRes = await apiRequest({ method: 'get', url: 'http://localhost:8080/api/feedback/daily-limit' });
      setLimitInfo(limitRes.data);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setMessage({ text: 'Ошибка сервера: не удалось загрузить данные пользователя. Обратитесь в поддержку.', type: 'error' });
      }
    }
  };

  useEffect(() => {
    fetchUserAndLimit();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!limitInfo.canSubmit) {
      setMessage({ text: 'Лимит исчерпан: можно отправить не более 2 обращений в день.', type: 'error' });
      return;
    }
    setSubmitting(true);
    try {
      await apiRequest({
        method: 'post',
        url: 'http://localhost:8080/api/feedback',
        data: {
          ...formData,
          email: userEmail,
        },
      });
      setMessage({ text: '✅ Ваше обращение отправлено! Спасибо.', type: 'success' });
      setFormData({ type: 'Баг', subject: '', message: '' });
      const limitRes = await apiRequest({ method: 'get', url: 'http://localhost:8080/api/feedback/daily-limit' });
      setLimitInfo(limitRes.data);
    } catch (err) {
      const errorMsg = err.response?.data || 'Ошибка отправки';
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="page-container">
        <div className="content-card feedback-card">
          <h2>Обратная связь</h2>
          <p className="limit-info">
            Осталось обращений сегодня: {limitInfo.limit - limitInfo.count} из {limitInfo.limit}
          </p>
          {message.text && (
            <div className={`feedback-message ${message.type}`}>{message.text}</div>
          )}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Тип обращения *</label>
              <select name="type" value={formData.type} onChange={handleChange} required>
                <option>Баг</option>
                <option>Жалоба</option>
                <option>Совет по улучшению</option>
                <option>Прочее</option>
              </select>
            </div>
            <div className="form-group">
              <label>Тема *</label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                required
                placeholder="Кратко опишите суть"
              />
            </div>
            <div className="form-group">
              <label>Сообщение *</label>
              <textarea
                name="message"
                rows="6"
                value={formData.message}
                onChange={handleChange}
                required
                placeholder="Подробно опишите проблему или предложение..."
              />
            </div>
            <button type="submit" className="btn-submit" disabled={submitting || !limitInfo.canSubmit}>
              {submitting ? 'Отправка...' : 'Отправить'}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}

export default FeedbackPage;
