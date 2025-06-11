import React, { useState, useCallback } from 'react';

function ApkUpload({ onUploadSuccess, onUploadError }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false); // Trạng thái để theo dõi khi kéo qua vùng drop
  const [error, setError] = useState(null); // Trạng thái để lưu lỗi nếu có
  const [loading, setLoading] = useState(false); // Trạng thái để theo dõi quá trình tải lên

  // Xử lý khi người dùng chọn tệp bằng input
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.apk')) {
      setSelectedFile(file);
      setError(null); // Xóa lỗi nếu có
    } else {
      setSelectedFile(null);
      setError("Chỉ chấp nhận tệp APK. Vui lòng chọn lại.");
    }
  };

  // Xử lý sự kiện kéo qua (để cho phép drop)
  const handleDragOver = useCallback((event) => {
    event.preventDefault(); // Quan trọng: Ngăn chặn hành vi mặc định của trình duyệt (mở tệp)
    setIsDragOver(true);
  }, []);

  // Xử lý sự kiện rời khỏi vùng kéo
  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  // Xử lý sự kiện thả tệp
  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);

    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.apk')) {
        setSelectedFile(file);
        setError(null); // Xóa lỗi nếu có
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
        onUploadSuccess(data);
      } else {
        onUploadError(data.error || "Đã xảy ra lỗi khi tải lên tệp.");
      }
    } catch (error) {
      console.error("Lỗi mạng hoặc server:", error);
      onUploadError("Không thể kết nối đến server. Vui lòng kiểm tra backend.");
    } finally {
      // Có thể muốn giữ lại tệp đã chọn hoặc xóa nó tùy theo UX
      // setSelectedFile(null);
      setLoading(false);
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
          style={{ display: 'none' }} // Ẩn input mặc định
        />
        <label htmlFor="apkFile" className="file-input-label">
          Chọn tệp APK
        </label>
      </div>

      {selectedFile && <p className="selected-file-name">Tệp đã chọn: <strong>{selectedFile.name}</strong></p>}
      
      {/* Hiển thị lỗi nếu có */}
      {error && <p className="error-message">{setError}</p>}

      <button onClick={handleUpload} disabled={!selectedFile || loading}>
        {loading ? 'Đang tải lên...' : 'Tải lên và Phân tích'}
      </button>
    </div>
  );
}

export default ApkUpload;