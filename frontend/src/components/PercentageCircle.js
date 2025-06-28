// frontend/src/components/PercentageCircle.js
import React from 'react';

function PercentageCircle({ score, label }) {
  const radius = 60; // Bán kính của vòng tròn
  const strokeWidth = 10;
  const circleSize = radius * 2 + strokeWidth; // Tổng kích thước SVG
  const center = radius + strokeWidth / 2 // Tọa độ tâm
  const circumference = 2 * Math.PI * radius; // Chu vi vòng tròn
  
  // Điểm số từ model thường là một giá trị float từ 0 đến 1
  // 0 là benign và 1 là ransom
  // Chuyển đổi thành phần trăm (0-100)
  const percentage = Math.round(score * 100); 

  // Tính toán phần màu xanh (Benign) và màu đỏ (Ransomware)
  let benignPercentage = 0;
  let ransomwarePercentage = 0;

  // Ví dụ: 
  // kết quả dự đoán là 0% => 100% benign và 0% ransom
  // kết quả dự đoán là 30% => 70% benign và 30% ransom => benign
  benignPercentage = 100 - percentage; 
  ransomwarePercentage = percentage

  // Thuộc tính stroke-dasharray và stroke-dashoffset cho SVG
  const benignStrokeDashoffset = circumference - (benignPercentage / 100) * circumference;
  const ransomwareStrokeDashoffset = circumference - (ransomwarePercentage / 100) * circumference;

  const benignColor = '#4CAF50'; // Xanh lá
  const ransomwareColor = '#f44336'; // Đỏ

  return (
    <div className="percentage-circle-container">
      <svg
        className="percentage-circle-svg"
        width={circleSize} // Thêm một chút không gian cho stroke-width
        height={circleSize}
        viewBox={`0 0 ${circleSize} ${circleSize}`}
      >
        {/* Đường tròn nền (có thể là màu xám hoặc màu tổng) */}
        <circle
          stroke="#eee"
          strokeWidth={strokeWidth}
          fill="transparent"
          r={radius}
          cx={radius + 5}
          cy={radius + 5}
        />
        
        {/* Phần màu xanh (Benign) */}
        <circle
          stroke={benignColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={benignStrokeDashoffset}
          fill="transparent"
          r={radius}
          cx={radius + 5}
          cy={radius + 5}
          transform={`rotate(-90 ${center} ${center})`} /* Bắt đầu từ phía trên */
        />

        {/* Phần màu đỏ (Ransomware) */}
        <circle
          stroke={ransomwareColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={ransomwareStrokeDashoffset}
          fill="transparent"
          r={radius}
          cx={radius + 5}
          cy={radius + 5}
          // Xoay để phần đỏ bắt đầu ngay sau phần xanh
          transform={`rotate(${benignPercentage * 3.6 - 90} ${center} ${center})`} /* 3.6 độ = 1% */
        />

        <text
            x={center} 
            y={center - 10} /* Dịch lên trên một chút cho nhãn */
            textAnchor="middle" 
            dominantBaseline="central" 
            className={label === "Ransomware" ? "ransomware-label" : "benign-label"}
            style={{ fontSize: '0.9em', fontWeight: 'bold' }}
        >
            {label}
        </text>

        <text 
        x={center} 
        y={center + 15} /* Dịch xuống dưới một chút cho phần trăm */
        textAnchor="middle" 
        dominantBaseline="central" 
        className="score-percentage"
        style={{ fontSize: '1.5em', fontWeight: 'bold' }}
        >
          {percentage}%
        </text>
      </svg>
    </div>
  );
}

export default PercentageCircle;