const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const auth = require('../middleware/auth');
const User = require('../models/User');

// Configure multer for video upload
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const dir = 'uploads/videos';
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    cb(null, dir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({
  storage: storage,
  fileFilter: function (req, file, cb) {
    const filetypes = /mp4|webm|ogg/;
    const mimetype = filetypes.test(file.mimetype);
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    
    if (mimetype && extname) {
      return cb(null, true);
    }
    cb(new Error('Only video files (MP4, WEBM, OGG) are allowed!'));
  }
});

// Get interview questions based on job role
router.get('/questions', auth, async (req, res) => {
  try {
    const { role } = req.query;
    let questions;

    // Different questions based on role
    switch (role?.toLowerCase()) {
      case 'frontend':
        questions = [
          {
            id: 1,
            question: "Can you explain the difference between React's state and props?",
            category: 'Technical',
            followUp: "How do you decide when to use state vs props?"
          },
          {
            id: 2,
            question: "What is the Virtual DOM and how does it work?",
            category: 'Technical',
            followUp: "Can you explain the reconciliation process?"
          },
          {
            id: 3,
            question: "Describe a challenging project you worked on and how you solved the problems.",
            category: 'Behavioral',
            followUp: "What would you do differently if you had to do it again?"
          }
        ];
        break;

      case 'backend':
        questions = [
          {
            id: 1,
            question: "Explain RESTful API design principles.",
            category: 'Technical',
            followUp: "How do you handle API versioning?"
          },
          {
            id: 2,
            question: "How do you optimize database queries for better performance?",
            category: 'Technical',
            followUp: "Can you give an example of indexing strategy?"
          },
          {
            id: 3,
            question: "Tell me about a time when you had to debug a complex server issue.",
            category: 'Behavioral',
            followUp: "What tools did you use for debugging?"
          }
        ];
        break;

      default:
        questions = [
          {
            id: 1,
            question: "Tell me about yourself and your background in technology.",
            category: 'General',
            followUp: "What made you choose this career path?"
          },
          {
            id: 2,
            question: "What are your greatest strengths and weaknesses as a developer?",
            category: 'Behavioral',
            followUp: "How are you working on improving your weaknesses?"
          },
          {
            id: 3,
            question: "Where do you see yourself in 5 years?",
            category: 'Career Goals',
            followUp: "What steps are you taking to achieve these goals?"
          },
          {
            id: 4,
            question: "Describe a challenging project you worked on.",
            category: 'Experience',
            followUp: "What were the key learnings from this project?"
          },
          {
            id: 5,
            question: "How do you stay updated with the latest technology trends?",
            category: 'Professional Development',
            followUp: "What resources do you use for learning?"
          }
        ];
    }

    res.json({ questions });
  } catch (err) {
    console.error('Error getting interview questions:', err);
    res.status(500).json({ message: 'Error fetching questions', error: err.message });
  }
});

// Submit interview recording
router.post('/submit/:userId', auth, upload.single('video'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'Please upload a video recording' });
    }

    const user = await User.findById(req.params.userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Mock AI analysis of the interview (replace with actual AI analysis in production)
    const feedback = {
      confidence: {
        score: 85,
        feedback: [
          'Good eye contact maintained',
          'Clear and steady voice',
          'Professional posture',
          'Consider using more hand gestures to emphasize points'
        ]
      },
      communication: {
        score: 90,
        feedback: [
          'Well-structured responses',
          'Good use of technical terminology',
          'Clear explanation of complex concepts',
          'Could improve pace of speaking slightly'
        ]
      },
      technical_accuracy: {
        score: 88,
        feedback: [
          'Strong technical knowledge demonstrated',
          'Good real-world examples provided',
          'Consider adding more specific metrics to examples',
          'Could elaborate more on system design decisions'
        ]
      },
      improvements: [
        'Practice more concise responses',
        'Prepare more quantifiable examples',
        'Research company-specific technical challenges',
        'Prepare questions for the interviewer'
      ],
      overall_score: 88
    };

    res.json({
      message: 'Interview recording analyzed successfully',
      feedback
    });
  } catch (err) {
    console.error('Error analyzing interview:', err);
    res.status(500).json({ message: 'Error analyzing interview', error: err.message });
  }
});

module.exports = router; 