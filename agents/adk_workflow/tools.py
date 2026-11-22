from src.services.knowledge_base.models import AdvisoryContext, DiseaseRecord

# Lazy singleton pattern — agents are instantiated on first call, not at import time.
# This avoids loading the TF model multiple times when this module is imported by adk_coordinator.
_disease_agent = None
_severity_agent = None
_advisory_agent = None
_weather_agent = None
_risk_agent = None

def _get_disease_agent():
    global _disease_agent
    if _disease_agent is None:
        from agents.disease_detection_agent.disease_detection_agent import DiseaseDetectionAgent
        _disease_agent = DiseaseDetectionAgent()
    return _disease_agent

def _get_severity_agent():
    global _severity_agent
    if _severity_agent is None:
        from agents.severity_agent.severity_agent import SeverityAgent
        _severity_agent = SeverityAgent()
    return _severity_agent

def _get_advisory_agent():
    global _advisory_agent
    if _advisory_agent is None:
        from agents.advisory_agent.advisory_agent import AdvisoryAgent
        _advisory_agent = AdvisoryAgent()
    return _advisory_agent

def _get_weather_agent():
    global _weather_agent
    if _weather_agent is None:
        from agents.weather_agent.weather_agent import WeatherAgent
        _weather_agent = WeatherAgent()
    return _weather_agent

def _get_risk_agent():
    global _risk_agent
    if _risk_agent is None:
        from agents.environmental_risk_agent.environmental_risk_agent import EnvironmentalRiskAgent
        _risk_agent = EnvironmentalRiskAgent()
    return _risk_agent

def detect_disease_tool(image_path: str) -> dict:
    """
    Detects crop disease from an image.
    
    Args:
        image_path (str): The absolute path to the crop image file.
        
    Returns:
        dict: A dictionary containing 'disease', 'confidence', and 'confidence_level'.
    """
    try:
        return _get_disease_agent().predict(image_path)
    except Exception as e:
        return {"error": str(e)}

def analyze_severity_tool(image_path: str, disease_class: str, confidence: float) -> dict:
    """
    Analyzes the severity of a detected crop disease.
    
    Args:
        image_path (str): The absolute path to the crop image file.
        disease_class (str): The name of the detected disease (e.g. 'Tomato___Late_blight').
        confidence (float): The confidence percentage of the disease prediction.
        
    Returns:
        dict: A dictionary containing 'severity', 'severity_score', 'details', and 'assessment_method'.
    """
    try:
        return _get_severity_agent().analyze_severity(
            image_path=image_path,
            disease_class=disease_class,
            confidence=confidence
        )
    except Exception as e:
        return {"error": str(e)}

def generate_advice_tool(disease_data: dict, weather_data: dict, severity_data: dict, risk_data: dict, knowledge_context: dict) -> dict:
    """
    Generates agricultural advice based on disease, severity, weather, environmental risk, and knowledge context.
    
    Args:
        disease_data (dict): Prediction data.
        weather_data (dict): Current weather data.
        severity_data (dict): Severity assessment.
        risk_data (dict): Risk assessment.
        knowledge_context (dict): Disease knowledge base context.
        
    Returns:
        dict: Agricultural recommendations.
    """
    try:
        # Check if already a DiseaseRecord or needs unpacking
        k_ctx = None
        if knowledge_context:
            if isinstance(knowledge_context, DiseaseRecord):
                k_ctx = knowledge_context
            elif isinstance(knowledge_context, dict):
                k_ctx = DiseaseRecord(**knowledge_context)

        # Convert dictionary state back to Pydantic model for AdvisoryAgent
        context = AdvisoryContext(
            disease_data=disease_data,
            weather_data=weather_data,
            severity_data=severity_data,
            risk_data=risk_data,
            knowledge_context=k_ctx
        )
        return _get_advisory_agent().generate_advice(context=context)
    except Exception as e:
        return {"error": str(e)}

def get_weather_tool(location_input: str = None, lat: float = None, lon: float = None) -> dict:
    """
    Retrieves weather data based on location string OR coordinates.
    """
    try:
        return _get_weather_agent().get_weather(location_input=location_input, lat=lat, lon=lon)
    except Exception as e:
        return {"error": str(e)}

def assess_risk_tool(disease_class: str, weather_data: dict) -> dict:
    """
    Calculates environmental disease risk based on weather data.
    """
    try:
        return _get_risk_agent().assess_risk(disease_class, weather_data)
    except Exception as e:
        return {"error": str(e)}
