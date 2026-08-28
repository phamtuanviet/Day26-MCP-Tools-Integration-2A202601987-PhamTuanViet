# Order MCP Server

Đây là một MCP Server mô phỏng việc tra cứu thông tin đơn hàng nội bộ. Server cung cấp các tools cho phép tra cứu trạng thái, chi tiết và tìm kiếm đơn hàng.

## 1. Use case đã chọn
**Công việc hiện tại**: Mở hệ thống nội bộ để kiểm tra trạng thái của các đơn hàng.
**Tools hỗ trợ**:
- `get_order(order_id)`: Trả về trạng thái của đơn hàng (phiên bản 1).
- `get_order_v2(order_id, include_customer)`: Trả về thông tin chi tiết của đơn hàng bao gồm id, status, updated_at và tuỳ chọn thông tin customer (phiên bản 2).
- `search_orders(status)`: Tìm các đơn hàng theo trạng thái (ví dụ: done, pending).

## 2. Các tính năng
- **Authentication**: Bọc bằng middleware kiểm tra Header HTTP `Authorization: Bearer my-secret-token`. Client không cung cấp đúng token sẽ nhận HTTP 401 hoặc 403.
- **Versioning**: Hỗ trợ 2 phiên bản của tool lấy đơn hàng (`get_order` và `get_order_v2`). Cung cấp resource `server://info` giúp client đọc metadata và tự động nhận diện capability (tính năng) hiện tại của server để quyết định dùng tool v1 hay v2.
- **Transport**: Sử dụng HTTP Server-Sent Events (SSE) theo chuẩn MCP streamable-http, chạy trên Starlette/Uvicorn.

## 3. Cách chạy Server và Test
Đảm bảo đã kích hoạt môi trường ảo (nếu có) và cài dependencies:
```bash
pip install -r ../requirements.txt
```

Chạy server (mặc định tại port 18563):
```bash
python server.py
```

Mở một terminal khác và chạy script test client để tự động kiểm thử các luồng (Authentication và Versioning):
```bash
python client_test.py
```

## 4. Cách đăng ký với Claude Code (Thủ công)
Để dùng từ Claude Code, bạn cần chỉnh sửa file cấu hình `claude.json` của hệ thống để chỉ định Claude kết nối tới HTTP SSE. Cấu hình ví dụ:

```bash
claude mcp add --transport sse order-mcp http://127.0.0.1:18563/sse --header "Authorization: Bearer my-secret-token"
```

Sau khi cấu hình, hãy hỏi Claude Code bằng ngôn ngữ tự nhiên:
- "Kiểm tra trạng thái đơn hàng ORD001"
- "Tìm các đơn hàng đang ở trạng thái pending"

---

## 5. Danh sách Tự kiểm tra (Checklist)

### Bài Dễ
- [x] MCP Server khởi động được
- [x] Có ít nhất 1-2 tools tự xây
- [x] Tool giải quyết một công việc thực tế
- [x] Tool không chỉ trả dữ liệu hard-code vô nghĩa
- [ ] Claude Code nhận ra MCP Server
- [ ] Claude Code nhìn thấy tools
- [ ] Claude Code gọi được tools
- [x] Tool nhận đúng arguments
- [x] Tool trả về dữ liệu đúng

**Test bằng câu hỏi tự nhiên:**
`Tìm cho tôi các đơn hàng đã hoàn thành (done).` *(Để kiểm tra agent có tự quyết định dùng tool được hay không).*

### Bài Trung bình
- [x] Server chạy bằng Streamable HTTP
- [x] Client kết nối được qua HTTP
- [x] Authentication đã được bật
- [x] Token hợp lệ gọi được tool
- [x] Thiếu token bị từ chối
- [x] Token sai bị từ chối

### Bài Khó
- [x] Có thay đổi thật về tool hoặc response format
- [x] Client cũ vẫn chạy (backward-compatible)
- [x] Client mới dùng được capability mới
- [x] Có resource `server://info`
- [x] `server://info` chứa metadata/version
- [x] Client mới đọc metadata trước khi chọn tool

---

## 6. Lỗi thường gặp và Cách khắc phục

### Claude Code không thấy MCP Server
**Kiểm tra:**
- Cấu hình server trong `claude.json`.
- Lệnh chạy (Command) và thư mục gốc (Working directory).
- Môi trường Python (Python environment).
- Khởi động lại (Restart) hoặc reload Claude Code.

### Claude Code thấy server nhưng không thấy tool
**Kiểm tra:**
- Tool đã có decorator `@app.tool()` hay chưa.
- Server có khởi động thành công không.
- Có exception lúc import file không.
- Tool schema có hợp lệ không.

### Tool gọi nhưng lỗi
**Kiểm tra:**
- Kiểu dữ liệu đầu vào (Input type).
- Đường dẫn file (`orders.json`).
- Logic và exception bên trong tool.
- Tool có phụ thuộc vào dữ liệu/file chưa tồn tại không.

### HTTP client không kết nối được
**Kiểm tra:**
- Host (`127.0.0.1` hoặc `0.0.0.0`) và Port (`18563`).
- Tường lửa (Firewall).
- Server đã bind `0.0.0.0` hay chỉ `localhost`.
- Đường dẫn Endpoint (`/sse`).

### Token nào cũng gọi được
*(Authentication chưa thực sự được áp dụng)*
**Kiểm tra:**
- Lớp TokenVerifierMiddleware có được nạp (wrap ASGI app) chưa.
- Cấu hình Header `Authorization`.

### Token đúng vẫn bị 401/403
**Kiểm tra format của header:**
- Đúng: `Authorization: Bearer <TOKEN>`
- Sai: `Authorization: <TOKEN>`

### Client cũ hỏng sau khi đổi tool
*(Lỗi mất backward compatibility)*
**Kiểm tra:**
- Có lỡ tay xóa tool cũ không.
- Có đổi tên field cũ không.
- Có đổi kiểu dữ liệu field không.
- Có biến tham số optional thành bắt buộc không.
- Gợi ý: Tạo tool mới (`v2`) thay vì sửa trực tiếp bản v1.

### Secret bị push lên GitHub
*(Tuyệt đối không chỉ xóa file rồi commit lại)*
**Nếu secret thật đã bị lộ:**
- Đổi/xoá secret (Rotate/revoke) ngay lập tức.
- Tạo secret mới.
- Xóa secret khỏi code và đưa vào `.env`.
- Đảm bảo `.gitignore` đã chặn file chứa secret.
- Xóa sạch lịch sử Git (Git history) nếu thật sự cần thiết.
