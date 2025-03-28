const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const User = require('../models/User');

// Get job recommendations based on user's resume analysis
router.get('/recommendations', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user || !user.resumeAnalysis) {
      return res.json({ recommendations: [] });
    }

    // Extract skills and experience from resume analysis
    const { skills, experience } = user.resumeAnalysis;
    const userSkills = [...skills.technical, ...skills.soft];
    const yearsOfExperience = experience.years;

    // Mock job recommendations based on skills and experience
    // In a real application, this would come from a job database or API
    const recommendations = [
      {
        title: 'Senior Software Engineer',
        company: 'Tech Solutions Inc.',
        matchScore: calculateMatchScore(userSkills, ['JavaScript', 'React', 'Node.js', 'MongoDB']),
        requiredSkills: ['JavaScript', 'React', 'Node.js', 'MongoDB'],
        location: 'Remote',
        salary: '$120,000 - $150,000'
      },
      {
        title: 'Full Stack Developer',
        company: 'Digital Innovations',
        matchScore: calculateMatchScore(userSkills, ['Python', 'Django', 'React', 'PostgreSQL']),
        requiredSkills: ['Python', 'Django', 'React', 'PostgreSQL'],
        location: 'Hybrid',
        salary: '$100,000 - $130,000'
      },
      {
        title: 'Frontend Developer',
        company: 'Web Solutions',
        matchScore: calculateMatchScore(userSkills, ['React', 'TypeScript', 'CSS', 'HTML']),
        requiredSkills: ['React', 'TypeScript', 'CSS', 'HTML'],
        location: 'Remote',
        salary: '$90,000 - $120,000'
      }
    ].filter(job => job.matchScore > 50) // Only show jobs with >50% match
      .sort((a, b) => b.matchScore - a.matchScore); // Sort by match score

    res.json({ recommendations });
  } catch (err) {
    console.error('Error getting job recommendations:', err);
    res.status(500).json({ message: 'Error getting job recommendations' });
  }
});

// Helper function to calculate match score between user skills and job requirements
function calculateMatchScore(userSkills, requiredSkills) {
  const matchingSkills = userSkills.filter(skill => 
    requiredSkills.some(reqSkill => 
      reqSkill.toLowerCase().includes(skill.toLowerCase()) || 
      skill.toLowerCase().includes(reqSkill.toLowerCase())
    )
  );
  return Math.round((matchingSkills.length / requiredSkills.length) * 100);
}

module.exports = router; 