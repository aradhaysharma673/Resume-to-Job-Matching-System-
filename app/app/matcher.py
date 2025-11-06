import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List
from app.models import MatchLevel, MatchResult
from app.config import settings

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

class ResumeMatcher:
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=500
        )
        
        # Common tech skills for matching
        self.common_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'express', 'django', 'flask', 'fastapi', 'sql', 'mongodb',
            'postgresql', 'mysql', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'git', 'ci/cd', 'agile', 'scrum', 'rest api', 'graphql',
            'html', 'css', 'bootstrap', 'tailwind', 'figma', 'ui/ux',
            'data structures', 'algorithms', 'system design', 'testing',
            'selenium', 'jest', 'pytest', 'linux', 'bash'
        ]
    
    def calculate_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate cosine similarity between resume and job description"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def get_match_level(self, score: float) -> MatchLevel:
        """Determine match level based on score"""
        if score >= settings.excellent_match:
            return MatchLevel.EXCELLENT
        elif score >= settings.good_match:
            return MatchLevel.GOOD
        elif score >= settings.fair_match:
            return MatchLevel.FAIR
        else:
            return MatchLevel.POOR
    
    def extract_key_phrases(self, resume_text: str, job_text: str, top_n: int = 5) -> List[str]:
        """Extract top matching phrases between resume and job"""
        try:
            # Fit vectorizer on job description
            self.vectorizer.fit([job_text])
            
            # Transform resume text
            resume_vector = self.vectorizer.transform([resume_text])
            
            # Get feature names and their scores
            feature_names = self.vectorizer.get_feature_names_out()
            resume_scores = resume_vector.toarray()[0]
            
            # Get top features
            top_indices = np.argsort(resume_scores)[-top_n:][::-1]
            top_phrases = [feature_names[i] for i in top_indices if resume_scores[i] > 0]
            
            return top_phrases
        except Exception as e:
            print(f"Key phrase extraction error: {e}")
            return []
    
    def find_matched_skills(self, resume_text: str, required_skills: List[str]) -> List[str]:
        """Find which required skills are present in resume"""
        resume_lower = resume_text.lower()
        matched = []
        
        for skill in required_skills:
            if skill.lower() in resume_lower:
                matched.append(skill)
        
        return matched
    
    def find_missing_skills(self, resume_text: str, required_skills: List[str]) -> List[str]:
        """Find which required skills are missing from resume"""
        matched = self.find_matched_skills(resume_text, required_skills)
        return [skill for skill in required_skills if skill not in matched]
    
    def generate_recommendation(self, match_level: MatchLevel, score: float) -> str:
        """Generate hiring recommendation based on match level"""
        recommendations = {
            MatchLevel.EXCELLENT: f"🌟 Strong candidate! Match score of {score:.0f}% indicates excellent alignment. Recommend for immediate interview.",
            MatchLevel.GOOD: f"✅ Good candidate. Match score of {score:.0f}% shows solid fit. Consider for interview after initial screening.",
            MatchLevel.FAIR: f"⚠️ Fair candidate. Match score of {score:.0f}% suggests potential but may need skill development. Review carefully.",
            MatchLevel.POOR: f"❌ Weak match. Score of {score:.0f}% indicates significant gaps. Consider only if other factors compensate."
        }
        return recommendations.get(match_level, "No recommendation available.")
    
    def match_resume_to_job(
        self, 
        resume_text: str, 
        job_title: str,
        job_description: str,
        required_skills: List[str]
    ) -> MatchResult:
        """
        Main matching function that returns comprehensive match analysis
        """
        # Combine job title and description for better matching
        full_job_text = f"{job_title} {job_description}"
        
        # Calculate similarity score
        similarity = self.calculate_similarity(resume_text, full_job_text)
        match_score = round(similarity * 100, 2)
        
        # Determine match level
        match_level = self.get_match_level(similarity)
        
        # Find matched and missing skills
        matched_skills = self.find_matched_skills(resume_text, required_skills)
        missing_skills = self.find_missing_skills(resume_text, required_skills)
        
        # Extract key highlights
        key_highlights = self.extract_key_phrases(resume_text, full_job_text, top_n=5)
        
        # Generate recommendation
        recommendation = self.generate_recommendation(match_level, match_score)
        
        return MatchResult(
            match_score=match_score,
            match_level=match_level,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            key_highlights=key_highlights,
            recommendation=recommendation
        )

matcher = ResumeMatcher()
