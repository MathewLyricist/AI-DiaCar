import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import '../styles/RegisterPage.css';

function Register() {
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Регистрация...');
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
              <div className="form-group">
                <label>Имя</label>
                <input type="text" className="form-control" placeholder="Введите имя" required />
              </div>
              
              <div className="form-group">
                <label>Предприятие (при наличии)</label>
                <input type="text" className="form-control" placeholder="Название предприятия" />
              </div>
              
              <div className="form-group">
                <label>Электронная почта</label>
                <input type="email" className="form-control" placeholder="Введите email" required />
              </div>
              
              <div className="form-group">
                <label>Номер телефона</label>
                <input type="tel" className="form-control" placeholder="+7 (___) ___-__-__" required />
              </div>
              
              <div className="form-group">
                <label>Пароль</label>
                <input type="password" className="form-control" placeholder="Придумайте пароль" required />
              </div>
              
              <div className="form-group">
                <label>Подтверждение пароля</label>
                <input type="password" className="form-control" placeholder="Повторите пароль" required />
              </div>
              
              <button type="submit" className="btn btn-primary btn-block">
                Зарегистрироваться
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
