import React from 'react';

function ImageDisplay({ imageUrls }) {
  if (!imageUrls || imageUrls.length === 0) return null;

  // Sắp xếp các URL ảnh để hiển thị theo thứ tự mong muốn
  const sortedImageUrls = [...imageUrls].sort((a, b) => {
    const order = ["xml", "arsc", "dex", "jar", "static"];
    const typeA = order.findIndex(type => a.includes(type));
    const typeB = order.findIndex(type => b.includes(type));
    return typeA - typeB;
  });

  const getImageType = (url) => {
  // Ví dụ URL: /extracted_images/SHA256_HASH/xml_images/image_name.png
  // Chúng ta muốn lấy "xml"
  const parts = url.split('/');
  // Tìm phần tử có chứa "_images"
   for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (part.endsWith('_images') && part !== 'extracted_images') { // Kiểm tra cả endsWith và không phải là 'extracted_images'
            return part.replace('_images', '');
        }
    }
    return '';
  }

  return (
    <div className="image-display">
      <h3>Ảnh đã trích xuất</h3>
      <div className="image-grid">
        {sortedImageUrls.map((url, index) => (
          <div key={index} className="image-item">
            {/* Backend chạy trên cổng 5000 */}
            <p className="image-type">Loại: <strong>{getImageType(url).toUpperCase()}</strong></p>
            <img src={`http://localhost:5000${url}`} alt={`Extracted Image ${index}`} />
            <p>{url.split('/').pop()}</p> {/* Hiển thị tên tệp ảnh */}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ImageDisplay;