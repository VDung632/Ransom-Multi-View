import React from 'react';

function ApkInfoDisplay({ info }) {
  if (!info) return null;

  return (
    <div className="apk-info-display">
      <h3>Thông tin APK đã trích xuất</h3>
      <p><strong>Tên gốc tệp:</strong> {info.original_filename}</p>
      <p><strong>SHA256:</strong> {info.file_sha256}</p>
      {/* Các thông tin khác sẽ được hiển thị ở đây khi backend hỗ trợ */}
      <p><strong>Tên gói:</strong> {info.package_name || "Đang cập nhật..."}</p>
      {/* <p><strong>Quyền:</strong> {info.permissions ? info.permissions.join(', ') : "Đang cập nhật..."}</p> */}
    </div>
  );
}

export default ApkInfoDisplay;