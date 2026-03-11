# AI Story Agent

Hệ thống **AI Agent (RAG)** thông minh, chuyên nghiệp, tự động thu thập và giải đáp thắc mắc về truyện từ TruyenFull.

---

## Tính Năng Chính
- **Agentic RAG:** AI tự suy luận và sử dụng công cụ (`search_stories`, `crawl_new_story`) để học kiến thức mới.
- **Bộ Não Gemini 2.5:** Tích hợp **Gemini 2.5 Flash Lite** cho tốc độ phản hồi cực nhanh và hiểu tiếng Việt sâu sắc.
- **Giao Diện Midnight Indigo:** UI hiện đại (React 18 + Tailwind) với hiệu ứng Glassmorphism và chế độ tối huyền bí.
- **Vận Hành Ổn Định:** Tự động Retry (Tenacity), Docker hóa và sẵn sàng triển khai (Production Ready).

---

## Hướng Dẫn Sử Dụng
1. **Khởi động Server:**
   ```bash
   poetry run python src/app/main.py
   ```
2. **Truy cập:** [http://localhost:8000](http://localhost:8000)

---

## Kiến Trúc "Bộ Não"
Hệ thống vận hành theo quy trình **ReAct Agent**:
- **Reasoning:** AI phân tích câu hỏi của bạn.
- **Action:** Tự động tìm kiếm trong kho dữ liệu hoặc đi "thu thập" thêm truyện mới nếu cần.
- **Observation:** Tổng hợp và trả lời dựa trên ngữ cảnh thực tế của truyện.


