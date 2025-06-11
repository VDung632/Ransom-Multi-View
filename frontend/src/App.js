import React, { useState } from 'react';
import ApkUpload from './components/APK_upload';
import ApkInfoDisplay from './components/APK_info_display';
import PredictionResult from './components/APK_predict_result';
import ImageDisplay from './components/Image_display';
import StaticFeaturesDisplay from './components/Static_Features_Display';
import './App.css'; // Để có thể thêm CSS tùy chỉnh

function App() {
  const [apkInfo, setApkInfo] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [imageUrls, setImageUrls] = useState([]);
  const [loading, setLoading] = useState(false); // loading toàn cục
  const [error, setError] = useState(null); // error toàn cục

  const handleUploadSuccess = (data) => {
    setApkInfo(data.extracted_info);
    setPredictions(data.predictions);
    setImageUrls(data.image_urls);
    setLoading(false);
    setError(null);
  };

  const handleUploadError = (err) => {
    setError(err);
    setLoading(false);
    setApkInfo(null);
    setPredictions([]);
    setImageUrls([]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>APK Ransomware Detector</h1>
      </header>
      <main>
        <ApkUpload 
          onUploadSuccess={handleUploadSuccess} 
          onUploadError={handleUploadError}
        />

        {loading && <p>Đang xử lý APK của bạn, vui lòng đợi...</p>}
        {error && <p className="error-message">Lỗi: {error}</p>}

        {apkInfo && (
          <div className="results-section">
            <ApkInfoDisplay info={apkInfo} />
            <PredictionResult predictions={predictions} />
            {apkInfo.static_features && (
              <StaticFeaturesDisplay features={apkInfo.static_features} />
            )}
            <ImageDisplay imageUrls={imageUrls} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;