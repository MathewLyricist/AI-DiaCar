import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import '../styles/LoginPage.css';

function Login() {
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Вход в систему...');
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
              <div className="form-group">
                <label>Электронная почта</label>
                <input type="email" className="form-control" placeholder="Введите email" required />
              </div>
              
              <div className="form-group">
                <label>Пароль</label>
                <input type="password" className="form-control" placeholder="Введите пароль" required />
              </div>
              
              <div className="form-group checkbox">
                <label>
                  <input type="checkbox" /> Запомнить меня
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
