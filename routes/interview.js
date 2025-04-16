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

// Sample job database
const jobDatabase = [
  {
    title: "Software Development Engineer",
    company: "Amazon",
    match_score: 95,
    required_skills: ["Java", "Python", "AWS", "Microservices", "System Design", "Data Structures"],
    salary_range: "$130,000 - $190,000",
    location: "Hybrid",
    description: "Build and scale Amazon's e-commerce platforms and cloud services",
    benefits: ["Health Insurance", "RSUs", "401(k) Match", "Relocation Support"],
    growth_potential: "Senior SDE / Principal Engineer within 3 years"
  },
  {
    title: "Full Stack Software Engineer",
    company: "Microsoft",
    match_score: 93,
    required_skills: ["C#", ".NET", "React", "Azure", "SQL Server", "TypeScript"],
    salary_range: "$125,000 - $185,000",
    location: "Hybrid",
    description: "Develop enterprise-level applications using Microsoft technologies",
    benefits: ["Premium Healthcare", "Stock Options", "Flexible Hours", "Education Allowance"],
    growth_potential: "Senior Software Engineer / Technical Lead"
  },
  {
    title: "Software Engineer - AI/ML",
    company: "Google",
    match_score: 92,
    required_skills: ["Python", "TensorFlow", "Machine Learning", "Algorithms", "Distributed Systems"],
    salary_range: "$140,000 - $200,000",
    location: "On-site",
    description: "Work on cutting-edge AI/ML projects and Google's core search technology",
    benefits: ["Comprehensive Healthcare", "Google Stock Units", "Free Meals", "Gym Access"],
    growth_potential: "Senior AI Engineer / Research Scientist"
  },
  {
    title: "React Native Developer",
    company: "Meta",
    match_score: 90,
    required_skills: ["React Native", "JavaScript", "TypeScript", "Redux", "Mobile Development"],
    salary_range: "$120,000 - $180,000",
    location: "Remote",
    description: "Build mobile applications for Facebook, Instagram, and WhatsApp",
    benefits: ["Full Benefits", "Meta RSUs", "Wellness Programs", "Internet Allowance"],
    growth_potential: "Lead Mobile Engineer / Mobile Architect"
  },
  {
    title: "Backend Software Engineer",
    company: "Netflix",
    match_score: 89,
    required_skills: ["Java", "Spring Boot", "Microservices", "AWS", "Kafka", "Redis"],
    salary_range: "$135,000 - $195,000",
    location: "Hybrid",
    description: "Build scalable backend services for Netflix's streaming platform",
    benefits: ["Top-tier Healthcare", "Netflix Stock", "Unlimited PTO", "Home Office Setup"],
    growth_potential: "Senior Backend Engineer / Platform Architect"
  },
  {
    title: "Cloud Software Engineer",
    company: "Salesforce",
    match_score: 88,
    required_skills: ["Java", "Apex", "Lightning", "Cloud Computing", "API Development"],
    salary_range: "$115,000 - $175,000",
    location: "Remote",
    description: "Develop enterprise cloud solutions on Salesforce platform",
    benefits: ["Health & Dental", "Stock Purchase Plan", "Remote Work", "Learning Budget"],
    growth_potential: "Senior Cloud Engineer / Solutions Architect"
  },
  {
    title: "Software Engineer - Gaming",
    company: "Electronic Arts",
    match_score: 87,
    required_skills: ["C++", "Unity", "Unreal Engine", "Game Physics", "3D Graphics"],
    salary_range: "$110,000 - $170,000",
    location: "Hybrid",
    description: "Create immersive gaming experiences and game engine features",
    benefits: ["Healthcare", "EA Play Pro", "Fitness Benefits", "Game Library Access"],
    growth_potential: "Senior Game Engineer / Technical Director"
  },
  {
    title: "Software Security Engineer",
    company: "CrowdStrike",
    match_score: 86,
    required_skills: ["Python", "C++", "Security Protocols", "Threat Detection", "Cloud Security"],
    salary_range: "$125,000 - $185,000",
    location: "Remote",
    description: "Develop cybersecurity solutions and threat detection systems",
    benefits: ["Full Medical", "Stock Options", "Certification Support", "Home Office Allowance"],
    growth_potential: "Senior Security Engineer / Security Architect"
  },
  {
    title: "Blockchain Software Engineer",
    company: "Coinbase",
    match_score: 85,
    required_skills: ["Solidity", "Web3.js", "Smart Contracts", "Ethereum", "Blockchain"],
    salary_range: "$130,000 - $190,000",
    location: "Remote",
    description: "Build decentralized applications and blockchain infrastructure",
    benefits: ["Health Insurance", "Crypto Benefits", "Flexible Work", "Learning Credits"],
    growth_potential: "Lead Blockchain Engineer / Protocol Architect"
  },
  {
    title: "DevOps Software Engineer",
    company: "GitLab",
    match_score: 84,
    required_skills: ["Go", "Kubernetes", "Docker", "CI/CD", "Infrastructure as Code"],
    salary_range: "$120,000 - $180,000",
    location: "Remote",
    description: "Improve and maintain GitLab's DevOps platform",
    benefits: ["Remote-First Culture", "Stock Options", "Learning & Development", "Wellness Programs"],
    growth_potential: "Senior DevOps Engineer / Platform Lead"
  }
];

