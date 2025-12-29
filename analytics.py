"""
Analytics Module for Exam Explainer Bot
Tracks usage statistics for StudySensei-style insights
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
import json


@dataclass
class SessionAnalytics:
    """
    Track analytics for a single user session
    """
    session_start: datetime = field(default_factory=datetime.now)
    questions_asked: int = 0
    topics_explored: List[str] = field(default_factory=list)
    languages_used: List[str] = field(default_factory=list)
    refused_queries: int = 0  # Queries that violated ethical constraints
    
    def record_question(self, topic: str, language: str) -> None:
        """Record a new question"""
        self.questions_asked += 1
        if topic and topic not in self.topics_explored:
            self.topics_explored.append(topic)
        if language and language not in self.languages_used:
            self.languages_used.append(language)
    
    def record_refusal(self) -> None:
        """Record a refused/blocked query"""
        self.refused_queries += 1
    
    def get_session_duration(self) -> float:
        """Get session duration in minutes"""
        return (datetime.now() - self.session_start).total_seconds() / 60
    
    def get_summary(self) -> Dict:
        """Get analytics summary"""
        return {
            "questions_asked": self.questions_asked,
            "topics_explored": len(self.topics_explored),
            "topics_list": self.topics_explored,
            "languages_used": self.languages_used,
            "session_duration_minutes": round(self.get_session_duration(), 2),
            "refused_queries": self.refused_queries
        }


def detect_topic(query: str) -> str:
    """
    Detect the topic of a query for analytics
    
    Args:
        query: User's question
        
    Returns:
        Detected topic name
    """
    query_lower = query.lower()
    
    topic_keywords = {
        "Grading System": ["grade", "cgpa", "gpa", "marks", "percentage", "point", "score"],
        "Internal/External Evaluation": ["internal", "external", "evaluation", "assessment", "continuous"],
        "Revaluation": ["revaluation", "re-evaluation", "recheck", "photocopy"],
        "Supplementary Exam": ["supplementary", "supply", "backlog", "failed", "arrear"],
        "Exam Rules": ["rules", "conduct", "malpractice", "cheating", "prohibited"],
        "Attendance": ["attendance", "detained", "condonation", "absent"],
        "General": []  # Default
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return topic
    
    return "General"


def is_prohibited_query(query: str) -> bool:
    """
    Check if a query is asking for prohibited content
    
    Args:
        query: User's question
        
    Returns:
        True if query is prohibited
    """
    query_lower = query.lower()
    
    prohibited_patterns = [
        "predict my grade",
        "predict my marks",
        "will i pass",
        "what will be my score",
        "solve this question",
        "answer this question",
        "give me answers",
        "solve my assignment",
        "write my assignment",
        "do my homework",
        "question paper leak",
        "give me question paper",
        "previous year answers",
    ]
    
    return any(pattern in query_lower for pattern in prohibited_patterns)
