import React from 'react';
import Navbar from '../components/Navbar';
import '../styles/AccountPage.css';

function AccountPage() {
  return (
    <>
      <Navbar />
      
      <div className="account-page">
        <div className="account-container">
          {/* Основная карточка */}
          <div className="account-card">
            <div className="account-header">
              <div className="account-info">
                <dl className="account-dl">
                  <div className="dl-row">
                    <dt>Аккаунт:</dt>
                    <dd>Вася механик</dd>
                  </div>
                  
                  <div className="dl-row">
                    <dt>Предприятие:</dt>
                    <dd>нет</dd>
                  </div>
                  
                  <div className="dl-row">
                    <dt>Эл. почта:</dt>
                    <dd>agbdkq@gmail.ru</dd>
                  </div>
                  
                  <div className="dl-row">
                    <dt>Дата регистрации:</dt>
                    <dd>01.01.24</dd>
                  </div>
                  
                  <div className="dl-row">
                    <dt>Количество а/м:</dt>
                    <dd>2</dd>
                  </div>
                  
                  <div className="dl-row">
                    <dt>Номер телефона:</dt>
                    <dd>+39347242557</dd>
                  </div>
                </dl>
              </div>
              
              <div className="account-avatar-wrapper">
                <img 
                  src="/images/account.jpeg" 
                  alt="Avatar" 
                  className="account-avatar"
                />
              </div>
            </div>
            
            <div className="account-buttons">
              <button className="btn-edit">Изменить</button>
              <button className="btn-save">Сохранить</button>
            </div>
          </div>

          {/* Список автомобилей */}
          <div className="account-card car-list">
            <h3 className="card-title">Список автомобилей:</h3>
            
            <div className="car-item">
              <span className="car-name">Toyota Land Cruiser 200 3.5V</span>
              <div className="car-buttons">
                <button className="btn-small btn-small-edit">Изменить</button>
                <button className="btn-small btn-small-delete">Удалить</button>
              </div>
            </div>
            
            <div className="car-item">
              <span className="car-name">Lada Priora 1.5i P.O.O.P.</span>
              <div className="car-buttons">
                <button className="btn-small btn-small-edit">Изменить</button>
                <button className="btn-small btn-small-delete">Удалить</button>
              </div>
            </div>
            
            <div className="car-item">
              <span className="car-name">Daewoo Nexia 1.5i GL</span>
              <div className="car-buttons">
                <button className="btn-small btn-small-edit">Изменить</button>
                <button className="btn-small btn-small-delete">Удалить</button>
              </div>
            </div>
          </div>

          {/* Диагностические карты - ССЫЛКИ */}
          <div className="diagnostics-section">
            <div className="diagnostics-title">Список диагностических карт</div>
            
            <a href="#" className="diag-item diag-link">
              <span className="diag-date">Дата обращения: 21.01.25</span>
              <span className="diag-car">Toyota Land Cruiser 200 3.5V</span>
              <span className="diag-arrow">→</span>
            </a>
            
            <a href="#" className="diag-item diag-link">
              <span className="diag-date">Дата обращения: 25.01.25</span>
              <span className="diag-car">Lada Priora 1.5i</span>
              <span className="diag-arrow">→</span>
            </a>
            
            <a href="#" className="diag-item diag-link">
              <span className="diag-date">Дата обращения: 23.01.25</span>
              <span className="diag-car">Daewoo Nexia 1.5i</span>
              <span className="diag-arrow">→</span>
            </a>
          </div>
          
          <div className="footer-text">
            Стань одним из тех, кто изменит мир.
          </div>
        </div>
      </div>
    </>
  );
}

export default AccountPage;
