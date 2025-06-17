// frontend/src/components/ResultPage.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
// import ApkInfoDisplay from './APK_info_display'; // Xóa dòng này
import PredictionAndInfoDisplay from './PredictionAndInfoDisplay'; // Import component mới
import ImageDisplay from './Image_display';
import StaticFeaturesDisplay from './Static_Features_Display';
import '../App.css'; 

function ResultPage({ initialApkData, onUploadError }) {
  const { sha256 } = useParams();
  const [apkInfo, setApkInfo] = useState(initialApkData ? initialApkData.extracted_info : null);
  const [predictions, setPredictions] = useState(initialApkData ? initialApkData.predictions : []);
  const [imageUrls, setImageUrls] = useState(initialApkData ? initialApkData.image_urls : []);
  const [lime_image_urls, SetLimeUrls] = useState(initialApkData ? initialApkData.lime_image_urls : [])
  const [loading, setLoading] = useState(!initialApkData);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!initialApkData && sha256) {
      const fetchResults = async () => {
        setLoading(true);
        setError(null);
        try {
          const response = await fetch(`http://localhost:5000/results/${sha256}`);
          const data = await response.json();

          if (response.ok) {
            setApkInfo(data.extracted_info);
            setPredictions(data.predictions);
            setImageUrls(data.image_urls);
            SetLimeUrls(data.lime_image_urls)
          } else {
            setError(data.error || "Không thể tải kết quả từ server.");
            onUploadError(data.error || "Không thể tải kết quả từ server.");
          }
        } catch (err) {
          console.error("Lỗi khi fetch kết quả:", err);
          setError("Không thể kết nối đến server để lấy kết quả.");
          onUploadError("Không thể kết nối đến server để lấy kết quả.");
        } finally {
          setLoading(false);
        }
      };

      fetchResults();
    }
  }, [initialApkData, sha256, onUploadError]);

  if (loading) {
    return <p>Đang tải kết quả...</p>;
  }

  if (error) {
    return <p className="error-message">Lỗi: {error}</p>;
  }

  if (!apkInfo && !sha256) {
    return <p>Không có kết quả để hiển thị. Vui lòng tải lên tệp APK từ <a href="/">trang chủ</a>.</p>;
  }

  return (
    <div className="results-section">
      {/* Chỉ render một component mới chứa cả Prediction và Info */}
      <PredictionAndInfoDisplay predictions={predictions} info={apkInfo} />
      
      {apkInfo?.static_features && (
        <StaticFeaturesDisplay features={apkInfo.static_features} />
      )}
      <ImageDisplay imageUrls={imageUrls} limeImageUrls={lime_image_urls} />
      <p><a href="/">Quay lại trang chủ để tải lên tệp khác</a></p>
    </div>
  );
}

export default ResultPage;