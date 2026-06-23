import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import '../styles/ErrorPage.css';

function ErrorPage({ error, status = 500, title = "Упс, что-то пошло не так!" }) {
  const navigate = useNavigate();

  const getErrorMessage = (code) => {
    switch (code) {
      case 404:
        return "Страница, которую вы ищете, не найдена. Возможно, она была удалена или перемещена.";
      case 403:
        return "Доступ запрещен. У вас недостаточно прав для просмотра этой страницы.";
      case 401:
        return "Вы не авторизованы. Пожалуйста, войдите в систему.";
      case 500:
        return "Внутренняя ошибка сервера. Наши инженеры уже уведомлены о проблеме.";
      case 'NETWORK':
        return "Нет соединения с сервером. Проверьте ваше интернет-соединение или попробуйте позже.";
      default:
        return error?.message || "Произошла непредвиденная ошибка.";
    }
  };

  return (
    <>
      <Navbar />
      <div className="error-page-container">
        <div className="error-content">
          <div className="error-code">{status === 'NETWORK' ? '📡' : status}</div>
          
          <h1 className="error-title">{title}</h1>
          
          <p className="error-description">
            {getErrorMessage(status)}
          </p>

          {error && status !== 'NETWORK' && (
            <details className="error-details">
              <summary>Технические детали (для разработчика)</summary>
              <pre>{JSON.stringify(error, null, 2)}</pre>
            </details>
          )}

          <div className="error-actions">
            <button onClick={() => window.location.reload()} className="btn-error-reload">
              🔄 Обновить страницу
            </button>
            <Link to="/" className="btn-error-home">
              🏠 На главную
            </Link>
            {status === 401 && (
              <button onClick={() => navigate('/login')} className="btn-error-login">
                Войти в систему
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default ErrorPage;
