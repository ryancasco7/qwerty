"""
Configuration and constants for the Training Needs Analysis System
"""
import os

# Application Configuration
APP_NAME = "Training Recommender System"
APP_TAGLINE = "A Training Needs Analysis for the BEED Department Extension Program"
APP_DEPARTMENT = "Bachelor of Elementary Education Department"
APP_VERSION = "1.0.0"

# Security Configuration
PASSWORD_MIN_LENGTH = 8
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
SESSION_TIMEOUT_MINUTES = 60

# Default Admin Account
DEFAULT_ADMIN_USERNAME = "administrator"
DEFAULT_ADMIN_PASSWORD = "admin123"  # Should be changed in production

# File Paths
DATA_FILE = "clustering_results.xlsx"
USERS_FILE = "users.json"

# User Roles
ROLE_ADMIN = "admin"
ROLE_TEACHER = "teacher"

# Cluster Configuration
NUM_CLUSTERS = 3
CLUSTER_RANDOM_STATE = 42

# Data Validation
MIN_AGE = 21
MAX_AGE = 70
MIN_YEARS_EXPERIENCE = 0
MAX_YEARS_EXPERIENCE = 50
MIN_RATING = 1
MAX_RATING = 5

# Domain Names
DOMAIN_NAMES = {
    '1': 'Teaching Strategies and Pedagogies',
    '2': 'Classroom Management Techniques',
    '3': 'Teaching Literacy and Numeracy in Early Grades',
    '4': 'Differentiated Instruction and Inclusive Education',
    '5': 'Integrating ICT in the Classroom',
    '6': 'Assessment and Evaluation of Learning',
    '7': 'Child Protection and Safe Learning Environment',
    '8': 'Parent and Community Engagement in Learning',
    '9': '21st Century Skills',
    '10': 'Values Education and Character Development',
    '11': 'Remediation Teaching Strategies',
    '12': 'Mental Health and Well-Being for Educators',
    '13': 'Curriculum Development and Planning'
}

# Cluster Interpretations
CLUSTER_INTERPRETATIONS = {
    0: "**High Engagement Teachers - Active Strategy Users**: This cluster has high mean values across most features, particularly those related to instructional approaches (e.g., Inquiry-Based Learning, Project-Based Learning, Cooperative Learning, Contextualized and Local Teaching) and classroom management (e.g., Managing Disruptive Behavior, Establishing routines, Use of positive reinforcement, Time on task management, Promoting learning self-discipline). This cluster seems to represent individuals who strongly endorse or actively utilize a wide range of teaching and classroom management strategies.",
    1: "**Moderate Engagement Teachers - Neutral Stance**: This cluster has mean values around 3 for most features, indicating a more moderate or neutral stance on the various teaching and classroom management strategies. This group might represent individuals who are somewhat familiar with or occasionally use these approaches but do not strongly identify with them.",
    2: "**Low Engagement Teachers - Traditional Methods**: This cluster has low mean values across most features. This suggests that individuals in this cluster tend to rate these teaching and classroom management strategies as less important or less frequently used. This group might represent individuals who rely on more traditional methods or have less experience with the approaches listed."
}
