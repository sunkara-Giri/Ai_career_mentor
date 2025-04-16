import json
import sys
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def load_model():
    """Load the AI model and tokenizer."""
    try:
        # Using a more reliable model for text analysis
        model_name = "microsoft/phi-2"  # Smaller, faster model
        logger.info(f"Loading model: {model_name}")
        
        # Get Hugging Face token
        hf_token = os.getenv('HUGGINGFACE_API_KEY')
        if not hf_token:
            raise ValueError("Hugging Face API key not found in environment variables")
        
        # Load model with authentication
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=hf_token,
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=hf_token,
            torch_dtype=torch.float32,
            device_map="auto",
            trust_remote_code=True
        )
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def analyze_resume(text):
    """Analyze resume text using the AI model."""
    try:
        model, tokenizer = load_model()
        
        # Prepare the prompt
        prompt = f"""Analyze the following resume text and provide a structured analysis:
        
        Resume Text:
        {text}
        
        Provide a JSON response with the following structure:
        {{
            "technical_skills": ["skill1", "skill2", ...],
            "soft_skills": ["skill1", "skill2", ...],
            "years_of_experience": number,
            "education": [
                {{
                    "degree": "string",
                    "institution": "string",
                    "year": number
                }}
            ],
            "project_highlights": ["project1", "project2", ...],
            "formatting_suggestions": ["suggestion1", "suggestion2", ...],
            "recommended_job_roles": ["role1", "role2", ...]
        }}
        """
        
        # Generate response
        inputs = tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = model.generate(
            inputs.input_ids,
            max_length=2048,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response
        try:
            # Find the JSON part in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            # Parse and validate JSON
            analysis = json.loads(json_str)
            
            # Ensure all required fields are present
            required_fields = [
                "technical_skills", "soft_skills", "years_of_experience",
                "education", "project_highlights", "formatting_suggestions",
                "recommended_job_roles"
            ]
            
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = []
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return {
                "error": "Failed to parse AI response",
                "technical_skills": [],
                "soft_skills": [],
                "years_of_experience": 0,
                "education": [],
                "project_highlights": [],
                "formatting_suggestions": [],
                "recommended_job_roles": []
            }
            
    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        return {
            "error": str(e),
            "technical_skills": [],
            "soft_skills": [],
            "years_of_experience": 0,
            "education": [],
            "project_highlights": [],
            "formatting_suggestions": [],
            "recommended_job_roles": []
        }

def get_job_recommendations(skills, experience):
    """Generate job recommendations based on skills and experience."""
    try:
        model, tokenizer = load_model()
        
        # Prepare the prompt
        prompt = f"""Based on the following skills and experience, recommend suitable job roles:
        
        Skills: {', '.join(skills)}
        Years of Experience: {experience}
        
        Provide a JSON response with the following structure:
        {{
            "recommendations": [
                {{
                    "title": "string",
                    "company": "string",
                    "match_score": number,
                    "required_skills": ["skill1", "skill2", ...],
                    "location": "string",
                    "salary_range": "string"
                }}
            ]
        }}
        """
        
        # Generate response
        inputs = tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True)
        outputs = model.generate(
            inputs.input_ids,
            max_length=2048,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            recommendations = json.loads(json_str)
            return recommendations.get("recommendations", [])
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing job recommendations JSON: {str(e)}")
            return []
            
    except Exception as e:
        logger.error(f"Error in get_job_recommendations: {str(e)}")
        return []

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"error": "No text provided"}))
            sys.exit(1)
            
        resume_text = sys.argv[1]
        
        # Analyze resume
        analysis = analyze_resume(resume_text)
        
        # Get job recommendations
        if "error" not in analysis:
            skills = analysis["technical_skills"] + analysis["soft_skills"]
            experience = analysis["years_of_experience"]
            recommendations = get_job_recommendations(skills, experience)
            analysis["job_recommendations"] = recommendations
        
        print(json.dumps(analysis))
        
    except Exception as e:
        print(json.dumps({"error": str(e)})) 