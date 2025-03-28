from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import sys

class AIAnalyzer:
    def __init__(self):
        print("Initializing AI Analyzer...")
        self.tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3-0324", trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-V3-0324", trust_remote_code=True)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"Model loaded on {self.device}")

    def analyze_resume(self, resume_text):
        print("Analyzing resume...")
        # Prepare the prompt for resume analysis
        prompt = f"""Analyze the following resume and provide a detailed analysis in JSON format:
        {resume_text}
        
        Please provide analysis in the following format:
        {{
            "technical_skills": ["skill1", "skill2", ...],
            "soft_skills": ["skill1", "skill2", ...],
            "years_of_experience": number,
            "education": {{
                "degree": "string",
                "field": "string",
                "institution": "string"
            }},
            "project_highlights": ["highlight1", "highlight2", ...],
            "formatting_suggestions": ["suggestion1", "suggestion2", ...],
            "recommended_job_roles": ["role1", "role2", ...]
        }}"""

        # Generate analysis
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_length=1000,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        # Decode and parse the response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Analysis completed")
        
        # Extract the JSON part from the response
        try:
            # Find the first '{' and last '}'
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            analysis = json.loads(json_str)
            return analysis
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            # Fallback to a basic analysis if JSON parsing fails
            return {
                "technical_skills": [],
                "soft_skills": [],
                "years_of_experience": 0,
                "education": {
                    "degree": "Not specified",
                    "field": "Not specified",
                    "institution": "Not specified"
                },
                "project_highlights": [],
                "formatting_suggestions": ["Unable to analyze formatting"],
                "recommended_job_roles": []
            }

    def get_job_recommendations(self, skills, experience):
        # Prepare the prompt for job recommendations
        prompt = f"""Based on the following skills and experience, recommend suitable job roles:
        Skills: {', '.join(skills)}
        Years of Experience: {experience}
        
        Please provide recommendations in the following format:
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
        }}"""

        # Generate recommendations
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_length=1000,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        # Decode and parse the response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        try:
            # Find the first '{' and last '}'
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            recommendations = json.loads(json_str)
            return recommendations.get("recommendations", [])
        except json.JSONDecodeError:
            return []

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Please provide resume text"}))
        sys.exit(1)

    try:
        # Get resume text from command line argument
        resume_text = sys.argv[1]
        
        # Initialize analyzer and analyze resume
        analyzer = AIAnalyzer()
        analysis = analyzer.analyze_resume(resume_text)
        
        # Print the analysis as JSON
        print(json.dumps(analysis))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main() 