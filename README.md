# AI-Driven Virtual Career Mentor

An intelligent career guidance system that helps students with job recommendations, resume analysis, and mock interview practice.

## Features

- **Job Recommendations**: Get personalized job suggestions based on your skills and interests
- **Resume Analysis**: Upload your resume for AI-powered analysis and improvement suggestions
- **Mock Interviews**: Practice with industry-specific interview questions and get instant feedback

## Prerequisites

- Node.js (v14 or higher)
- MongoDB
- npm or yarn

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-career-mentor
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory with the following variables:
```
PORT=5000
MONGODB_URI=mongodb://localhost:27017/career-mentor
JWT_SECRET=your-secret-key-here
NODE_ENV=development
```

4. Start the server:
```bash
npm run dev
```

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Login user

### Job Recommendations
- GET `/api/jobs/recommendations/:userId` - Get personalized job recommendations
- GET `/api/jobs` - Get all available jobs

### Resume Analysis
- POST `/api/resume/upload/:userId` - Upload and analyze resume
- GET `/api/resume/analysis/:userId` - Get resume analysis results

### Mock Interviews
- GET `/api/interview/questions/:industry` - Get interview questions by industry
- POST `/api/interview/analyze` - Analyze interview answer and get feedback

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 