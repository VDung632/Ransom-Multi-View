// frontend/src/components/ResultPage.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ApkInfoDisplay from './APK_info_display';
import PredictionResult from './APK_predict_result';
import ImageDisplay from './Image_display';
import StaticFeaturesDisplay from './Static_Features_Display';

function ResultPage({ initialApkData, onUploadError }) {
  const { sha256 } = useParams(); // Lấy sha256 từ URL
  const [apkInfo, setApkInfo] = useState(initialApkData ? initialApkData.extracted_info : null);
  const [predictions, setPredictions] = useState(initialApkData ? initialApkData.predictions : []);
  const [imageUrls, setImageUrls] = useState(initialApkData ? initialApkData.image_urls : []);
  const [loading, setLoading] = useState(!initialApkData); // Nếu không có initialData thì đang loading
  const [error, setError] = useState(null);

  useEffect(() => {
    // Nếu không có dữ liệu ban đầu (initialApkData), fetch lại từ backend
    if (!initialApkData && sha256) {
      const fetchResults = async () => {
        setLoading(true);
        setError(null);
        try {
          // Bạn cần một endpoint mới ở backend để lấy thông tin theo SHA256
          // Ví dụ: GET /results/<sha256>
          const response = await fetch(`http://localhost:5000/results/${sha256}`);
          const data = await response.json();

          if (response.ok) {
            setApkInfo(data.extracted_info);
            setPredictions(data.predictions);
            setImageUrls(data.image_urls);
          } else {
            setError(data.error || "Không thể tải kết quả từ server.");
            onUploadError(data.error || "Không thể tải kết quả từ server."); // Truyền lỗi lên App.js
          }
        } catch (err) {
          console.error("Lỗi khi fetch kết quả:", err);
          setError("Không thể kết nối đến server để lấy kết quả.");
          onUploadError("Không thể kết nối đến server để lấy kết quả."); // Truyền lỗi lên App.js
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

  // Nếu không có dữ liệu hoặc sha256, thông báo cho người dùng quay lại trang chủ
  if (!apkInfo && !sha256) {
    return <p>Không có kết quả để hiển thị. Vui lòng tải lên tệp APK từ <a href="/">trang chủ</a>.</p>;
  }

  return (
    <div className="results-section">
      <ApkInfoDisplay info={apkInfo} />
      <PredictionResult predictions={predictions} />
      {apkInfo?.static_features && (
        <StaticFeaturesDisplay features={apkInfo.static_features} />
      )}
      <ImageDisplay imageUrls={imageUrls} />
      <p><a href="/">Quay lại trang chủ để tải lên tệp khác</a></p>
    </div>
  );
}

export default ResultPage;