"""
Knowledge Base for Exam Explainer Bot
Manages academic regulations and provides context for the AI
Supports both JSON knowledge base and PDF document uploads
"""

import json
import os
from typing import Optional, List, Dict
from pathlib import Path

# Default knowledge base path - rag.json in project root
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "rag.json"


class KnowledgeBase:
    """
    Manages academic regulations knowledge base
    Provides context injection for Gemini prompts
    """
    
    def __init__(self, knowledge_path: Optional[str] = None):
        """
        Initialize the knowledge base
        
        Args:
            knowledge_path: Path to JSON knowledge base file
        """
        self.knowledge_path = Path(knowledge_path) if knowledge_path else KNOWLEDGE_BASE_PATH
        self.documents = []  # List of document chunks from rag.json
        self.regulations = {}  # Legacy format for backward compatibility
        self.custom_documents = []
        
        # Load knowledge base if exists
        self.load_knowledge_base()
    
    def load_knowledge_base(self) -> bool:
        """
        Load knowledge base from JSON file (supports rag.json array format)
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.knowledge_path.exists():
                with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle array format (rag.json style)
                if isinstance(data, list):
                    self.documents = data
                    print(f"✅ Loaded {len(self.documents)} document chunks from rag.json")
                    return True
                # Handle legacy dict format
                elif isinstance(data, dict):
                    self.regulations = data
                    return True
            else:
                # Use default regulations
                self.regulations = self._get_default_regulations()
                return True
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self.regulations = self._get_default_regulations()
            return False
    
    def _get_default_regulations(self) -> Dict:
        """
        Get default generic academic regulations
        
        Returns:
            Dictionary of default regulations
        """
        return {
            "grading_system": {
                "title": "Grading System",
                "content": """
## Grading System Overview

### CGPA (Cumulative Grade Point Average)
- Grade Points range from 0 to 10
- CGPA = Sum of (Grade Point × Credits) / Total Credits
- Minimum passing CGPA is typically 4.0 or 5.0

### Letter Grade to Grade Point Conversion:
| Letter Grade | Grade Points | Percentage Range |
|--------------|--------------|------------------|
| O (Outstanding) | 10 | 90-100% |
| A+ (Excellent) | 9 | 80-89% |
| A (Very Good) | 8 | 70-79% |
| B+ (Good) | 7 | 60-69% |
| B (Above Average) | 6 | 55-59% |
| C (Average) | 5 | 50-54% |
| P (Pass) | 4 | 40-49% |
| F (Fail) | 0 | Below 40% |

### Percentage from CGPA:
Approximate Percentage = (CGPA - 0.5) × 10
Example: CGPA 8.5 ≈ 80%
                """
            },
            "internal_external_evaluation": {
                "title": "Internal and External Evaluation",
                "content": """
## Internal vs External Evaluation

### Internal Evaluation (Continuous Assessment)
- **Weight**: Typically 30-40% of total marks
- **Components**:
  - Mid-semester examinations
  - Assignments and homework
  - Class participation and attendance
  - Lab work and practicals
  - Mini projects and presentations
  - Quizzes and class tests

### External Evaluation (End Semester)
- **Weight**: Typically 60-70% of total marks
- **Components**:
  - End semester written examination
  - Practical/Lab examination
  - Viva voce (oral examination)
  - Project evaluation by external examiner

### Key Points:
- Internal marks are awarded by course faculty
- External exams are conducted by the university/institution
- Both components must be passed separately in most cases
- Minimum passing marks: usually 40% in each component
                """
            },
            "revaluation_process": {
                "title": "Revaluation Process",
                "content": """
## Revaluation/Re-evaluation Process

### What is Revaluation?
Revaluation is the process of getting your answer sheet re-assessed by a different evaluator if you believe there was an error in marking.

### Steps to Apply for Revaluation:
1. **Check Results**: Review your marks once results are declared
2. **Apply Online/Offline**: Submit revaluation application within deadline
3. **Pay Fee**: Pay the revaluation fee (varies by institution)
4. **Processing**: Answer sheet is evaluated by a new examiner
5. **Result**: Revised marks are published (can increase, decrease, or stay same)

