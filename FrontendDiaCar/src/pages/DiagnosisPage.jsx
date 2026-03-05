import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import '../styles/DiagnosisPage.css';

function DiagnosisPage() {
  const [userMessage, setUserMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Отправка запроса:', userMessage);
    setUserMessage('');
  };

  const handleDownload = () => {
    console.log('Скачивание диагностической карты...');
  };

  const handleFinish = () => {
    console.log('Завершение сессии...');
  };

  return (
    <>
      <Navbar />
      
      {/* Фон на всю страницу */}
      <div className="diagnosis-page">
        <div className="diagnosis-container">
          
          {/* Левая колонка - Информация об автомобиле */}
          <div className="car-info-card">
            <div className="car-info-header">
              <h2>Ваш Автомобиль</h2>
            </div>
            
            {/* Круглая рамка с изображением автомобиля */}
            <div className="car-image-wrapper">
              <img 
                src="/images/mark2.png" 
                alt="Toyota Mark 2" 
                className="car-image-rounded"
              />
            </div>

            <div className="car-specs">
              <div className="spec-item">
                <span className="spec-label">Марка:</span>
                <span className="spec-value">Toyota</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Модель:</span>
                <span className="spec-value">Mark 2</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Двигатель:</span>
                <span className="spec-value">1JZ-GTE</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Комплектация:</span>
                <span className="spec-value">Grande</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Год выпуска:</span>
                <span className="spec-value">1995</span>
              </div>
            </div>

            <div className="car-description">
              <p><strong>Особенности:</strong> Седьмое поколение Toyota Mark II в кузовах 90-й серии выпускалось с октября 1992 по август 1996 гг.[12] Применялось несколько двигателей, устанавливающихся на задне- и полноприводные.</p>
              <p><strong>Слабые места:</strong> ходовая часть, шаровые опоры, автоматическая коробка передач.</p>
            </div>

            <div className="car-buttons">
              <button className="btn-download" onClick={handleDownload}>
                Скачать диаг. карту
              </button>
              <button className="btn-finish" onClick={handleFinish}>
                Завершить
              </button>
            </div>
          </div>

          {/* Правая колонка - Чат с AI */}
          <div className="chat-card">
            <div className="chat-messages">
              <div className="message user-message">
                <p><strong>Пользователь:</strong> машина постояла ночь, одну, а утром на работу ехать, я её завожу, кутыр кутыр кутыр кутыр кутыр и не хочет ехать. Я снял аккумулятор и погрел его дома у огня. Приношу снова акум, пытаюсь завести, а машины кутыкырткутыкырту и не хочет завестись.</p>
              </div>
              
              <div className="message ai-message">
                <p><strong>AI DiaCar:</strong> Провожу анализ, пожалуйста, подождите...</p>
              </div>
              
              <div className="message ai-message">
                <p><strong>AI DiaCar:</strong> Спасибо за ожидание. После проведения анализа AI выделил несколько причин данной неисправности:</p>
                <ul>
                  <li>проблема со свечами зажигания;</li>
                  <li>проблема с подачей топлива;</li>
                  <li>проблема с владельцем автомобиля;</li>
                  <li>неисправный стартер.</li>
                </ul>
                <p>Если я сумел определить точную неисправность по вашему описанию, то вы можете скачать диагностическую карту, при завершении сессии данные автоматически удалятся, кроме основной проблемы и вероятных симптомов выбранного вами автомобиля.</p>
              </div>
            </div>

            <form className="chat-input-form" onSubmit={handleSubmit}>
              <input 
                type="text" 
                className="chat-input" 
                placeholder="Введите ваш запрос"
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
              />
              <button type="submit" className="btn-send">➤</button>
            </form>
          </div>

        </div>

        {/* Футер */}
        <footer className="diagnosis-footer">
          <div className="footer-content">
            <p>Давай начнем</p>
            <div className="social-icons">
              <a href="#" className="social-icon">📷</a>
              <a href="#" className="social-icon">💼</a>
              <a href="#" className="social-icon">𝕏</a>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

export default DiagnosisPage;
