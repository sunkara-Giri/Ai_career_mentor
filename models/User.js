const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  skills: {
    type: [String],
    default: []
  },
  interests: {
    type: [String],
    default: []
  },
  resumePath: {
    type: String
  },
  resumeAnalysis: {
    skills: {
      technical: [String],
      soft: [String],
      missing: [String]
    },
    experience: {
      years: Number,
      relevantProjects: [String],
      suggestions: [String]
    },
    education: {
      degree: String,
      relevance: String,
      suggestions: [String]
    },
    format: {
      score: Number,
      improvements: [String]
    },
    jobFit: {
      recommendedRoles: [{
        title: String,
        match: Number,
        missingSkills: [String]
      }]
    },
    overallScore: Number,
    improvements: [String]
  },
  jobPreferences: {
    roles: [String],
    locations: [String],
    experienceLevel: String,
    salary: {
      min: Number,
      max: Number,
      currency: String
    }
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

// Pre-save middleware to hash password
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) {
    return next();
  }
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (err) {
    next(err);
  }
});

// Method to compare passwords
userSchema.methods.comparePassword = async function(candidatePassword) {
  try {
    return await bcrypt.compare(candidatePassword, this.password);
  } catch (err) {
    throw err;
  }
};

module.exports = mongoose.model('User', userSchema); 