import React from 'react';

function PredictionResult({ predictions }) {
  if (!predictions || predictions.length === 0) return null;

  return (
    <div className="prediction-result">
      <h3>Kết quả dự đoán</h3>
      {predictions.map((p, index) => (
        <p key={index}>
          Tệp: <strong>{p.image_name}</strong> - Điểm số: <strong>{p.score}</strong> - Nhãn: <strong className={p.label === "Ransomware" ? "ransomware-label" : "benign-label"}>{p.label}</strong>
        </p>
      ))}
    </div>
  );
}

export default PredictionResult;