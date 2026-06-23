import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/AdvicePage.css';

function AdvicePage() {
  const [advice, setAdvice] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'Engine',
    difficulty: 'Medium',
    imageUrl: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [expandedAdvice, setExpandedAdvice] = useState({});

  const apiRequest = async (config) => {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    if (!config.headers) config.headers = {};
    if (token) config.headers.Authorization = `Bearer ${token}`;
    try {
      return await axios(config);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        window.location.href = '/login';
      }
      throw err;
    }
  };

  const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const response = await axios.post('http://localhost:8080/api/uploads/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data.url;
  };

  useEffect(() => {
    fetchAdvice();
    fetchUserRole();
  }, []);

  const fetchAdvice = async () => {
    try {
      const res = await axios.get('http://localhost:8080/api/advice');
      setAdvice(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserRole = async () => {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    if (!token) return;
    try {
      const res = await apiRequest({ method: 'get', url: 'http://localhost:8080/api/account/me' });
      setUserRole(res.data.role);
    } catch (err) {}
  };

  const openCreateModal = () => {
    setEditId(null);
    setFormData({
      title: '',
      content: '',
      category: 'Engine',
      difficulty: 'Medium',
      imageUrl: '',
    });
    setImageFile(null);
    setShowModal(true);
  };

  const openEditModal = (item) => {
    setEditId(item.id);
    setFormData({
      title: item.title,
      content: item.content,
      category: item.category || 'Engine',
      difficulty: item.difficulty || 'Medium',
      imageUrl: item.imageUrl || '',
    });
    setImageFile(null);
    setShowModal(true);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      let imageUrl = formData.imageUrl;
      if (imageFile) {
        setUploadingImage(true);
        imageUrl = await uploadImage(imageFile);
        setUploadingImage(false);
      }
      const payload = { ...formData, imageUrl };
      if (editId) {
        await apiRequest({
          method: 'put',
          url: `http://localhost:8080/api/advice/${editId}`,
          data: payload,
        });
      } else {
        await apiRequest({
          method: 'post',
          url: 'http://localhost:8080/api/advice',
          data: payload,
        });
      }
      setShowModal(false);
      fetchAdvice();
      setImageFile(null);
    } catch (err) {
      alert('Ошибка: ' + (err.response?.data || err.message));
    } finally {
      setSubmitting(false);
      setUploadingImage(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить совет?')) return;
    try {
      await apiRequest({ method: 'delete', url: `http://localhost:8080/api/advice/${id}` });
      fetchAdvice();
    } catch (err) {
      alert('Ошибка удаления');
    }
  };

  const toggleExpand = (id) => {
    setExpandedAdvice(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const getDifficultyColor = (diff) => {
    if (diff === 'Easy') return '#28a745';
    if (diff === 'Medium') return '#ffc107';
    return '#dc3545';
  };

  if (loading) return <><Navbar /><div className="page-container">Загрузка...</div></>;

  return (
    <>
      <Navbar />
      <div className="page-container">
        <div className="content-card">
          <div className="section-header">
            <h2>Полезные советы</h2>
            {userRole === 'ROLE_ADMIN' && (
              <button className="btn-add" onClick={openCreateModal}>+ Добавить совет</button>
            )}
          </div>
          <div className="advice-grid">
            {advice.map((item) => {
              const isExpanded = expandedAdvice[item.id];
              const previewLength = 200;

              return (
                <div key={item.id} className="advice-card">
                  {item.imageUrl && <img src={`http://localhost:8080${item.imageUrl}`} alt={item.title} className="advice-image" />}
                  <div className="advice-content">
                    <div className="advice-badges">
                      <span className="badge category">{item.category}</span>
                      <span className="badge difficulty" style={{ backgroundColor: getDifficultyColor(item.difficulty) }}>
                        {item.difficulty}
                      </span>
                    </div>
                    <h3>{item.title}</h3>
                    <div className="advice-text">
                      {isExpanded
                        ? item.content
                        : item.content.length > previewLength
                          ? item.content.substring(0, previewLength) + '...'
                          : item.content}
                    </div>
                    {item.content.length > previewLength && (
                      <button className="read-more-btn" onClick={() => toggleExpand(item.id)}>
                        {isExpanded ? 'Свернуть' : 'Читать далее'}
                      </button>
                    )}
                  </div>
                  {userRole === 'ROLE_ADMIN' && (
                    <div className="admin-actions">
                      <button onClick={() => openEditModal(item)} className="btn-edit">✏️</button>
                      <button onClick={() => handleDelete(item.id)} className="btn-delete">🗑️</button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{editId ? 'Редактировать совет' : 'Новый совет'}</h3>
            <input type="text" placeholder="Заголовок" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} />
            <textarea placeholder="Содержание" rows="5" value={formData.content} onChange={(e) => setFormData({ ...formData, content: e.target.value })} />
            <select value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })}>
              <option>Engine</option>
              <option>Transmission</option>
              <option>Electronics</option>
              <option>Brakes</option>
              <option>Maintenance</option>
            </select>
            <select value={formData.difficulty} onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}>
              <option>Easy</option>
              <option>Medium</option>
              <option>Hard</option>
            </select>
            <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
            {formData.imageUrl && !imageFile && (
              <div style={{ marginBottom: '15px', fontSize: '12px', color: '#666' }}>
                Текущее изображение: {formData.imageUrl.split('/').pop()}
              </div>
            )}
            <div className="modal-buttons">
              <button onClick={handleSubmit} disabled={submitting || uploadingImage}>
                {submitting || uploadingImage ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button onClick={() => setShowModal(false)}>Отмена</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AdvicePage;
