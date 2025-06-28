// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import ApkUpload from './components/APK_upload';
import ResultPage from './components/ResultPage'; // Import component mới
import './App.css';

// Component Wrapper để truy cập useNavigate trong App
function AppContent() {
  const navigate = useNavigate();
  const [apkData, setApkData] = useState(null); // Lưu trữ toàn bộ dữ liệu từ backend

  // Function được truyền xuống ApkUpload để cập nhật dữ liệu và chuyển hướng
  const handleUploadSuccess = (data) => {
    setApkData(data); // Lưu toàn bộ dữ liệu trả về
    // Chuyển hướng đến trang kết quả với SHA256
    navigate(`/results/${data.extracted_info.file_sha256}`);
  };

  const handleUploadError = (error) => {
    // Xử lý lỗi, có thể hiển thị thông báo lỗi trên trang upload
    console.error("Lỗi tải lên trong App.js:", error);
    setApkData(null); // Xóa dữ liệu cũ nếu có lỗi
    alert(`Lỗi: ${error}`); // Hoặc hiển thị lỗi một cách trực quan hơn
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>APK Ransomware Detector</h1>
      </header>
      <main>
        <Routes>
          <Route path="/" element={
            <ApkUpload 
              onUploadSuccess={handleUploadSuccess} 
              onUploadError={handleUploadError} 
            />
          } />
          <Route path="/results/:sha256" element={
            <ResultPage initialApkData={apkData} onUploadError={handleUploadError} />
          } />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router basename='/MultiViewAR-Detector'>
      <AppContent />
    </Router>
  );
}

export default App;