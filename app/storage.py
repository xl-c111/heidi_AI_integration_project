# app/storage.py - Simple in-memory storage for demo
from datetime import datetime
import json

# Simple in-memory storage - resets when server restarts (perfect for demo)
care_plans = {}
patient_sessions = {}
patient_notes = {}

class SimpleStorage:
    @staticmethod
    def save_care_plan(session_id, care_plan_data):
        """Save care plan for a session"""
        care_plans[session_id] = {
            'data': care_plan_data,
            'created_at': datetime.now().isoformat(),
            'session_id': session_id
        }
        return session_id

    @staticmethod
    def get_care_plan(session_id):
        """Get care plan by session ID"""
        return care_plans.get(session_id)

    @staticmethod
    def save_patient_note(session_id, note_text):
        """Save patient daily notes"""
        if session_id not in patient_notes:
            patient_notes[session_id] = []

        patient_notes[session_id].append({
            'text': note_text,
            'timestamp': datetime.now().isoformat()
        })
        return True

    @staticmethod
    def get_patient_notes(session_id):
        """Get all notes for a session"""
        return patient_notes.get(session_id, [])

    @staticmethod
    def save_session_data(session_id, patient_data):
        """Save any session-related data"""
        patient_sessions[session_id] = {
            'patient_data': patient_data,
            'last_updated': datetime.now().isoformat()
        }
        return True

    @staticmethod
    def get_session_data(session_id):
        """Get session data"""
        return patient_sessions.get(session_id)

    @staticmethod
    def get_all_sessions():
        """Get all sessions - useful for demo"""
        return list(patient_sessions.keys())

# For demo purposes - populate with sample data
def init_demo_data():
    """Initialize with sample data for demo"""
    sample_session = "demo_session_123"

    SimpleStorage.save_care_plan(sample_session, {
        'medications': [
            {'name': 'Ibuprofen 400mg', 'frequency': 'Every 6 hours', 'instructions': 'Take with food'},
            {'name': 'Amoxicillin 500mg', 'frequency': '3 times daily', 'instructions': 'Complete full course'}
        ],
        'activities': [
            {'activity': 'Short walks', 'frequency': 'Every 2 hours', 'restrictions': '5-10 minutes only'},
            {'activity': 'Deep breathing', 'frequency': '3 times daily', 'restrictions': 'None'}
        ],
        'wound_care': [
            'Change dressing daily',
            'Keep incision dry for 48 hours',
            'Watch for signs of infection'
        ],
        'warning_signs': [
            'Fever over 101°F',
            'Severe pain not controlled by medication',
            'Signs of infection at incision site'
        ]
    })

    SimpleStorage.save_patient_note(sample_session, "Day 1: Pain level manageable, took morning medication on time")
    SimpleStorage.save_patient_note(sample_session, "Day 2: Feeling better, completed short walk")

    return sample_session

# Initialize demo data on import
DEMO_SESSION_ID = init_demo_data()