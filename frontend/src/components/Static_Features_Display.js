import React, { useState } from 'react';
import './StaticFeatureDisplay.css'

// Hàm trợ giúp để phân tích cú pháp chuỗi danh sách Python từ CSV
const parsePythonCsvListString = (str) => {
  // Ví dụ chuỗi đầu vào từ CSV: "[\"\"android.permission.INTERNET\"\", \"\"android.permission.RECORD_AUDIO\"\"]"
  // Bước 1: Loại bỏ dấu ngoặc vuông bên ngoài
  let content = str.substring(1, str.length - 1);

  // Bước 2: Thay thế dấu ngoặc kép kép `""` thành dấu ngoặc kép đơn `"`
  // Điều này biến `""item""` thành `"item"`, hợp lệ cho JSON.parse
  content = content.replace(/""/g, '"');

  // Bước 3: Đặt nội dung vào một mảng JSON hợp lệ và phân tích cú pháp
  try {
    return JSON.parse(`[${content}]`);
  } catch (e) {
    console.error("Lỗi khi phân tích cú pháp chuỗi danh sách từ CSV:", str, e);
    // Phương án dự phòng: nếu JSON.parse thất bại, thử tách bằng dấu phẩy và làm sạch
    return content.split(',')
                  .map(item => item.trim().replace(/"/g, '')) // Loại bỏ dấu ngoặc kép còn sót
                  .filter(item => item !== ''); // Lọc bỏ các chuỗi rỗng
  }
};


function StaticFeaturesDisplay({ features }) {
  // State để điều khiển việc mở/đóng của phần chính "Đặc trưng tĩnh của APK"
  const [isMainSectionOpen, setIsMainSectionOpen] = useState(false); // Mặc định thu gọn

  // State để điều khiển việc mở/đóng của các phần con
  const [isBasicInfoOpen, setIsBasicInfoOpenOpen] = useState(false); // Mặc định thu gọn
  const [isDetailedListOpen, setIsDetailedListOpen] = useState(false); // Mặc định thu gọn

  if (!features || Object.keys(features).length === 0) {
    return <div className="static-features-display"><p>Không có thông tin đặc trưng tĩnh.</p></div>;
  }

  // Handle collapse các section
  const handleToggleMainSection = () => {
    setIsMainSectionOpen(!isMainSectionOpen);
  };

  const handleToggleBasicInfo = () => {
    setIsBasicInfoOpenOpen(!isBasicInfoOpen);
  };

  const handleToggleDetailedList = () => {
    setIsDetailedListOpen(!isDetailedListOpen);
  };

  // Tạo bản sao của features để không làm thay đổi props gốc
  const basicFeatures = { ...features };
  const listFeatures = {};
  const listKeys = ["Permissions", "Actions", "Services", "Categories"];

  // Tách các đặc trưng danh sách và các đặc trưng cơ bản
  listKeys.forEach(key => {
    if (key in basicFeatures) {
      listFeatures[key] = basicFeatures[key];
      delete basicFeatures[key];
    }
  });

  // Xóa các cột không cần thiết khác mà bạn không muốn hiển thị
  delete basicFeatures["App name"];
  delete basicFeatures["FileName"];
  delete basicFeatures["error"]; // Xử lý lỗi từ backend nếu có

  return (
    <div className="static-features-display">
      <div className='accordion-header' onClick={handleToggleMainSection}>
        <h3>Đặc trưng tĩnh của APK</h3>
        <span className={`arrow ${isMainSectionOpen ? 'open' : ''}`}>&#9660;</span>
      </div>

      {features.error && <p className="error-message">{features.error}</p>}

      {isMainSectionOpen && (
        <div className={`accordion-content ${isMainSectionOpen ? 'open' : ''}`}>
          {/* Phần Thông tin cơ bản */}
          <div className="accordion-section">
            <div className="accordion-header sub-header" onClick={handleToggleBasicInfo}>
              <h4>Thông tin cơ bản</h4>
              <span className={`arrow ${isBasicInfoOpen ? 'open' : ''}`}>&#9660;</span>
            </div>
            {isBasicInfoOpen && (
              <div className={`accordion-content sub-content ${isBasicInfoOpen ? 'open' : ''}`}>
                <table>
                  <tbody>
                    {Object.entries(basicFeatures).map(([key, value]) => (
                      <tr key={key}>
                        <td><strong>{key.replace(/Number of /, 'Số lượng ').replace(/App size/, 'Kích thước ứng dụng')}:</strong></td> {/* Dịch và làm đẹp tên cột */}
                        <td>{value !== null ? value : "N/A"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        

          <div className="accordion-section">
            <div className="accordion-header sub-header" onClick={handleToggleDetailedList}>
              <h4>Danh sách chi tiết</h4>
              <span className={`arrow ${isDetailedListOpen ? 'open' : ''}`}>&#9660;</span>
            </div>
            {isDetailedListOpen && (
              <div className={`accordion-content sub-content ${isDetailedListOpen ? 'open' : ''}`}>
                {listKeys.map(key => {
                  const rawValue = listFeatures[key];
                  // Sử dụng hàm mới để phân tích cú pháp chuỗi
                  const items = parsePythonCsvListString(rawValue);

                  return (
                    <div key={key} className="feature-list-item">
                      <h5>{key}: ({items.length})</h5>
                      {items.length > 0 ? (
                        <ul>
                          {items.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>Không có {key.toLowerCase()}.</p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    
    </div>
  
  );
}

export default StaticFeaturesDisplay;