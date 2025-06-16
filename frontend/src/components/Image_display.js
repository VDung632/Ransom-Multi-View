// frontend/src/components/Image_display.js
import React, { useState, useEffect } from 'react';
import './ImageDisplay.css'; // Thêm file CSS mới cho modal

function ImageDisplay({ imageUrls }) {

  const [selectedImage, setSelectedImage] = useState(null); // State để lưu URL ảnh phóng to

  // useEffect để quản lý class 'no-scroll' trên body
  useEffect(() => {
    if (selectedImage) {
      document.body.classList.add('no-scroll');
    } else {
      document.body.classList.remove('no-scroll');
    }
    // Cleanup function để đảm bảo class được xóa khi component unmount
    return () => {
      document.body.classList.remove('no-scroll');
    };
  }, [selectedImage]); // Chạy lại khi selectedImage thay đổi

  if (!imageUrls || imageUrls.length === 0) return null;
  
  // Sắp xếp các URL ảnh để hiển thị theo thứ tự mong muốn
  const sortedImageUrls = [...imageUrls].sort((a, b) => {
    const order = ["xml", "arsc", "dex", "jar", "static"];
    const typeA = order.findIndex(type => a.includes(type));
    const typeB = order.findIndex(type => b.includes(type));
    return typeA - typeB;
  });

  const getImageType = (url) => {
    const parts = url.split('/');
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (part.endsWith('_images') && part !== 'extracted_images') {
        return part.replace('_images', '');
      }
    }
    return '';
  };

  const handleImageClick = (url) => {
    setSelectedImage(url); // Khi ảnh được click, lưu URL vào state
  };

  const handleCloseModal = () => {
    setSelectedImage(null); // Đóng modal khi click ra ngoài hoặc nút đóng
  };

  return (
    <div className="image-display">
      <h3>Ảnh đã trích xuất</h3>
      <div className="image-grid">
        {sortedImageUrls.map((url, index) => (
          <div key={index} className="image-item">
            <p className="image-type">Loại: <strong>{getImageType(url).toUpperCase()}</strong></p>
            {/* Thêm onClick handler vào ảnh */}
            <img 
              src={`http://localhost:5000${url}`} 
              alt={`Extracted Image ${index}`} 
              onClick={() => handleImageClick(`http://localhost:5000${url}`)} 
              style={{ cursor: 'pointer' }} // Thêm cursor để người dùng biết có thể click
            />
          </div>
        ))}
      </div>

      {/* Modal hiển thị ảnh phóng to */}
      {selectedImage && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}> {/* Ngăn chặn click lan truyền */}
            <img src={selectedImage} alt="Phóng to" className="modal-image" />
            <button className="close-button" onClick={handleCloseModal}>X</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageDisplay;