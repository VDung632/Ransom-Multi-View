// frontend/src/components/Image_display.js
import React, { useState, useEffect } from 'react';
import './ImageDisplay.css'; // Thêm file CSS mới cho modal

function ImageDisplay({ imageUrls, limeImageUrls }) {

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
  if (!limeImageUrls || limeImageUrls.length === 0) return null;
  
  const getImageType = (url) => {
    const parts = url.split('/');
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (part.endsWith('_images') && part !== 'extracted_images') {
        return part.replace('_images', '');
      }
      else if (part.endsWith('_explained.png')){
        return part.split("_")[1];
      }
    }
    return '';
  };

  const groupedImages = {};
  const fileTypesOrder = ["xml", "arsc", "dex", "jar", "static"];

  fileTypesOrder.forEach(type => {
      groupedImages[type] = { extracted: null, lime: null };
  });

  // Điền ảnh trích xuất
  imageUrls.forEach(url => {
    const type = getImageType(url);
    if (type) {
      groupedImages[type].extracted = url;
    }
  });

  // Điền ảnh LIME
  limeImageUrls.forEach(url => {
    const type = getImageType(url);
    if (type) {
      groupedImages[type].lime = url;
    }
  });

  const handleImageClick = (url) => {
    setSelectedImage(url); // Khi ảnh được click, lưu URL vào state
  };

  const handleCloseModal = () => {
    setSelectedImage(null); // Đóng modal khi click ra ngoài hoặc nút đóng
  };

  return (
    <div className="image-display">
      <h3>Ảnh đã trích xuất và Giải thích LIME</h3>
      <div className="image-grid-container"> {/* Thêm container mới cho grid */}
        {fileTypesOrder.map(type => (
          (groupedImages[type].extracted || groupedImages[type].lime) ? (
            <div key={type} className="image-pair-group">
              <p className="image-type-header">Loại: <strong>{type.toUpperCase()}</strong></p>
              <div className="image-pair">
                {groupedImages[type].extracted && (
                  <div className="image-item">
                    <img 
                      src={`http://localhost:5000${groupedImages[type].extracted}`} 
                      alt={`Ảnh trích xuất loại ${type}`} 
                      onClick={() => handleImageClick(`http://localhost:5000${groupedImages[type].extracted}`)} 
                      style={{ cursor: 'pointer' }} 
                    />
                    <p>Ảnh gốc</p>
                  </div>
                )}
                {groupedImages[type].lime && (
                  <div className="image-item">
                    <img 
                      src={`http://localhost:5000${groupedImages[type].lime}`} 
                      alt={`Giải thích LIME loại ${type}`} 
                      onClick={() => handleImageClick(`http://localhost:5000${groupedImages[type].lime}`)} 
                      style={{ cursor: 'pointer' }} 
                    />
                    <p>Giải thích LIME</p>
                  </div>
                )}
              </div>
            </div>
          ) : null
        ))}
      </div>

      {selectedImage && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <img src={selectedImage} alt="Ảnh phóng to" className="modal-image" />
            <button className="close-button" onClick={handleCloseModal}>X</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageDisplay;