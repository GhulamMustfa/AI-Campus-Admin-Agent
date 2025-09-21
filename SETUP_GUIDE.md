# 🚀 AI Campus Admin Agent - Setup Guide

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API Key

## 🛠 Quick Setup

### 1. **Install Dependencies**
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 2. **Environment Configuration**
```bash
# Copy the environment template
cp env_template.txt .env

# Edit .env with your actual values
nano .env
```

**Required Environment Variables:**
```env
OPENAI_API_KEY=your_openai_api_key_here
DB_URI=mongodb://localhost:27017
DB_NAME=campus_admin_agent
```

### 3. **Start MongoDB**
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas (cloud)
# Update DB_URI in .env to your Atlas connection string
```

### 4. **Run the Server**
```bash
# Using the startup script
python run_server.py

# Or directly with uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### **Chat Endpoints**
- `POST /chat` - Normal chat
- `POST /chat/stream` - Streaming chat (SSE)

### **Student Management**
- `GET /api/v1/students` - List all students
- `POST /api/v1/students` - Create student
- `GET /api/v1/students/{id}` - Get student
- `PATCH /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student

### **Analytics**
- `GET /api/v1/analytics` - Full analytics
- `GET /api/v1/analytics/summary` - Quick summary
- `GET /api/v1/analytics/departments` - Department breakdown
- `GET /api/v1/analytics/recent` - Recent enrollments

### **System**
- `GET /` - Server status
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🧪 Testing with Postman

### **1. Test Chat Endpoint**
```json
POST /chat
{
    "message": "Add a new student named John Doe with ID 12345 in Computer Science department",
    "user_id": "test_user"
}
```

### **2. Test Student Creation**
```json
POST /api/v1/students
{
    "name": "John Doe",
    "student_id": "12345",
    "department": "Computer Science",
    "email": "john.doe@university.edu"
}
```

### **3. Test Analytics**
```json
GET /api/v1/analytics
```

## 🔧 Troubleshooting

### **Database Connection Issues**
```bash
# Check MongoDB status
mongosh --eval "db.adminCommand('ping')"

# Check connection string format
# Local: mongodb://localhost:27017
# Atlas: mongodb+srv://username:password@cluster.mongodb.net/
```

### **API Key Issues**
```bash
# Verify OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## 📊 Features Implemented

✅ **Core Agent**
- OpenAI GPT-4o-mini integration
- Tool calling with function definitions
- Conversation memory
- Streaming responses (SSE)

✅ **Student Management**
- CRUD operations
- Input validation
- Error handling

✅ **Analytics**
- Total students count
- Department breakdown
- Recent enrollments
- Activity tracking (mock)

✅ **API Features**
- FastAPI with automatic docs
- CORS support
- Logging
- Health checks

## 🎯 Next Steps

1. **Test all endpoints** with Postman
2. **Add sample data** to MongoDB
3. **Test chat functionality** with tool calling
4. **Verify streaming** responses
5. **Create Postman collection** for testing

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify environment variables
3. Test database connectivity
4. Check API key validity

---

**Happy Coding! 🎉**
