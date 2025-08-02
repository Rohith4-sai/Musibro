#!/usr/bin/env python3
"""
Test script to verify the music recommendation app works with Python 3.11
and without TensorFlow dependencies.
"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        print("✅ Pandas and NumPy imported successfully")
    except Exception as e:
        print(f"❌ Pandas/NumPy import failed: {e}")
        return False
    
    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.neural_network import MLPRegressor
        print("✅ Scikit-learn imported successfully")
    except Exception as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except Exception as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    # Test our custom modules
    try:
        from src.ml.models import HybridRecommendationSystem
        print("✅ ML models imported successfully")
    except Exception as e:
        print(f"❌ ML models import failed: {e}")
        return False
    
    try:
        from src.utils.config import Config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from src.ui.components import MusicPlayerComponent, FeedbackComponent
        print("✅ UI components imported successfully")
    except Exception as e:
        print(f"❌ UI components import failed: {e}")
        return False
    
    return True

def test_ml_functionality():
    """Test ML functionality without TensorFlow"""
    print("\n🧪 Testing ML functionality...")
    
    try:
        from src.ml.models import HybridRecommendationSystem
        from src.ml.debiasing import DiversityInjector
        
        # Create a simple recommendation system
        rec_system = HybridRecommendationSystem()
        print("✅ Recommendation system created successfully")
        
        # Create diversity injector
        diversity_injector = DiversityInjector()
        print("✅ Diversity injector created successfully")
        
        return True
    except Exception as e:
        print(f"❌ ML functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🎵 Music Recommendation App - Python 3.11 Compatibility Test")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    if "3.11" in sys.version:
        print("✅ Using Python 3.11 - Perfect!")
    else:
        print("⚠️  Not using Python 3.11 - may have compatibility issues")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test ML functionality
    if not test_ml_functionality():
        print("\n❌ ML functionality tests failed!")
        return False
    
    print("\n🎉 All tests passed! Your app is ready to run.")
    print("\n🚀 To start the app, run:")
    print("   python -m streamlit run app.py")
    print("\n🌐 Then open your browser to: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 