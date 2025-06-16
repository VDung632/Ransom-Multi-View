// frontend/src/components/APK_upload.js
import React, { useState, useCallback } from 'react';

function ApkUpload({ onUploadSuccess, onUploadError }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.apk')) {
      setSelectedFile(file);
      setError(null);
    } else {
      setSelectedFile(null);
      setError("Chỉ chấp nhận tệp APK. Vui lòng chọn lại.");
    }
  };

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);

    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.apk')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setSelectedFile(null);
        setError("Chỉ chấp nhận tệp APK. Vui lòng chọn lại.");
      }
    }
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Vui lòng chọn hoặc kéo thả một tệp APK.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('apk_file', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/upload-apk', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        onUploadSuccess(data); // Gọi callback truyền dữ liệu lên App.js
      } else {
        // Gọi callback onUploadError để App.js xử lý lỗi và hiển thị
        onUploadError(data.error || "Đã xảy ra lỗi khi tải lên tệp.");
        setError(data.error || "Đã xảy ra lỗi khi tải lên tệp."); // Cập nhật lỗi cục bộ để hiển thị trên form
      }
    } catch (error) {
      console.error("Lỗi mạng hoặc server:", error);
      onUploadError("Không thể kết nối đến server. Vui lòng kiểm tra backend.");
      setError("Không thể kết nối đến server. Vui lòng kiểm tra backend."); // Cập nhật lỗi cục bộ
    } finally {
      setLoading(false);
      // Giữ lại selectedFile để người dùng có thể tải lại hoặc xem thông tin tệp đã chọn
      // Hoặc reset nếu muốn bắt đầu lại hoàn toàn: setSelectedFile(null);
    }
  };

  return (
    <div className="apk-upload-container">
      <h2>Tải lên tệp APK để phân tích</h2>

      <div
        className={`drop-zone ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p>Kéo và thả tệp APK vào đây</p>
        <p>hoặc</p>
        <input
          type="file"
          accept=".apk"
          onChange={handleFileChange}
          id="apkFile"
          style={{ display: 'none' }}
        />
        <label htmlFor="apkFile" className="file-input-label">
          Chọn tệp APK
        </label>
      </div>

      {selectedFile && <p className="selected-file-name">Tệp đã chọn: <strong>{selectedFile.name}</strong></p>}
      
      {error && <p className="error-message">{error}</p>} {/* Hiển thị lỗi cục bộ */}

      <button onClick={handleUpload} disabled={!selectedFile || loading}>
        {loading ? 'Đang tải lên...' : 'Tải lên và Phân tích'}
      </button>
    </div>
  );
}

export default ApkUpload;