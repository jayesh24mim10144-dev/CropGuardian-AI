import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Try to import google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

import logging
import time
from src.utils.logger import get_logger, save_raw_payload, GEMINI_DIR, pipeline_run_id_var
from src.services.knowledge_base.models import AdvisoryContext

logger = get_logger("advisory_agent", "advisory_agent.log")

load_dotenv()

class AdvisoryAgent:
    def __init__(self):
        """
        Initializes the Advisory Agent.
        Uses google-genai to generate tailored advice based on disease and severity.
        Contains a fallback knowledge base if the API is unavailable.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if GENAI_AVAILABLE and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_advice(self, context: AdvisoryContext) -> Dict[str, Any]:
        """
        Generates agricultural advice based on the disease, severity, weather, environmental risk, and knowledge base.
        """
        try:
            disease_class = context.disease_data.get("disease", "Unknown")
            severity = context.severity_data.get("severity", "Unknown")
            weather_data = context.weather_data
            risk_data = context.risk_data
            knowledge = context.knowledge_context

            if "healthy" in disease_class.lower():
                return {
                    "disease_description": "The plant appears healthy.",
                    "symptoms": [],
                    "treatment": [],
                    "prevention": ["Maintain current watering and fertilization schedules.", "Monitor plants regularly."],
                    "fertilizer_recommendations": ["Use standard balanced fertilizer based on crop type."],
                    "weather_based_warnings": "None.",
                    "immediate_actions": "None required.",
                    "expert_consultation": "Not necessary at this time.",
                    "source": "Fallback Knowledge Base"
                }

            if not self.api_key:
                logger.warning("AdvisoryAgent: GEMINI_API_KEY not found. Using fallback knowledge base.")
                return self._get_fallback_advice(disease_class, severity, knowledge)

            # Define the desired JSON schema for structured output
            response_schema = {
                "type": "OBJECT",
                "properties": {
                    "disease_description": {"type": "STRING"},
                    "symptoms": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "treatment": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "prevention": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "fertilizer_recommendations": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "weather_based_warnings": {"type": "STRING"},
                    "immediate_actions": {"type": "STRING"},
                    "expert_consultation": {"type": "STRING"},
                    "source": {"type": "STRING"}
                },
                "required": ["disease_description", "symptoms", "treatment", "prevention", "fertilizer_recommendations", "weather_based_warnings", "immediate_actions", "expert_consultation", "source"]
            }

            weather_context = ""
            if weather_data and weather_data.get("status") != "unavailable" and "weather" in weather_data:
                w = weather_data["weather"]
                weather_context = f"\nCurrent Weather at {weather_data.get('location', 'Unknown')}: {w.get('temperature')}°C, {w.get('humidity')}% Humidity, {w.get('precipitation')}mm precipitation."
            else:
                weather_context = "\nNOTE: Real-time weather data is currently unavailable. Do not provide specific weather-based recommendations, and explicitly state in the weather_based_warnings that weather data could not be retrieved."
            
            risk_context = ""
            if risk_data and risk_data.get("status") != "skipped":
                risk_context = f"\nEnvironmental Risk: {risk_data.get('overall_risk')} (Spread Probability: {risk_data.get('spread_probability')}%)"

            kb_context = ""
            if knowledge:
                kb_context = f"\nKnowledge Base Context for {disease_class}:\n{knowledge.model_dump_json(indent=2)}"

            prompt = f"""
            You are an expert agricultural AI. 
            A farmer has uploaded an image of a plant. The system detected:
            - Disease: {disease_class}
            - Current Severity: {severity}
            {weather_context}
            {risk_context}
            {kb_context}

            Provide a concise, practical, and farmer-focused advisory report.
            Base your advice on the provided Knowledge Base Context whenever possible.
            Explain how the current weather impacts the disease (in weather_based_warnings) and what the farmer must do right now (in immediate_actions).
            Return the output in strict JSON format. Set the "source" field to "Gemini 2.5 Flash + Knowledge Base".
            """
            
            prompt_length = len(prompt)
            logger.info(f"Sending prompt to Gemini. Length: {prompt_length} chars.")
            
            response = None
            last_api_error = None
            for model_name in ['gemini-1.5-flash', 'gemini-3.8-flash']:
                try:
                    start_api = time.time()
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=response_schema
                        ),
                    )
                    api_latency_ms = int((time.time() - start_api) * 1000)
                    tokens_used = getattr(response.usage_metadata, "total_token_count", "Unknown") if hasattr(response, "usage_metadata") else "Unknown"
                    logger.info(f"Gemini API ({model_name}) Response Received. Latency: {api_latency_ms}ms. Tokens Used: {tokens_used}")
                    break
                except Exception as ex:
                    last_api_error = ex
                    logger.warning(f"Model {model_name} failed ({ex}). Retrying with next model...")
            
            if not response:
                raise last_api_error or Exception("All Gemini models failed.")
            
            # Save raw payload
            run_id = pipeline_run_id_var.get()
            if run_id and run_id != "-":
                save_raw_payload(GEMINI_DIR, f"{run_id}_raw.txt", response.text)
            
            logger.info("Successfully parsed JSON response from Gemini.")
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            fallback = self._get_fallback_advice(context.disease_data.get("disease", "Unknown"), context.severity_data.get("severity", "Unknown"), context.knowledge_context)
            fallback["_gemini_warning"] = f"Gemini API call failed ({type(e).__name__}): {e}. Advice generated from fallback knowledge base."
            return fallback

    def _get_fallback_advice(self, disease_class: str, severity: str, knowledge: Any = None) -> Dict[str, Any]:
        """
        Returns structured fallback advice if Gemini is unavailable.
        Safely extracts values from Pydantic models or dictionaries.
        """
        if knowledge:
            # Safely extract overview description
            desc = knowledge.overview.description if hasattr(knowledge, "overview") and knowledge.overview else f"Diagnosed with {disease_class}."
            
            # Safely extract symptoms as a list of strings
            symptoms_list = []
            if hasattr(knowledge, "symptoms") and knowledge.symptoms:
                for stage in ["early", "moderate", "severe"]:
                    stage_items = getattr(knowledge.symptoms, stage, None)
                    if isinstance(stage_items, list):
                        symptoms_list.extend(stage_items)
            
            # Safely extract treatments as a list of strings
            treatment_list = []
            if hasattr(knowledge, "treatment") and knowledge.treatment:
                for t_type in ["organic", "chemical", "biological", "integrated_management"]:
                    items = getattr(knowledge.treatment, t_type, None)
                    if isinstance(items, list):
                        treatment_list.extend(items)
            if not treatment_list:
                treatment_list = ["Apply recommended fungicide or bactericide according to label directions."]

            # Safely extract prevention measures as a list of strings
            prevention_list = []
            if hasattr(knowledge, "prevention") and knowledge.prevention:
                for p_type in ["farm_hygiene", "irrigation", "crop_rotation", "air_circulation"]:
                    items = getattr(knowledge.prevention, p_type, None)
                    if isinstance(items, list):
                        prevention_list.extend(items)
            if not prevention_list:
                prevention_list = ["Maintain field sanitation and crop rotation."]

            # Safely extract fertilizer/nutrient management
            fertilizer_list = []
            if hasattr(knowledge, "nutrient_management") and knowledge.nutrient_management:
                if isinstance(knowledge.nutrient_management, list):
                    fertilizer_list = knowledge.nutrient_management
                elif hasattr(knowledge.nutrient_management, "recommendations"):
                    fertilizer_list = getattr(knowledge.nutrient_management, "recommendations", [])
            if not fertilizer_list:
                fertilizer_list = ["Apply balanced N-P-K fertilizer suitable for this crop."]

            # Safely extract immediate actions as a string
            immediate_str = "Monitor crop closely."
            if hasattr(knowledge, "immediate_actions") and knowledge.immediate_actions:
                act = knowledge.immediate_actions
                actions = []
                for field in ["today", "within_24_hours", "within_one_week"]:
                    val = getattr(act, field, None)
                    if isinstance(val, list):
                        actions.extend(val)
                if actions:
                    immediate_str = "; ".join(actions)

            # Safely extract weather warning
            weather_warn = "Monitor weather conditions."
            if hasattr(knowledge, "weather_influence") and knowledge.weather_influence:
                if hasattr(knowledge.weather_influence, "high_humidity"):
                    weather_warn = f"Humidity influence: {knowledge.weather_influence.high_humidity}"

            advice = {
                "disease_description": desc,
                "symptoms": symptoms_list,
                "treatment": treatment_list,
                "prevention": prevention_list,
                "fertilizer_recommendations": fertilizer_list,
                "weather_based_warnings": weather_warn,
                "immediate_actions": immediate_str,
                "expert_consultation": "Consult a local agronomist if symptoms persist.",
                "source": "Local Knowledge Base (Fallback)"
            }
        else:
            advice = {
                "disease_description": f"A general fungal or bacterial infection commonly known as {disease_class}.",
                "symptoms": ["Leaf spotting", "Discoloration", "Wilting"],
                "treatment": ["Remove infected leaves immediately.", "Apply appropriate broad-spectrum fungicide."],
                "prevention": ["Ensure proper spacing for air circulation.", "Avoid overhead watering to keep leaves dry."],
                "fertilizer_recommendations": ["Avoid excessive nitrogen which promotes lush, susceptible growth."],
                "weather_based_warnings": "Consider adjusting watering if humidity or rain is high.",
                "immediate_actions": "Monitor crop closely.",
                "expert_consultation": "Consult a local agronomist if symptoms persist after 2 weeks.",
                "source": "Fallback Knowledge Base"
            }
        
        if severity == "High":
            if isinstance(advice.get("treatment"), list):
                advice["treatment"].append("Consider destroying heavily infected plants to protect adjacent rows.")
            advice["immediate_actions"] = "Isolate infected area immediately."
            advice["expert_consultation"] = "Consult a professional immediately due to high severity."
            
        return advice
