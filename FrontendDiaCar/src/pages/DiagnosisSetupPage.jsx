import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/DiagnosisSetupPage.css';

function DiagnosisSetupPage() {
  const navigate = useNavigate();
  
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);
  const [years, setYears] = useState([]);
  
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  
  const [carDetails, setCarDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [manualInfo, setManualInfo] = useState({ available: false, type: 'NONE', checked: false });
  
  const isSubmittingRef = useRef(false);

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
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
        navigate('/login', { replace: true });
        throw new Error('Token expired');
      }
      throw err;
    }
  };

  useEffect(() => {
    const fetchBrands = async () => {
      const token = checkAuth();
      if (!token) return;
      try {
        const res = await apiRequest({
          method: 'get',
          url: 'http://localhost:8080/api/cars/brands',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setBrands(res.data.sort());
      } catch (err) {
        if (err.message !== 'Token expired') console.error(err);
      }
    };
    fetchBrands();
  }, [navigate]);

  useEffect(() => {
    if (!selectedBrand) return;
    const fetchModels = async () => {
      const token = checkAuth();
      if (!token) return;
      try {
        const res = await apiRequest({
          method: 'get',
          url: `http://localhost:8080/api/cars/models?brand=${selectedBrand}`,
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setModels(res.data.sort());
        setSelectedModel('');
        setYears([]);
        setSelectedYear('');
        setCarDetails(null);
        setManualInfo({ available: false, type: 'NONE', checked: false });
      } catch (err) {
        if (err.message !== 'Token expired') console.error(err);
      }
    };
    fetchModels();
  }, [selectedBrand]);

  useEffect(() => {
    if (!selectedBrand || !selectedModel) return;
    const fetchYears = async () => {
      const token = checkAuth();
      if (!token) return;
      try {
        const res = await apiRequest({
          method: 'get',
          url: `http://localhost:8080/api/cars/years?brand=${selectedBrand}&model=${selectedModel}`,
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setYears(res.data.sort((a,b) => a - b));
        setSelectedYear('');
        setCarDetails(null);
      } catch (err) {
        if (err.message !== 'Token expired') console.error(err);
      }
    };
    fetchYears();
  }, [selectedBrand, selectedModel]);

  useEffect(() => {
    if (!selectedBrand || !selectedModel || !selectedYear) return;
    const fetchCarDetails = async () => {
      const token = checkAuth();
      if (!token) return;
      try {
        const res = await apiRequest({
          method: 'get',
          url: `http://localhost:8080/api/cars/car-details?brand=${selectedBrand}&model=${selectedModel}&year=${selectedYear}`,
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setCarDetails(res.data);
        const manualRes = await apiRequest({
          method: 'get',
          url: 'http://localhost:8080/api/manuals/search',
          params: { brand: selectedBrand, model: selectedModel },
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setManualInfo({
          available: manualRes.data.found,
          type: manualRes.data.manualType || 'NONE',
          checked: true
        });
      } catch (err) {
        if (err.message !== 'Token expired') console.error(err);
        setCarDetails(null);
      }
    };
    fetchCarDetails();
  }, [selectedBrand, selectedModel, selectedYear]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmittingRef.current) return;
    if (!selectedBrand || !selectedModel || !selectedYear || !carDetails) {
      alert('Выберите марку, модель и год');
      return;
    }
    isSubmittingRef.current = true;
    setLoading(true);
    setError(null);

    try {
      const token = checkAuth();
      if (!token) return;

      const sessionRes = await apiRequest({
        method: 'post',
        url: 'http://localhost:8080/api/cars/start-session',
        data: { carId: carDetails.carId },
        headers: { 'Authorization': `Bearer ${token}` }
      });

      navigate('/diagnosis', { state: { sessionData: sessionRes.data } });

    } catch (err) {
      if (err.message !== 'Token expired') {
        console.error('Ошибка:', err);
        setError('Ошибка при создании сессии: ' + (err.response?.data || err.message));
      }
    } finally {
      setLoading(false);
      isSubmittingRef.current = false;
    }
  };

  const getManualStatusText = () => {
    if (!manualInfo.checked) return '';
    if (!manualInfo.available) return '⚠️ Мануал не найден. Будет использована общая диагностика.';
    switch (manualInfo.type) {
      case 'SPECIFIC': return '✅ Найден мануал для конкретной модели.';
      case 'BRAND_COMMON': return '✅ Найден общий мануал бренда.';
      case 'GENERAL': return '✅ Найден общий мануал для всех автомобилей.';
      default: return '';
    }
  };

  return (
    <>
      <Navbar />
      <div className="setup-container">
        <h2>Настройка диагностики</h2>
        <p className="subtitle">Выберите автомобиль из справочника</p>
        
        {error && <div className="error-msg">{error}</div>}

        {manualInfo.checked && (
          <div className={`manual-status ${manualInfo.available ? 'success' : 'warning'}`}>
            {getManualStatusText()}
          </div>
        )}

        <form onSubmit={handleSubmit} className="smart-form">
          <div className="form-group">
            <label>Марка автомобиля</label>
            <select 
              value={selectedBrand} 
              onChange={(e) => setSelectedBrand(e.target.value)}
              className="form-control"
              required
            >
              <option value="">-- Выберите марку --</option>
              {brands.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Модель</label>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              className="form-control"
              disabled={!selectedBrand}
              required
            >
              <option value="">-- Сначала выберите марку --</option>
              {models.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          {selectedModel && years.length > 0 && (
            <div className="form-group">
              <label>Год выпуска</label>
              <select 
                value={selectedYear} 
                onChange={(e) => setSelectedYear(e.target.value)}
                className="form-control"
                required
              >
                <option value="">-- Выберите год --</option>
                {years.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-lg" disabled={loading || !carDetails}>
            {loading ? 'Создание сессии...' : 'Начать диагностику'}
          </button>
        </form>
      </div>
    </>
  );
}

export default DiagnosisSetupPage;
