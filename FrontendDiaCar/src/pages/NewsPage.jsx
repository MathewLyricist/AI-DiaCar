import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/NewsPage.css';

function NewsPage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userRole, setUserRole] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    imageUrl: '',
    videoUrl: '',
    date: new Date().toISOString().split('T')[0],
  });
  const [submitting, setSubmitting] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);

  const [expandedNews, setExpandedNews] = useState({});

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
    fetchNews();
    fetchUserRole();
  }, []);

  const fetchNews = async () => {
    try {
      const res = await axios.get('http://localhost:8080/api/news');
      setNews(res.data);
    } catch (err) {
      setError('Не удалось загрузить новости');
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
    } catch (err) {
      console.error('Failed to fetch role');
    }
  };

  const openCreateModal = () => {
    setEditId(null);
    setFormData({
      title: '',
      content: '',
      imageUrl: '',
      videoUrl: '',
      date: new Date().toISOString().split('T')[0],
    });
    setImageFile(null);
    setShowModal(true);
  };

  const openEditModal = (item) => {
    setEditId(item.id);
    setFormData({
      title: item.title,
      content: item.content,
      imageUrl: item.imageUrl || '',
      videoUrl: item.videoUrl || '',
      date: item.date || new Date().toISOString().split('T')[0],
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
          url: `http://localhost:8080/api/news/${editId}`,
          data: payload,
        });
      } else {
        await apiRequest({
          method: 'post',
          url: 'http://localhost:8080/api/news',
          data: payload,
        });
      }
      setShowModal(false);
      fetchNews();
      setImageFile(null);
    } catch (err) {
      alert('Ошибка при сохранении: ' + (err.response?.data || err.message));
    } finally {
      setSubmitting(false);
      setUploadingImage(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить новость?')) return;
    try {
      await apiRequest({ method: 'delete', url: `http://localhost:8080/api/news/${id}` });
      fetchNews();
    } catch (err) {
      alert('Ошибка удаления');
    }
  };

  const toggleExpand = (id) => {
    setExpandedNews(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const renderVideo = (url) => {
    if (!url) return null;
    if (url.includes('youtube.com/watch')) {
      const videoId = url.split('v=')[1]?.split('&')[0];
      return (
        <iframe
          width="100%"
          height="200"
          src={`https://www.youtube.com/embed/${videoId}`}
          title="YouTube video"
          frameBorder="0"
          allowFullScreen
        ></iframe>
      );
    }
    return <video src={url} controls style={{ width: '100%', maxHeight: '200px' }} />;
  };

  if (loading) return <><Navbar /><div className="page-container">Загрузка...</div></>;

  return (
    <>
      <Navbar />
      <div className="page-container">
        <div className="content-card">
          <div className="section-header">
            <h2>Новости индустрии</h2>
            {userRole === 'ROLE_ADMIN' && (
              <button className="btn-add" onClick={openCreateModal}>+ Добавить новость</button>
            )}
          </div>
          {error && <div className="error-message">{error}</div>}
          <div className="news-grid">
            {news.map((item) => {
              const isExpanded = expandedNews[item.id];
              const previewLength = 300; 

              return (
                <div key={item.id} className="news-card">
                  {item.imageUrl && <img src={`http://localhost:8080${item.imageUrl}`} alt={item.title} className="news-image" />}
                  <div className="news-content">
                    <h3>{item.title}</h3>
                    <div className="news-meta">
                      {new Date(item.date).toLocaleDateString('ru-RU', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                      })}
                    </div>
                    <div className="news-text">
                      {isExpanded
                        ? item.content
                        : item.content.length > previewLength
                          ? item.content.substring(0, previewLength) + '...'
                          : item.content
                      }
                    </div>
                    {item.content.length > previewLength && (
                      <button className="read-more-btn" onClick={() => toggleExpand(item.id)}>
                        {isExpanded ? 'Свернуть' : 'Читать далее'}
                      </button>
                    )}
                    {item.videoUrl && <div className="news-video">{renderVideo(item.videoUrl)}</div>}
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
            <h3>{editId ? 'Редактировать новость' : 'Новая новость'}</h3>
            <input type="text" placeholder="Заголовок" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} />
            <textarea placeholder="Содержание" rows="5" value={formData.content} onChange={(e) => setFormData({ ...formData, content: e.target.value })} />
            <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
            {formData.imageUrl && !imageFile && (
              <div style={{ marginBottom: '15px', fontSize: '12px', color: '#666' }}>
                Текущее изображение: {formData.imageUrl.split('/').pop()}
              </div>
            )}
            <input type="text" placeholder="URL видео (YouTube)" value={formData.videoUrl} onChange={(e) => setFormData({ ...formData, videoUrl: e.target.value })} />
            <input type="date" value={formData.date} onChange={(e) => setFormData({ ...formData, date: e.target.value })} />
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

export default NewsPage;
