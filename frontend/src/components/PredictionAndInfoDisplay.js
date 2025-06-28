import React from 'react';
import PercentageCircle from './PercentageCircle';

function PredictionAndInfoDisplay({ predictions, info }) {
  if (!predictions || predictions.length === 0) return null;


  return (
    <div className='prediction-info-combined-display'>
      <h3>Kết quả dự đoán và thông tin APK</h3>
      <div className='content-wrapper'>
        <div className='prediction-section'>
        {predictions.map((p, index) => (
          <PercentageCircle score={p.score} label={p.label}/>
        ))}
        </div>

        <div className="apk-info-section">
          <h4>Thông tin APK đã trích xuất</h4> {/* Tiêu đề con */}
          <p><strong>Tên tệp:</strong> {info.original_filename}</p>
          <p><strong>SHA256:</strong> {info.file_sha256}</p>
          <p><strong>Tên gói:</strong> {info.package_name || "Đang cập nhật..."}</p>
        </div>
      </div>
    </div>
  );
}

export default PredictionAndInfoDisplay;