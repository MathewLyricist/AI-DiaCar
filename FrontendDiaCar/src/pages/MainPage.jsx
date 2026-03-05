import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import '../styles/MainPage.css';

function MainPage() {
  return (
    <>
      <Navbar />
      
      {/* Герой-секция */}
      <section className="hero-section">
        <div className="hero-content">
          <h1>Твой автомобиль приболел?</h1>
          <h2>Я выпишу тебе лекарство!</h2>
          <Link to="/diagnosis" className="btn-hero">
            НАЧАТЬ ДИАГНОСТИКУ
          </Link>
        </div>
      </section>

      {/* Футер */}
      <footer className="main-footer">
        <div className="footer-container">
          <div className="footer-col">
            <h3>AI DiaCar</h3>
            <p>Разработано на технологиях OpenAI.</p>
          </div>
          
          <div className="footer-col">
            <h4>Партнеры</h4>
            <ul>
              <li><a href="#">Drive2</a></li>
              <li><a href="#">Drom.ru</a></li>
              <li><a href="#">Гараж 54</a></li>
            </ul>
          </div>
          
          <div className="footer-col">
            <h4>Поддержка</h4>
            <ul>
              <li><Link to="/feedback">Обратная связь</Link></li>
              <li><Link to="/partners">Сотрудничество</Link></li>
            </ul>
          </div>
        </div>
      </footer>
    </>
  );
}

export default MainPage;