// Analyze answers and generate feedback
function analyzeAnswers(answers) {
  let skills = new Set();
  let experience = [];
  let workStyle = [];
  let careerGoals = [];
  let salaryExpectations = "";

  // Process each answer
  Object.values(answers).forEach(qa => {
    switch (qa.category) {
      case "Technical Skills":
        // Extract skills from the answer
        const skillWords = qa.answer.toLowerCase().match(/\b\w+\b/g) || [];
        const techSkills = skillWords.filter(word => 
          ["javascript", "python", "java", "react", "node", "aws", "docker", "kubernetes", 
           "sql", "mongodb", "typescript", "angular", "vue", "spring", "django", "flask",
           "redis", "postgresql", "mysql", "graphql", "rest", "git", "jenkins", "terraform",
           "azure", "gcp", "html", "css", "redux", "express", "php", "ruby", "rails",
           "scala", "kotlin", "swift", "flutter", "react native", "android", "ios",
           "machine learning", "ai", "data science", "tensorflow", "pytorch", "spark"]
            .includes(word)
        );
        techSkills.forEach(skill => skills.add(skill));
        break;
      
      case "Experience":
        experience.push(qa.answer);
        break;
      
      case "Work Culture":
        workStyle.push(qa.answer);
        break;
      
      case "Career Goals":
        careerGoals.push(qa.answer);
        break;
      
      case "Expectations":
        salaryExpectations = qa.answer;
        break;
    }
  });

  // Match jobs based on skills and experience
  const matchedJobs = jobDatabase
    .map(job => {
      const skillMatch = job.required_skills.filter(skill => 
        skills.has(skill.toLowerCase())
      ).length;
      
      const matchScore = Math.min(
        95,
        (skillMatch / job.required_skills.length) * 100
      );
      
      return {
        ...job,
        match_score: Math.round(matchScore)
      };
    })
    .filter(job => job.match_score > 70)
    .sort((a, b) => b.match_score - a.match_score);

  // Generate skills feedback
  let skillsFeedback = skills.size > 0
    ? `Based on your responses, you have demonstrated skills in ${Array.from(skills).join(', ')}. `
    : "Consider highlighting more specific technical skills in your responses. ";

  skillsFeedback += experience.length > 0
    ? "Your project experience shows practical application of these skills. "
    : "Try to provide more specific examples of projects where you've applied your skills. ";

  // Add career path suggestions
  const careerPathSuggestions = [
    "Consider pursuing cloud certifications to enhance your cloud computing expertise.",
    "Learning containerization and orchestration tools can open up DevOps opportunities.",
    "Developing expertise in AI/ML technologies can lead to specialized roles.",
    "Full-stack development skills are highly valued in startups and tech companies."
  ];

  return {
    jobs: matchedJobs.slice(0, 3),
    analysis: {
      skills_feedback: skillsFeedback,
      identified_skills: Array.from(skills),
      work_style: workStyle[0],
      career_trajectory: careerGoals[0],
      career_suggestions: careerPathSuggestions
    }
  };
}

// POST route to analyze interview answers
router.post('/analyze', async (req, res) => {
  try {
    const { answers } = req.body;
    
    if (!answers || Object.keys(answers).length === 0) {
      return res.status(400).json({ error: 'No answers provided' });
    }

    const analysis = analyzeAnswers(answers);
    res.json(analysis);
  } catch (error) {
    console.error('Error analyzing interview:', error);
    res.status(500).json({ error: 'Failed to analyze interview responses' });
  }
});

module.exports = router; 