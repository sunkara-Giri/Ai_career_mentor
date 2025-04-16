const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const auth = require('../middleware/auth');
const User = require('../models/User');

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = 'uploads/resumes';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF and Word documents are allowed.'));
    }
  },
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  }
});

// Helper function to extract text from PDF
async function extractTextFromPDF(filePath) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['extract_text.py', filePath]);
    let result = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python Error: ${data}`);
      reject(new Error('Failed to extract text from PDF'));
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}`));
      } else {
        try {
          const jsonResult = JSON.parse(result);
          resolve(jsonResult.text);
        } catch (error) {
          reject(new Error('Failed to parse Python output'));
        }
      }
    });
  });
}

// Helper function to analyze text with AI
async function analyzeTextWithAI(text) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['ai_resume_analyzer.py', text]);
    let result = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python Error: ${data}`);
      reject(new Error('Failed to analyze text with AI'));
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}`));
      } else {
        try {
          const analysisResult = JSON.parse(result);
          resolve(analysisResult);
        } catch (error) {
          reject(new Error('Failed to parse AI analysis result'));
        }
      }
    });
  });
}

// Upload and analyze resume
router.post('/upload', auth, upload.single('resume'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' });
    }

    // Extract text from the uploaded file
    const extractedText = await extractTextFromPDF(req.file.path);

    // Analyze text with AI
    const analysisResult = await analyzeTextWithAI(extractedText);

    // Save analysis results to user's document
    const user = await User.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    user.resumeAnalysis = {
      text: extractedText,
      entities: analysisResult.entities,
      education: analysisResult.education,
      experience: analysisResult.experience,
      skills: analysisResult.skills,
      jobRecommendations: analysisResult.job_recommendations,
      resumeImprovements: analysisResult.resume_improvements,
      lastUpdated: new Date()
    };

    await user.save();

    // Clean up uploaded file
    fs.unlinkSync(req.file.path);

    res.json({
      message: 'Resume analyzed successfully',
      analysis: user.resumeAnalysis
    });
  } catch (error) {
    console.error('Error processing resume:', error);
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    res.status(500).json({ message: 'Failed to process resume', error: error.message });
  }
});

// Get resume analysis
router.get('/analysis', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    if (!user.resumeAnalysis) {
      return res.json({
        message: 'No resume analysis found',
        analysis: null
      });
    }

    res.json(user.resumeAnalysis);
  } catch (error) {
    console.error('Error fetching resume analysis:', error);
    res.status(500).json({ message: 'Failed to fetch resume analysis', error: error.message });
  }
});

module.exports = router; 