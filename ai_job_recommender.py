import json
import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
from dotenv import load_dotenv
import requests
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class JobRecommender:
    def __init__(self):
        self.hf_token = os.getenv('HUGGINGFACE_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        
        # Using more specialized models for better analysis
        self.models = {
            'skills': "microsoft/phi-2",
            'experience': "microsoft/phi-2",
            'recommendations': "microsoft/phi-2"
        }
        self.tokenizers = {}
        self.models_loaded = {}
        
        # Initialize models
        self.load_models()

    def load_models(self):
        """Load all required models."""
        try:
            for name, model_name in self.models.items():
                logger.info(f"Loading {name} model: {model_name}")
                self.tokenizers[name] = AutoTokenizer.from_pretrained(
                    model_name,
                    token=self.hf_token,
                    trust_remote_code=True
                )
                self.models_loaded[name] = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    token=self.hf_token,
                    torch_dtype=torch.float32,
                    device_map="auto",
                    trust_remote_code=True
                )
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise

    def analyze_skills(self, resume_text: str) -> List[str]:
        """Analyze and extract skills from resume text."""
        try:
            prompt = f"""Extract technical and soft skills from the following resume text. Focus on:
            1. Programming languages
            2. Frameworks and tools
            3. Soft skills
            4. Domain knowledge
            
            Resume Text:
            {resume_text}
            
            Provide a JSON array of skills in the following format:
            ["skill1", "skill2", ...]
            """
            
            inputs = self.tokenizers['skills'](prompt, return_tensors="pt", max_length=2048, truncation=True)
            outputs = self.models_loaded['skills'].generate(
                inputs.input_ids,
                max_length=2048,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            response = self.tokenizers['skills'].decode(outputs[0], skip_special_tokens=True)
            skills = json.loads(response[response.find('['):response.rfind(']')+1])
            return skills
        except Exception as e:
            logger.error(f"Error analyzing skills: {str(e)}")
            return []

    def analyze_experience(self, resume_text: str) -> Dict[str, Any]:
        """Analyze work experience from resume text."""
        try:
            prompt = f"""Extract work experience details from the following resume text. Focus on:
            1. Total years of experience
            2. Industries worked in
            3. Previous roles and responsibilities
            4. Notable achievements
            
            Resume Text:
            {resume_text}
            
            Provide a JSON object with the following structure:
            {{
                "years_of_experience": number,
                "industries": ["industry1", "industry2", ...],
                "roles": ["role1", "role2", ...],
                "achievements": ["achievement1", "achievement2", ...]
            }}
            """
            
            inputs = self.tokenizers['experience'](prompt, return_tensors="pt", max_length=2048, truncation=True)
            outputs = self.models_loaded['experience'].generate(
                inputs.input_ids,
                max_length=2048,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            response = self.tokenizers['experience'].decode(outputs[0], skip_special_tokens=True)
            experience = json.loads(response[response.find('{'):response.rfind('}')+1])
            return experience
        except Exception as e:
            logger.error(f"Error analyzing experience: {str(e)}")
            return {"years_of_experience": 0, "industries": [], "roles": [], "achievements": []}

    def get_job_recommendations(self, skills: List[str], experience: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate job recommendations based on skills and experience."""
        try:
            # Prepare the prompt with detailed context
            prompt = f"""Based on the following profile, recommend suitable job roles. Consider:
            1. Current skills and experience
            2. Industry trends
            3. Career growth potential
            4. Salary expectations
            
            Profile:
            Skills: {', '.join(skills)}
            Years of Experience: {experience['years_of_experience']}
            Industries: {', '.join(experience['industries'])}
            Previous Roles: {', '.join(experience['roles'])}
            Notable Achievements: {', '.join(experience.get('achievements', []))}
            
            Provide a JSON array of job recommendations in the following format:
            [
                {{
                    "title": "string",
                    "company": "string",
                    "match_score": number,
                    "required_skills": ["skill1", "skill2", ...],
                    "location": "string",
                    "salary_range": "string",
                    "description": "string",
                    "growth_potential": "string",
                    "required_experience": "string",
                    "company_culture": "string",
                    "benefits": ["benefit1", "benefit2", ...]
                }}
            ]
            """
            
            inputs = self.tokenizers['recommendations'](prompt, return_tensors="pt", max_length=2048, truncation=True)
            outputs = self.models_loaded['recommendations'].generate(
                inputs.input_ids,
                max_length=2048,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            response = self.tokenizers['recommendations'].decode(outputs[0], skip_special_tokens=True)
            recommendations = json.loads(response[response.find('['):response.rfind(']')+1])
            
            # Filter and sort recommendations by match score
            recommendations = [r for r in recommendations if r['match_score'] > 50]
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            return recommendations[:5]  # Return top 5 recommendations
        except Exception as e:
            logger.error(f"Error generating job recommendations: {str(e)}")
            return []

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Main function to analyze resume and generate recommendations."""
        try:
            # Analyze skills
            skills = self.analyze_skills(resume_text)
            
            # Analyze experience
            experience = self.analyze_experience(resume_text)
            
            # Generate job recommendations
            recommendations = self.get_job_recommendations(skills, experience)
            
            return {
                "skills": skills,
                "experience": experience,
                "job_recommendations": recommendations,
                "analysis_timestamp": str(datetime.now())
            }
        except Exception as e:
            logger.error(f"Error in analyze_resume: {str(e)}")
            return {
                "error": str(e),
                "skills": [],
                "experience": {"years_of_experience": 0, "industries": [], "roles": [], "achievements": []},
                "job_recommendations": []
            }

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"error": "No text provided"}))
            sys.exit(1)
            
        resume_text = sys.argv[1]
        recommender = JobRecommender()
        analysis = recommender.analyze_resume(resume_text)
        print(json.dumps(analysis))
        
    except Exception as e:
        print(json.dumps({"error": str(e)})) 