### Important Points:
- **Deadline**: Usually 10-15 days from result declaration
- **Fee**: Typically ₹500-2000 per subject
- **Outcome**: Marks may increase, decrease, or remain unchanged
- **Time**: Results usually within 30-45 days
- **No Re-revaluation**: Generally, revaluation decision is final

### Photocopy Option:
Many institutions allow students to get photocopy of answer sheets before applying for revaluation.
                """
            },
            "supplementary_exam": {
                "title": "Supplementary Examination",
                "content": """
## Supplementary Examinations

### What is a Supplementary Exam?
A supplementary exam is an additional opportunity given to students who failed in regular examinations or could not appear due to valid reasons.

### Eligibility:
- Students who failed in one or more subjects
- Students with medical issues during regular exams
- Students with backlogs from previous semesters

### Key Features:
- **Timing**: Usually conducted 1-2 months after regular exams
- **Fee**: Additional fee required (typically ₹1000-3000 per subject)
- **Marking**: Same pattern as regular examination
- **Maximum Marks**: Can score full marks (no cap in most institutions)
- **Grade Display**: Some institutions mark 'S' for supplementary pass

### Tips for Supplementary Exams:
- Focus on failed subjects only
- Use the extra time for thorough preparation
- Attend any special classes offered
- Clear doubts with faculty before exam
                """
            },
            "exam_rules": {
                "title": "Examination Rules and Conduct",
                "content": """
## Examination Rules

### Before Examination:
- Carry valid ID card and hall ticket
- Arrive 30 minutes before exam time
- Keep only permitted materials on desk
- Electronic devices are strictly prohibited

### During Examination:
- Read all instructions carefully
- Write roll number on every sheet
- Use only blue/black ink pen
- Additional sheets must be tagged properly
- Raise hand for clarifications (no talking)

### Prohibited Actions (Malpractice):
- Copying from others
- Using unauthorized materials
- Communicating with other students
- Possession of electronic devices
- Writing on question paper (if not allowed)

### Consequences of Malpractice:
- Cancellation of current exam
- Suspension from future exams
- Academic penalty (varies by institution)
- May affect degree completion

### After Examination:
- Submit answer sheet before leaving
- Do not take question paper if not permitted
- Clear the hall promptly
                """
            },
            "attendance_requirements": {
                "title": "Attendance Requirements",
                "content": """
## Attendance Requirements

### Minimum Attendance:
- **Theory Classes**: Minimum 75% attendance required
- **Practical/Lab**: Minimum 80% attendance typically required
- **Shortfall**: May lead to exam debarment

### Attendance Calculation:
Attendance % = (Classes Attended / Total Classes) × 100

### Condonation:
- Students with 65-74% may apply for condonation
- Medical certificates required for genuine cases
- Condonation fee applicable
- Maximum 2-3 condonations allowed during degree

### Consequences of Low Attendance:
- Below 65%: Detained/Not promoted
- 65-74%: Condonation required
- 75% and above: Eligible for exams

