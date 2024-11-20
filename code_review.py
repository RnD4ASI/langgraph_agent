"""
Code Review System Example

This script implements a multi-agent code review system using LangGraph.
It creates a team of specialized agents that work together to review code:
1. Coordinator Agent: Manages the review process and synthesizes feedback
2. Style Reviewer: Focuses on code style, readability, and best practices
3. Security Reviewer: Identifies potential security vulnerabilities

Key Features:
- AST-based code analysis
- Multiple specialized reviewers
- Coordinated review process
- Comprehensive feedback synthesis
"""

import ast
from typing import Dict, List
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage

import sys
import os
# Add parent directory to path to import agent_framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_framework import create_multi_agent_workflow

# Step 1: Define code analysis tools using AST
class CodeAnalyzer(ast.NodeVisitor):
    """
    AST-based code analyzer that collects metrics and code patterns.
    
    Metrics collected:
    - Function count and complexity
    - Class count and inheritance depth
    - Variable naming patterns
    - Code structure patterns
    """
    def __init__(self):
        self.stats = {
            'functions': 0,
            'classes': 0,
            'lines': 0,
            'complexity': 0
        }
        self.current_complexity = 0
    
    def visit_FunctionDef(self, node):
        """Analyze function definitions and their complexity"""
        self.stats['functions'] += 1
        # Reset complexity counter for new function
        self.current_complexity = 1
        # Visit function body
        self.generic_visit(node)
        # Add function complexity to total
        self.stats['complexity'] += self.current_complexity
    
    def visit_ClassDef(self, node):
        """Track class definitions and analyze their structure"""
        self.stats['classes'] += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Count conditional statements for complexity"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Count loops for complexity"""
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Count loops for complexity"""
        self.current_complexity += 1
        self.generic_visit(node)

def analyze_code(code: str) -> Dict:
    """
    Analyze Python code using AST and return metrics.
    
    Process:
    1. Parse code into AST
    2. Visit nodes to collect metrics
    3. Calculate complexity scores
    4. Return comprehensive analysis
    
    Args:
        code: Python source code string
    
    Returns:
        Dictionary of code metrics and analysis
    """
    try:
        tree = ast.parse(code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return analyzer.stats
    except SyntaxError as e:
        return {'error': f"Syntax error in code: {str(e)}"}

# Step 2: Define specialized reviewer agents
@dataclass
class ReviewerAgent:
    """Base class for specialized code reviewers"""
    name: str
    role: str
    expertise: List[str]

# Step 3: Configure reviewer specifications
style_reviewer = ReviewerAgent(
    name="Style Reviewer",
    role="Code Style Expert",
    expertise=[
        "PEP 8 compliance",
        "Code readability",
        "Documentation quality",
        "Naming conventions",
        "Code organization"
    ]
)

security_reviewer = ReviewerAgent(
    name="Security Reviewer",
    role="Security Expert",
    expertise=[
        "Input validation",
        "Authentication checks",
        "Data sanitization",
        "Access control",
        "Secure coding practices"
    ]
)

coordinator = ReviewerAgent(
    name="Review Coordinator",
    role="Lead Reviewer",
    expertise=[
        "Review management",
        "Feedback synthesis",
        "Priority assessment",
        "Communication clarity"
    ]
)

# Step 4: Define system messages for each agent
def create_reviewer_message(reviewer: ReviewerAgent) -> str:
    """
    Create a specialized system message for each reviewer type.
    
    Components:
    1. Role and responsibility definition
    2. Areas of expertise
    3. Review guidelines
    4. Output format specifications
    
    Args:
        reviewer: ReviewerAgent instance with role specifications
    
    Returns:
        Formatted system message for the agent
    """
    base_message = f"""You are the {reviewer.name}, acting as {reviewer.role}.
Your expertise includes: {', '.join(reviewer.expertise)}.
"""
    
    if reviewer.name == "Review Coordinator":
        return base_message + """
Your responsibilities:
1. Coordinate the review process
2. Assign specific aspects to other reviewers
3. Synthesize feedback into actionable items
4. Prioritize issues and recommendations
5. Ensure comprehensive coverage of the code

Provide clear, actionable summaries that:
- Highlight critical issues
- Group related feedback
- Prioritize improvements
- Include specific examples
"""
    elif reviewer.name == "Style Reviewer":
        return base_message + """
Focus on code quality aspects:
1. Check PEP 8 compliance
2. Evaluate naming conventions
3. Assess code organization
4. Review documentation quality
5. Suggest readability improvements

Provide feedback that:
- References specific code sections
- Suggests concrete improvements
- Includes best practice examples
- Considers maintainability
"""
    else:  # Security Reviewer
        return base_message + """
Analyze security concerns:
1. Identify potential vulnerabilities
2. Check input validation
3. Review error handling
4. Assess data protection
5. Evaluate access controls

Provide security recommendations that:
- Highlight risk levels
- Suggest specific fixes
- Include secure alternatives
- Consider edge cases
"""

# Step 5: Create the multi-agent workflow
def create_review_workflow(code: str):
    """
    Set up the code review workflow with multiple agents.
    
    Process:
    1. Initialize all reviewer agents
    2. Configure communication patterns
    3. Set up review stages
    4. Define feedback synthesis
    
    Args:
        code: Source code to review
    
    Returns:
        Configured workflow ready for execution
    """
    # Analyze code first
    metrics = analyze_code(code)
    
    # Create the multi-agent workflow
    workflow = create_multi_agent_workflow(
        agents=[
            (coordinator.name, create_reviewer_message(coordinator)),
            (style_reviewer.name, create_reviewer_message(style_reviewer)),
            (security_reviewer.name, create_reviewer_message(security_reviewer))
        ],
        model="gpt-3.5-turbo"
    )
    
    return workflow, metrics

def main():
    """
    Main function that runs the code review workflow.
    
    Process:
    1. Get code input
    2. Initialize review workflow
    3. Execute reviews
    4. Synthesize feedback
    5. Present results
    """
    # Step 6: Example code to review
    sample_code = """
def process_user_input(data):
    if data:
        result = eval(data)  # Security issue: unsafe eval
        return result
    else:
        return None

class UserManager:
    def __init__(self):
        self.users = {}
    
    def add_user(self, username, password):
        # Style issue: no input validation
        self.users[username] = password
    
    def get_user(self, username):
        return self.users.get(username)  # Security issue: direct password access
"""
    
    print("Code Review System Demo")
    print("\nAnalyzing code...")
    
    # Step 7: Create and run the workflow
    workflow, metrics = create_review_workflow(sample_code)
    
    # Initial message to start the review
    initial_message = f"""Please review this Python code and provide comprehensive feedback.
Code metrics:
- Functions: {metrics['functions']}
- Classes: {metrics['classes']}
- Complexity: {metrics['complexity']}

Code to review:
{sample_code}
"""
    
    # Step 8: Execute the review process
    result = workflow.invoke({
        "messages": [HumanMessage(content=initial_message)],
        "metadata": {
            "max_turns": 5,
            "review_type": "comprehensive"
        }
    })
    
    # Step 9: Display review results
    print("\nCode Review Summary:")
    print("-" * 80)
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            print(f"\n{message.content}\n")
            print("-" * 80)

if __name__ == "__main__":
    main()
