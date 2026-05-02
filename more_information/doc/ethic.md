Thực tế, Opta hay Google Cloud (đối tác của Premier League) mạnh nhất không phải là dự đoán trước trận (Pre-match), mà là Live Probability (Xác suất trực tiếp).


# 1. Cuộc chơi của Dòng chảy dữ liệu (Data Stream)

Các siêu máy tính như của Opta sử dụng hàng ngàn sự kiện mỗi giây (Pass, Shot, Pressure, Expected Goals - xG).

Trước trận, họ cũng chỉ dựa trên Elo, lịch sử đối đầu và đội hình ra sân. Độ chính xác lúc này thường chỉ quanh mức 54-56%.

Trong trận: Ngay khi một đội ghi bàn hoặc có thẻ đỏ, xác suất sẽ tăng vọt. 

Ví dụ: Nếu đội A dẫn 1-0 ở phút 70, xác suất thắng của họ sẽ vọt lên >80%.

Dự đoán lúc này dễ hơn rất nhiều vì "gạo đã thành cơm". Đó không còn là dự báo tương lai xa nữa, mà là phân tích thực tại.

# 2. Giá trị trong đồ án 
Việc dự đoán trước trận khó hơn gấp bội vì ta phải đối mặt với sự bất định tuyệt đối.

Mô hình đang trả lời câu hỏi: "Dựa trên thực lực (Elo) và phong độ (Rolling), ai có khả năng kiểm soát cuộc chơi cao hơn?"

Các nhà quản lý bóng đá cần những dự đoán này để lập kế hoạch chiến thuật, chứ không phải đợi đá xong mới biết ai thắng.

3. "Gót chân Achilles" của các siêu máy tính
Dù Opta rất mạnh, họ vẫn thường xuyên thất thế bởi những yếu tố mà dữ liệu khó chạm tới:

    Yếu tố tinh thần: Một đội bóng đang khủng hoảng nhưng vừa thay HLV (Hiệu ứng "New Manager Bounce").

    Tính chất trận đấu: Trận Derby vùng Merseyside hay North London luôn có những diễn biến phi logic mà Elo hay xG không giải thích nổi.

    Sự ngẫu nhiên: Một cú sút đập cột dọc nảy ra ngoài thay vì vào lưới có thể thay đổi hoàn toàn xác suất của Opta trong 1 giây.


"Khác với các mô hình dự báo trực tiếp (Live Update) dựa trên diễn biến đã xảy ra, nghiên cứu này tập trung vào bài toán khó hơn là Dự báo tiền trận (Pre-match Forecasting). Kết quả 51.0% - 54.3% cho thấy khả năng nhận diện quy luật từ các chỉ số tĩnh, giúp cung cấp cái nhìn khách quan về thực lực đội bóng trước khi tiếng còi khai cuộc vang lên."
