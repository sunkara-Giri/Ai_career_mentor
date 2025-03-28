const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const auth = require('../middleware/auth');
const User = require('../models/User');

// Configure multer for file upload
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const dir = 'uploads/resumes';
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    cb(null, dir);
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
  }
});

// Helper function to extract text from different file types
async function extractTextFromFile(filePath) {
  return new Promise((resolve, reject) => {
    console.log('Extracting text from file:', filePath);
    const pythonProcess = spawn('python', ['extract_text.py', filePath]);
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
      console.log('Text extraction output:', data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
      console.error('Text extraction error:', data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Text extraction failed: ${error}`));
      } else {
        try {
          const extractedText = JSON.parse(result);
          if (extractedText.error) {
            reject(new Error(extractedText.error));
          } else {
            resolve(extractedText.text);
          }
        } catch (err) {
          reject(new Error('Failed to parse extracted text'));
        }
      }
    });
  });
}

// Helper function to analyze resume using AI
async function analyzeResumeWithAI(text) {
  return new Promise((resolve, reject) => {
    console.log('Starting AI analysis...');
    const pythonProcess = spawn('python', ['ai_analyzer.py', text]);
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
      console.log('AI analysis output:', data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
      console.error('AI analysis error:', data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`AI analysis failed: ${error}`));
      } else {
        try {
          const analysis = JSON.parse(result);
          if (analysis.error) {
            reject(new Error(analysis.error));
          } else {
            resolve(analysis);
          }
        } catch (err) {
          reject(new Error('Failed to parse AI analysis'));
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

    console.log('File uploaded successfully:', req.file.path);

    // Extract text from the uploaded file
    const extractedText = await extractTextFromFile(req.file.path);
    console.log('Text extracted successfully');

    if (!extractedText || extractedText.trim().length === 0) {
      throw new Error('No text could be extracted from the resume');
    }

    // Analyze the resume using AI
    const analysis = await analyzeResumeWithAI(extractedText);
    console.log('Analysis completed successfully');

    // Update user's resume analysis in the database
    const user = await User.findById(req.user.id);
    user.resumeAnalysis = {
      ...analysis,
      filePath: req.file.path
    };
    await user.save();

    res.json({
      message: 'Resume analyzed successfully',
      analysis: analysis
    });
  } catch (error) {
    console.error('Resume analysis error:', error);
    res.status(500).json({ message: 'Failed to analyze resume', error: error.message });
  }
});

// Get resume analysis
router.get('/analysis', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user.resumeAnalysis) {
      return res.status(404).json({ message: 'No resume analysis found' });
    }
    res.json(user.resumeAnalysis);
  } catch (error) {
    console.error('Get analysis error:', error);
    res.status(500).json({ message: 'Failed to get resume analysis', error: error.message });
  }
});

module.exports = router; 