### Medical Leave:
- Inform within 3 days of absence
- Submit medical certificate
- Can be adjusted in attendance calculation
                """
            }
        }
    
    def get_context_for_query(self, query: str) -> str:
        """
        Get relevant knowledge base context for a user query
        
        Args:
            query: User's question
            
        Returns:
            Relevant context string
        """
        query_lower = query.lower()
        relevant_sections = []
        
        # If we have rag.json documents (array format)
        if self.documents:
            # Category to keywords mapping for rag.json
            category_keywords = {
                "grading": ["grade", "grading", "cgpa", "gpa", "marks", "percentage", "point", "score", "10-point"],
                "attendance": ["attendance", "detained", "condonation", "absent", "leave", "75%", "65%"],
                "evaluation": ["internal", "external", "evaluation", "assessment", "continuous", "semester", "cie", "see"],
                "revaluation": ["revaluation", "re-evaluation", "recheck", "recorrection", "third valuation"],
                "credits": ["credit", "credits", "160", "workload"],
                "internship": ["internship", "summer", "project", "industry"],
                "moocs": ["mooc", "online course", "nptel", "swayam"],
                "malpractice": ["malpractice", "cheating", "copying", "prohibited", "misconduct"],
                "promotion": ["promotion", "promoted", "higher semester"],
                "pass_criteria": ["pass", "passing", "minimum", "35%", "40%"],
                "general": ["college", "srkr", "autonomous", "regulation", "r23", "programme", "duration"]
            }
            
            # Find matching documents
            matched_docs = []
            for doc in self.documents:
                doc_content = doc.get("content", "").lower()
                doc_category = doc.get("metadata", {}).get("category", "").lower()
                
                # Check if query matches document content or category keywords
                content_match = any(word in doc_content for word in query_lower.split() if len(word) > 2)
                category_match = False
                
                for category, keywords in category_keywords.items():
                    if any(kw in query_lower for kw in keywords):
                        if category in doc_category or any(kw in doc_content for kw in keywords):
                            category_match = True
                            break
                
                if content_match or category_match:
                    matched_docs.append(doc)
            
            # If no matches, include top 5 most relevant general docs
            if not matched_docs:
                matched_docs = self.documents[:5]
            
            # Format matched documents
            for doc in matched_docs[:7]:  # Limit to 7 most relevant
                content = doc.get("content", "")
                source = doc.get("metadata", {}).get("source", "Knowledge Base")
                relevant_sections.append(f"• {content}")
            
            if relevant_sections:
                return "**SRKR Engineering College R23 Regulations:**\n\n" + "\n\n".join(relevant_sections)
        
        # Fallback to legacy dict format
        keywords_map = {
            "grading_system": ["grade", "cgpa", "gpa", "marks", "percentage", "point", "score"],
            "internal_external_evaluation": ["internal", "external", "evaluation", "assessment", "continuous", "semester"],
            "revaluation_process": ["revaluation", "re-evaluation", "recheck", "photocopy", "recorrection"],
            "supplementary_exam": ["supplementary", "supply", "backlog", "failed", "arrear", "repeat"],
            "exam_rules": ["rules", "conduct", "malpractice", "cheating", "prohibited", "hall ticket"],
            "attendance_requirements": ["attendance", "detained", "condonation", "absent", "leave"]
        }
        
        for section_key, keywords in keywords_map.items():
            if any(keyword in query_lower for keyword in keywords):
                if section_key in self.regulations:
                    section = self.regulations[section_key]
                    relevant_sections.append(f"### {section['title']}\n{section['content']}")
        
        if not relevant_sections:
            for section_key, section in self.regulations.items():
                relevant_sections.append(f"### {section['title']}\n{section['content']}")
        
        if self.custom_documents:
            relevant_sections.append("\n### Custom Regulations:\n" + "\n".join(self.custom_documents))
        
        return "\n\n".join(relevant_sections)
    
    def add_custom_document(self, content: str) -> None:
        """
        Add custom document content to knowledge base
        
        Args:
            content: Document text content
        """
        self.custom_documents.append(content)
    
    def clear_custom_documents(self) -> None:
        """Clear all custom documents"""
        self.custom_documents = []
    
    def save_knowledge_base(self) -> bool:
        """
        Save current regulations to JSON file
        
        Returns:
            True if saved successfully
        """
        try:
            # Ensure data directory exists
            self.knowledge_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.knowledge_path, 'w', encoding='utf-8') as f:
                json.dump(self.regulations, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False
    
    def get_all_topics(self) -> List[str]:
        """
        Get list of all available topics
        
        Returns:
            List of topic titles
        """
        return [section['title'] for section in self.regulations.values()]


# Create data directory and save default knowledge base
def initialize_knowledge_base():
    """Initialize the knowledge base with default regulations"""
    kb = KnowledgeBase()
    kb.save_knowledge_base()
    print("✅ Knowledge base initialized")
    return kb


if __name__ == "__main__":
    # Initialize and test
    kb = initialize_knowledge_base()
    print(f"Available topics: {kb.get_all_topics()}")
