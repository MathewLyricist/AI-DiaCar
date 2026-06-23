import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import '../styles/LoginPage.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('http://localhost:8080/api/auth/login', {
        email,
        password
      });

      const { token } = response.data;
      
      if (rememberMe) {
        localStorage.setItem('authToken', token);
        console.log('Токен сохранен в localStorage (постоянно)');
      } else {
        sessionStorage.setItem('authToken', token);
        console.log('Токен сохранен в sessionStorage (до закрытия вкладки)');
      }
      
      console.log('Вход успешен');
      navigate('/account');
      
    } catch (err) {
      console.error('Ошибка входа:', err);
      if (err.response && err.response.status === 401) {
        setError('Неверный email или пароль');
      } else {
        setError('Ошибка соединения с сервером');
      }
    }
  };

  return (
    <>
      <Navbar />
      <header className="image-header">
        <div className="container">
          <h1>Вход в систему</h1>
        </div>
      </header>

      <div className="container">
        <div className="row">
          <div className="col-md-6 col-md-offset-3">
            <form onSubmit={handleSubmit} className="auth-form">
              {error && <div style={{color: 'red', marginBottom: '10px'}}>{error}</div>}
              
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
                <label>Пароль</label>
                <input 
                  type="password" 
                  className="form-control" 
                  placeholder="Введите пароль" 
                  required 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              
              <div className="form-group checkbox">
                <label>
                  <input 
                    type="checkbox" 
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />{' '}
                  Запомнить меня
                </label>
              </div>
              
              <button type="submit" className="btn btn-primary btn-block">
                Войти
              </button>
            </form>
            
            <div className="text-center auth-links">
              <Link to="/register">Нет аккаунта? Зарегистрируйтесь</Link>
              <br />
              <a href="#">Забыли пароль?</a>
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

export default Login;
