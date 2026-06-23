import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Navbar.css';

function Navbar() {
  return (
    <nav className="navbar white-navbar">
      <div className="navbar-container">
        <div className="navbar-header">
          <button 
            type="button" 
            className="navbar-toggle"
            onClick={() => {
              const menu = document.querySelector('.navbar-menu');
              menu.classList.toggle('navbar-menu-active');
            }}
          >
            <span className="icon-bar"></span>
            <span className="icon-bar"></span>
            <span className="icon-bar"></span>
          </button>
          <Link className="navbar-brand" to="/">
            <span className="gear-icon">⚙️</span> AI DiaCar
          </Link>
        </div>
        
        <div className="navbar-menu">
          <ul className="navbar-nav navbar-left">
            <li><Link to="/news">Новости</Link></li>
            <li><Link to="/advice">Советы</Link></li>
            <li><Link to="/feedback">Обратная связь</Link></li>
          </ul>
          
          <ul className="navbar-nav navbar-right">
            <li><Link to="/account">Личный кабинет</Link></li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
