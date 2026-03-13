# AI Agent
---

## Tính Năng Chính
- Agentic RAG: AI tự suy luận và sử dụng công cụ (`search_stories`, `crawl_new_story`) để học kiến thức mới.
- Bộ Não Gemini 2.5:Tích hợp " Gemini 2.5 Flash Lite" cho tốc độ phản hồi cực nhanh và hiểu tiếng Việt sâu sắc.
- Giao Diện Midnight Indigo: UI hiện đại (React 18 + Tailwind) với hiệu ứng Glassmorphism và chế độ tối huyền bí.
- Vận Hành Ổn Định:Tự động Retry (Tenacity), Docker hóa và sẵn sàng triển khai (Production Ready).

---

## Hướng Dẫn Sử Dụng
1. Khởi động Server:
   ```bash
   poetry run python src/app/main.py
   ```
2. **Truy cập:** [http://localhost:8000](http://localhost:8000)

---

## Kiến Trúc "Bộ Não"
Hệ thống vận hành theo quy trình "ReAct Agent":
- Reasoning: AI phân tích câu hỏi của bạn.
- Action: Tự động tìm kiếm trong kho dữ liệu hoặc đi "thu thập" thêm truyện mới nếu cần.
- Observation: Tổng hợp và trả lời dựa trên ngữ cảnh thực tế của truyện.
## Hạn chế của hệ thống

Mặc dù hệ thống RAG đã hoạt động và có thể tạo câu trả lời dựa trên dữ liệu đã lưu, tuy nhiên vẫn còn một số hạn chế:

- Chất lượng câu trả lời phụ thuộc vào dữ liệu đã crawl và lưu trữ trong hệ thống.
- Trong một số trường hợp, hệ thống có thể chưa truy xuất được đoạn dữ liệu phù hợp nhất để trả lời câu hỏi.
- Hệ thống hiện chỉ hoạt động tốt với tập dữ liệu có quy mô nhỏ đến trung bình.
- Một số câu hỏi phức tạp có thể chưa được trả lời chính xác.
- Một số chức năng của AI Agent vẫn đang trong quá trình hoàn thiện.

