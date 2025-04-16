from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
import torch
import logging
import json
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIResumeAnalyzer:
    def __init__(self):
        """Initialize the AI Resume Analyzer with necessary models."""
        try:
            # Initialize NER pipeline for entity extraction
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize text classification for section identification
            self.section_classifier = pipeline(
                "text-classification",
                model="microsoft/deberta-v3-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize sentence transformer for semantic matching
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model="gpt2",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize zero-shot classification for skill identification
            self.zero_shot = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("AI Resume Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI Resume Analyzer: {str(e)}")
            raise

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from resume text."""
        try:
            entities = self.ner_pipeline(text)
            
            # Organize entities by type
            entity_dict = {
                'PER': [],  # Person names
                'ORG': [],  # Organizations
                'LOC': [],  # Locations
                'MISC': []  # Other entities
            }
            
            for entity in entities:
                entity_type = entity['entity'][2:]  # Remove B- or I- prefix
                if entity_type in entity_dict:
                    entity_dict[entity_type].append(entity['word'])
            
            return entity_dict
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}")
            return {}

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text."""
        try:
            # Define education-related keywords
            edu_keywords = ['education', 'degree', 'bachelor', 'master', 'phd', 'diploma', 'certification']
            
            # Split text into sections
            sections = text.split('\n\n')
            
            education_info = []
            for section in sections:
                # Check if section is about education
                if any(keyword in section.lower() for keyword in edu_keywords):
                    # Extract degree and institution
                    degree_match = re.search(r'(Bachelor|Master|PhD|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?S|M\.?S)[^,]*', section)
                    institution_match = re.search(r'([A-Z][a-zA-Z\s&]+(?:University|College|Institute|School))', section)
                    
                    if degree_match or institution_match:
                        education_info.append({
                            'degree': degree_match.group(0) if degree_match else '',
                            'institution': institution_match.group(0) if institution_match else '',
                            'section': section.strip()
                        })
            
            return education_info
        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}")
            return []

    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume text."""
        try:
            # Define experience-related keywords
            exp_keywords = ['experience', 'work', 'employment', 'job', 'position']
            
            # Split text into sections
            sections = text.split('\n\n')
            
            experience_info = []
            for section in sections:
                # Check if section is about experience
                if any(keyword in section.lower() for keyword in exp_keywords):
                    # Extract company and position
                    company_match = re.search(r'([A-Z][a-zA-Z\s&]+(?:Inc\.|Corp\.|LLC|Ltd\.|Company))', section)
                    position_match = re.search(r'(Senior|Junior|Lead|Manager|Director|Engineer|Developer|Designer|Architect|Consultant|Analyst|Scientist)[^,]*', section)
                    
                    if company_match or position_match:
                        experience_info.append({
                            'company': company_match.group(0) if company_match else '',
                            'position': position_match.group(0) if position_match else '',
                            'section': section.strip()
                        })
            
            return experience_info
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
            return []

    def extract_skills(self, text: str) -> List[Dict[str, float]]:
        """Analyze skills and their proficiency levels."""
        try:
            # Define skill categories and keywords
            skill_categories = {
                'programming': ['python', 'java', 'javascript', 'c++', 'sql', 'ruby', 'php', 'swift', 'kotlin'],
                'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel', 'express', 'node.js'],
                'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'elasticsearch'],
                'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
                'tools': ['git', 'jira', 'confluence', 'slack', 'trello', 'bitbucket', 'github'],
                'soft_skills': ['leadership', 'communication', 'problem-solving', 'teamwork', 'project management'],
                'ai_ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp'],
                'mobile': ['android', 'ios', 'react native', 'flutter', 'mobile development'],
                'web': ['html', 'css', 'sass', 'less', 'webpack', 'babel', 'rest api', 'graphql']
            }
            
            # Convert text to lowercase for matching
            text_lower = text.lower()
            
            # Analyze skills using zero-shot classification
            skills = []
            for category, keywords in skill_categories.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        # Use zero-shot classification to determine if the skill is mentioned
                        result = self.zero_shot(
                            text_lower,
                            candidate_labels=[f"has {keyword} experience", f"does not have {keyword} experience"]
                        )
                        
                        if result['scores'][0] > 0.5:  # If confidence is high
                            proficiency = self._calculate_skill_proficiency(text_lower, keyword)
                            skills.append({
                                'name': keyword,
                                'category': category,
                                'proficiency': proficiency,
                                'confidence': result['scores'][0]
                            })
            
            return skills
        except Exception as e:
            logger.error(f"Error in skill analysis: {str(e)}")
            return []

    def _calculate_skill_proficiency(self, text: str, skill: str) -> float:
        """Calculate proficiency level for a skill based on context."""
        try:
            # Define proficiency indicators
            indicators = {
                'expert': 1.0,
                'advanced': 0.8,
                'proficient': 0.6,
                'intermediate': 0.4,
                'basic': 0.2
            }
            
            # Find the context around the skill
            skill_index = text.find(skill)
            if skill_index == -1:
                return 0.0
                
            # Look for proficiency indicators in the context
            context = text[max(0, skill_index-50):min(len(text), skill_index+50)]
            for indicator, score in indicators.items():
                if indicator in context:
                    return score
            
            return 0.3  # Default to basic proficiency if no indicator found
        except Exception as e:
            logger.error(f"Error calculating skill proficiency: {str(e)}")
            return 0.0

    def generate_job_recommendations(self, skills: List[Dict[str, float]], experience: str) -> List[Dict[str, str]]:
        """Generate job recommendations based on skills and experience."""
        try:
            # Define job templates with detailed requirements
            job_templates = {
                'software_engineer': {
                    'title': 'Software Engineer',
                    'description': 'Develop and maintain software applications using modern technologies.',
                    'required_skills': ['programming', 'frameworks', 'databases'],
                    'salary_range': '₹6-15 LPA',
                    'growth_path': 'Senior Software Engineer → Technical Lead → Engineering Manager'
                },
                'data_scientist': {
                    'title': 'Data Scientist',
                    'description': 'Analyze complex data sets and develop machine learning models.',
                    'required_skills': ['python', 'machine learning', 'data analysis'],
                    'salary_range': '₹8-20 LPA',
                    'growth_path': 'Senior Data Scientist → Data Science Lead → Chief Data Scientist'
                },
                'devops_engineer': {
                    'title': 'DevOps Engineer',
                    'description': 'Manage and optimize cloud infrastructure and deployment pipelines.',
                    'required_skills': ['cloud', 'tools', 'programming'],
                    'salary_range': '₹7-18 LPA',
                    'growth_path': 'Senior DevOps Engineer → DevOps Lead → Cloud Architect'
                },
                'full_stack_developer': {
                    'title': 'Full Stack Developer',
                    'description': 'Develop end-to-end web applications using modern frameworks.',
                    'required_skills': ['programming', 'frameworks', 'web'],
                    'salary_range': '₹5-12 LPA',
                    'growth_path': 'Senior Full Stack Developer → Technical Lead → Solution Architect'
                },
                'mobile_developer': {
                    'title': 'Mobile Developer',
                    'description': 'Develop mobile applications for iOS and Android platforms.',
                    'required_skills': ['mobile', 'programming', 'frameworks'],
                    'salary_range': '₹6-15 LPA',
                    'growth_path': 'Senior Mobile Developer → Mobile Lead → Mobile Architect'
                }
            }
            
            # Calculate job matches
            recommendations = []
            for job_id, template in job_templates.items():
                match_score = self._calculate_job_match(skills, template['required_skills'])
                if match_score > 0.5:  # Only recommend jobs with >50% match
                    recommendations.append({
                        'title': template['title'],
                        'description': template['description'],
                        'match_score': match_score,
                        'salary_range': template['salary_range'],
                        'growth_path': template['growth_path'],
                        'explanation': self._generate_match_explanation(skills, template['required_skills'])
                    })
            
            # Sort by match score
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            return recommendations[:3]  # Return top 3 recommendations
        except Exception as e:
            logger.error(f"Error generating job recommendations: {str(e)}")
            return []

    def _calculate_job_match(self, skills: List[Dict[str, float]], required_skills: List[str]) -> float:
        """Calculate match score between candidate skills and job requirements."""
        try:
            if not skills or not required_skills:
                return 0.0
                
            # Convert skills to set for easier matching
            candidate_skills = {skill['name'] for skill in skills}
            required_skills_set = set(required_skills)
            
            # Calculate match score
            matching_skills = candidate_skills.intersection(required_skills_set)
            return len(matching_skills) / len(required_skills_set)
        except Exception as e:
            logger.error(f"Error calculating job match: {str(e)}")
            return 0.0

    def _generate_match_explanation(self, skills: List[Dict[str, float]], required_skills: List[str]) -> str:
        """Generate explanation for why the candidate matches the job requirements."""
        try:
            matching_skills = [skill for skill in skills if skill['name'] in required_skills]
            if not matching_skills:
                return "Candidate's skills do not match the job requirements."
                
            explanation = "Candidate is well-suited for this role because they have:"
            for skill in matching_skills:
                proficiency = "high" if skill['proficiency'] > 0.7 else "good" if skill['proficiency'] > 0.4 else "basic"
                explanation += f"\n- {proficiency} proficiency in {skill['name']}"
            
            return explanation
        except Exception as e:
            logger.error(f"Error generating match explanation: {str(e)}")
            return "Unable to generate match explanation."

    def generate_resume_improvements(self, text: str, skills: List[Dict[str, float]]) -> List[str]:
        """Generate suggestions for resume improvement."""
        try:
            improvements = []
            
            # Check for ATS optimization
            if not any(keyword in text.lower() for keyword in ['experience', 'skills', 'education']):
                improvements.append("Add clear section headers (Experience, Skills, Education) to improve ATS compatibility.")
            
            # Check for keyword optimization
            common_keywords = ['achieved', 'developed', 'led', 'managed', 'improved', 'increased', 'reduced', 'optimized']
            if not any(keyword in text.lower() for keyword in common_keywords):
                improvements.append("Use action verbs (achieved, developed, led) to describe your accomplishments.")
            
            # Check for skills presentation
            if len(skills) < 5:
                improvements.append("Add more specific technical skills to highlight your expertise.")
            
            # Check for metrics
            if not any(char.isdigit() for char in text):
                improvements.append("Include quantifiable achievements (e.g., 'increased efficiency by 25%').")
            
            # Check for education details
            if not re.search(r'(Bachelor|Master|PhD|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?S|M\.?S)', text):
                improvements.append("Clearly specify your educational qualifications with degrees and institutions.")
            
            # Check for experience details
            if not re.search(r'\d{4}[-–]\d{4}|\d{4}[-–]present', text):
                improvements.append("Include dates for your work experience to show career progression.")
            
            return improvements
        except Exception as e:
            logger.error(f"Error generating resume improvements: {str(e)}")
            return []

    def analyze_resume(self, text: str) -> Dict:
        """Perform comprehensive resume analysis."""
        try:
            # Extract entities
            entities = self.extract_entities(text)
            
            # Extract education information
            education = self.extract_education(text)
            
            # Extract experience information
            experience = self.extract_experience(text)
            
            # Analyze skills
            skills = self.analyze_skills(text)
            
            # Generate job recommendations
            recommendations = self.generate_job_recommendations(skills, text)
            
            # Generate resume improvements
            improvements = self.generate_resume_improvements(text, skills)
            
            return {
                'entities': entities,
                'education': education,
                'experience': experience,
                'skills': skills,
                'job_recommendations': recommendations,
                'resume_improvements': improvements
            }
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            return {
                'error': str(e),
                'entities': {},
                'education': [],
                'experience': [],
                'skills': [],
                'job_recommendations': [],
                'resume_improvements': []
            } 