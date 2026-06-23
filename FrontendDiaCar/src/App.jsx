import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './pages/MainPage';
import DiagnosisPage from './pages/DiagnosisPage';
import DiagnosisSetupPage from './pages/DiagnosisSetupPage';
import AccountPage from './pages/AccountPage';
import Register from './pages/RegisterPage';
import Login from './pages/LoginPage';
import News from './pages/NewsPage';
import Advice from './pages/AdvicePage';
import Feedback from './pages/FeedbackPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        {}
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/advice" element={<Advice />} />
        <Route path="/news" element={<News />} />
        <Route path="/register" element={<Register />} />
        
        {}
        <Route 
          path="/diagnosis-setup" 
          element={
            <ProtectedRoute>
              <DiagnosisSetupPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/diagnosis" 
          element={
            <ProtectedRoute>
              <DiagnosisPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/account" 
          element={
            <ProtectedRoute>
              <AccountPage />
            </ProtectedRoute>
          } 
        />
       <Route 
          path="/feedback" 
          element={
            <ProtectedRoute>
              <Feedback />
            </ProtectedRoute>
          } 
        /> 
      </Routes>
    </Router>
  );
}

export default App;
