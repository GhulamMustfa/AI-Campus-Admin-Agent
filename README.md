# Campus Admin Agent

An AI-powered campus administration system with conversational interface for managing student records and analytics.

## Features

- AI Chat Assistant with memory support
- Student CRUD operations
- Real-time analytics
- JWT authentication
- Streaming responses

## Quick Setup

1. **Clone and install**
```bash
git clone <repo-url>
cd campus-admin-agent
poetry install
```

2. **Environment setup**
Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URI=mongodb://localhost:27017
SECRET_KEY=your-secret-key
```

3. **Start services**
```bash
poetry run uvicorn backend.main:app --reload
```

4. **Test the API**
- API Docs: `http://localhost:8000/docs`
- Import `Campus_Admin_API_Collection.json` in Postman

## API Endpoints

### Authentication
- `POST /admin/signup` - Create admin account
- `POST /admin/login` - Get access token

### Chat
- `POST /chat` - AI assistant chat
- `POST /chat/stream` - Streaming chat responses

### Students
- `GET /students` - List all students
- `POST /students` - Create student
- `PATCH /students/{id}` - Update student
- `DELETE /students/{id}` - Delete student

### Analytics
- `GET /analytics` - Get dashboard data
- `GET /analytics/summary` - Get summary stats

## Usage Example

```bash
# 1. Create admin
curl -X POST "http://localhost:8000/admin/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123","name":"Admin"}'

# 2. Login
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'

# 3. Chat with AI
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"List all students","user_id":"test"}'
```

## Tech Stack

- Python
- FastAPI + MongoDB
- OpenAI Agent SDK with Gemini
- JWT authentication
