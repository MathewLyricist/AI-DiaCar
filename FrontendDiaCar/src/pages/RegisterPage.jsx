import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/RegisterPage.css';

function Register() {
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [enterprise, setEnterprise] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    if (password.length < 6) {
      setError('Пароль должен быть не менее 6 символов');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8080/api/auth/register', {
        name,
        enterprise,
        email,
        password
      });

      const { token } = response.data;
      localStorage.setItem('authToken', token);
      
      navigate('/account');
    } catch (err) {
      console.error('Ошибка регистрации:', err);
      if (err.response && err.response.data) {
        setError(err.response.data);
      } else {
        setError('Ошибка подключения к серверу. Проверьте, запущен ли Backend.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <header className="image-header">
        <div className="container">
          <h1>Регистрация</h1>
        </div>
      </header>

      <div className="container">
        <div className="row">
          <div className="col-md-6 col-md-offset-3">
            <form onSubmit={handleSubmit} className="auth-form">
              {error && <div style={{color: 'red', marginBottom: '15px', textAlign: 'center'}}>{error}</div>}
              
              <div className="form-group">
                <label>Имя</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="Введите имя" 
                  required 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            
              <div className="form-group">
                <label>Предприятие (при наличии)</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="Название предприятия" 
                  value={enterprise}
                  onChange={(e) => setEnterprise(e.target.value)}
                />
              </div>
            
              <div className="form-group">
                <label>Электронная почта</label>
                <input 
                  type="email" 
                  className="form-control" 
                  placeholder="Введите email" 
                  required 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            
              <div className="form-group">
                <label>Номер телефона</label>
                <input 
                  type="tel" 
                  className="form-control" 
                  placeholder="+7 (___) ___-__-__" 
                  required 
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
            
              <div className="form-group">
                <label>Пароль</label>
                <input 
                  type="password" 
                  className="form-control" 
                  placeholder="Придумайте пароль" 
                  required 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            
              <div className="form-group">
                <label>Подтверждение пароля</label>
                <input 
                  type="password" 
                  className="form-control" 
                  placeholder="Повторите пароль" 
                  required 
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            
              {}
              <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? 'Регистрация...' : 'Зарегистрироваться'}
              </button>
            </form>
          
            <div className="text-center auth-links">
              <Link to="/login">Уже есть аккаунт? Войдите</Link>
            </div>
          </div>
        </div>
      
        <div className="bottom-text text-center">
          <p>Сделаем мир лучше вместе.</p>
        </div>
      </div>
    </>
  );
}

export default Register;
