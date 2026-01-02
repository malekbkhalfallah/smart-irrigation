"""
Chatbot intelligent avec base de connaissances robuste et API Gemini
"""
import json
import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from config.settings import config

logger = logging.getLogger(__name__)

class EnhancedChatBot:
    """Chatbot avec base de connaissances étendue et intégration Gemini"""
    
    def __init__(self):
        self.knowledge_base = self._create_knowledge_base()
        self.conversation_history = {}
        self.gemini_available = self._check_gemini_availability()
        logger.info(f"✅ ChatBot initialisé - Gemini: {'✓' if self.gemini_available else '✗'}")
    
    def _check_gemini_availability(self) -> bool:
        """Vérifie si Gemini est disponible"""
        try:
            # Vérifier si la clé API est configurée
            if (not hasattr(config.api, 'OPENWEATHER_API_KEY') or 
                config.api.OPENWEATHER_API_KEY == "your_api_key_here"):
                return False
            
            # Essayer d'importer Gemini
            import google.generativeai as genai
            return True
        except ImportError:
            return False
        except Exception as e:
            logger.warning(f"⚠️ Gemini non disponible: {e}")
            return False
    
    def _create_knowledge_base(self) -> Dict[str, Any]:
        """Crée une base de connaissances robuste"""
        return {
            "greetings": {
                "patterns": ["bonjour", "salut", "hello", "coucou", "hey", "hi", "bonsoir"],
                "responses": [
                    "Bonjour ! Je suis l'assistant du système d'irrigation intelligent. Comment puis-je vous aider ?",
                    "Salut ! Prêt à vous aider avec votre système d'irrigation.",
                    "Hello ! Je suis là pour répondre à vos questions sur l'irrigation."
                ]
            },
            "farewells": {
                "patterns": ["au revoir", "bye", "à plus", "ciao", "goodbye", "à bientôt"],
                "responses": [
                    "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions.",
                    "À bientôt ! Bonne journée avec votre jardin.",
                    "Bye ! N'oubliez pas de vérifier l'humidité de vos plantes."
                ]
            },
            "thanks": {
                "patterns": ["merci", "thanks", "thank you", "je vous remercie"],
                "responses": [
                    "Je vous en prie ! C'est un plaisir de vous aider.",
                    "De rien ! N'hésitez pas si vous avez d'autres questions.",
                    "Avec plaisir ! Continuez à prendre soin de vos plantes."
                ]
            },
            
            # ========== CONNAISSANCES SPÉCIFIQUES ==========
            "irrigation_basics": {
                "questions": [
                    "comment arroser", "quand arroser", "fréquence arrosage", "combien d'eau",
                    "arrosage automatique", "techniques arrosage", "meilleur moment arroser"
                ],
                "responses": [
                    "Arrosez lorsque le sol est sec sur 2-3 cm de profondeur. Évitez l'arrosage en plein soleil.",
                    "Le meilleur moment pour arroser est tôt le matin ou en fin d'après-midi.",
                    "La fréquence dépend de la plante, de la saison et du type de sol. En général, 2-3 fois par semaine en été.",
                    "Arrosez abondamment mais lentement pour permettre à l'eau de pénétrer en profondeur.",
                    "Un système d'arrosage automatique comme le vôtre optimise l'utilisation de l'eau."
                ]
            },
            
            "plant_care": {
                "questions": [
                    "soin plantes", "entretien plantes", "plantes malades", "feuilles jaunes",
                    "plantes qui fanent", "engrais", "taille plantes", "rempotage"
                ],
                "responses": [
                    "Les feuilles jaunes peuvent indiquer un excès d'eau ou un manque de nutriments.",
                    "Pour des plantes saines: lumière adaptée, arrosage modéré et bon drainage.",
                    "L'engrais organique est recommandé toutes les 4-6 semaines pendant la croissance.",
                    "Le rempotage se fait généralement au printemps, lorsque les racines remplissent le pot.",
                    "Taillez les parties mortes pour favoriser une nouvelle croissance."
                ]
            },
            
            "system_operation": {
                "questions": [
                    "comment fonctionne le système", "capteurs", "problèmes système", "LEDs",
                    "configurer système", "redémarrer", "diagnostic", "calibration"
                ],
                "responses": [
                    "Le système utilise 4 capteurs: humidité sol, niveau eau, pluie, température/humidité.",
                    "LEDs: Rouge=erreur, Verte=humidité OK, Jaune=irrigation, Blanche=en ligne.",
                    "Pour redémarrer: arrêtez le programme et relancez python main.py.",
                    "La calibration se fait automatiquement. Vérifiez les connexions si problème.",
                    "Utilisez l'interface web ou l'app mobile pour surveiller en temps réel."
                ]
            },
            
            "troubleshooting": {
                "questions": [
                    "pompe ne marche pas", "capteur défectueux", "erreur système", "pas d'eau",
                    "système hors ligne", "données incorrectes", "connexion perdue"
                ],
                "responses": [
                    "Vérifiez: 1) Alimentation pompe 2) Relais 3) Niveau d'eau 4) Connexions GPIO.",
                    "Si un capteur est défectueux, vérifiez le câblage et redémarrez le système.",
                    "En cas d'erreur, consultez le fichier irrigation_system.log pour les détails.",
                    "Pas d'eau détecté? Remplissez le réservoir et vérifiez le capteur de niveau.",
                    "Système hors ligne? Vérifiez la connexion WiFi et redémarrez network_manager."
                ]
            },
            
            "plant_specific": {
                "tomates": [
                    "Les tomates nécessitent un arrosage régulier mais évitez l'eau sur les feuilles.",
                    "Humidité idéale: 60-80%. Arrosez profondément 2-3 fois par semaine.",
                    "Paillez le sol pour conserver l'humidité et éviter les maladies."
                ],
                "basilic": [
                    "Le basilic aime un sol constamment humide mais bien drainé.",
                    "Arrosez lorsque la surface du sol est sèche. Évitez la sécheresse.",
                    "Taillez régulièrement pour favoriser une croissance touffue."
                ],
                "cactus": [
                    "Les cactus nécessitent très peu d'eau. Laissez sécher complètement entre les arrosages.",
                    "En été: arrosez toutes les 2-3 semaines. En hiver: presque pas d'eau.",
                    "Utilisez un sol très drainant (mélange cactus)."
                ],
                "laitue": [
                    "La laitue a besoin d'un sol constamment humide mais pas détrempé.",
                    "Arrosez fréquemment par temps chaud. Le paillage aide à conserver l'humidité.",
                    "Récoltez le matin lorsque les feuilles sont fraîches."
                ]
            },
            
            "weather_impact": {
                "questions": [
                    "effet météo", "pluie et irrigation", "température arrosage", "saison arrosage",
                    "été hiver arrosage", "humidité air", "vent arrosage"
                ],
                "responses": [
                    "En cas de pluie, le système suspend automatiquement l'irrigation.",
                    "En été: arrosez plus fréquemment, tôt le matin. En hiver: réduisez la fréquence.",
                    "L'humidité élevée de l'air réduit les besoins en eau des plantes.",
                    "Par temps venteux, les plantes perdent plus d'eau par évaporation.",
                    "Le système ajuste automatiquement en fonction des conditions météo."
                ]
            },
            
            "water_conservation": {
                "questions": [
                    "économiser eau", "irrigation efficace", "goutte à goutte", "récupération eau",
                    "paillage", "plantes résistantes sécheresse"
                ],
                "responses": [
                    "Le système optimise l'eau en arrosant uniquement lorsque nécessaire.",
                    "Le paillage réduit l'évaporation de 70% et conserve l'humidité.",
                    "La récupération d'eau de pluie est excellente pour l'irrigation.",
                    "Plantes résistantes: lavande, romarin, sedum, agave.",
                    "Arrosez tôt le matin pour réduire l'évaporation."
                ]
            },
            
            "default_responses": [
                "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler votre question sur l'irrigation ou les plantes?",
                "Je suis spécialisé dans l'irrigation et le jardinage. Posez-moi une question sur ces sujets!",
                "Pour l'instant, je peux vous aider avec: soin des plantes, système d'irrigation, dépannage.",
                "Consultez le manuel du système ou essayez une question plus spécifique."
            ]
        }
    
    def ask_offline(self, question: str, user_id: str = "anonymous") -> str:
        """Répond en utilisant la base de connaissances locale"""
        try:
            question_lower = question.lower().strip()
            
            # 1. Vérifier les salutations
            for pattern in self.knowledge_base["greetings"]["patterns"]:
                if pattern in question_lower:
                    return random.choice(self.knowledge_base["greetings"]["responses"])
            
            # 2. Vérifier les au revoir
            for pattern in self.knowledge_base["farewells"]["patterns"]:
                if pattern in question_lower:
                    return random.choice(self.knowledge_base["farewells"]["responses"])
            
            # 3. Vérifier les remerciements
            for pattern in self.knowledge_base["thanks"]["patterns"]:
                if pattern in question_lower:
                    return random.choice(self.knowledge_base["thanks"]["responses"])
            
            # 4. Chercher dans les catégories spécifiques
            categories = [
                "irrigation_basics", "plant_care", "system_operation", 
                "troubleshooting", "weather_impact", "water_conservation"
            ]
            
            for category in categories:
                if category in self.knowledge_base:
                    for cat_question in self.knowledge_base[category]["questions"]:
                        if cat_question in question_lower:
                            return random.choice(self.knowledge_base[category]["responses"])
            
            # 5. Vérifier plantes spécifiques
            for plant_type, advice_list in self.knowledge_base["plant_specific"].items():
                if plant_type in question_lower:
                    return random.choice(advice_list)
            
            # 6. Réponse par défaut
            return random.choice(self.knowledge_base["default_responses"])
            
        except Exception as e:
            logger.error(f"❌ Erreur chatbot offline: {e}")
            return "Désolé, une erreur est survenue. Veuillez réessayer."
    
    def ask_online(self, question: str, user_id: str = "anonymous") -> str:
        """Répond en utilisant Gemini API si disponible"""
        if not self.gemini_available:
            return self.ask_offline(question, user_id)
        
        try:
            import google.generativeai as genai
            
            # Configurer Gemini
            genai.configure(api_key=config.api.OPENWEATHER_API_KEY)
            
            # Préparer le prompt contextuel
            context = """
            Tu es un expert en irrigation, jardinage et systèmes d'arrosage automatique.
            L'utilisateur utilise un système d'irrigation intelligent sur Raspberry Pi avec:
            - Capteurs: humidité sol, niveau eau, pluie, température/humidité
            - Pompe à eau contrôlée automatiquement
            - LEDs d'état: rouge (erreur), verte (OK), jaune (irrigation), blanche (en ligne)
            
            Donne des réponses courtes, pratiques et précises.
            Si la question n'est pas liée à l'irrigation/jardinage, explique que tu es spécialisé dans ce domaine.
            
            Question: {question}
            """
            
            # Créer le modèle
            model = genai.GenerativeModel('gemini-pro')
            
            # Générer la réponse
            response = model.generate_content(context.format(question=question))
            
            if response.text:
                # Ajouter à l'historique
                self._add_to_history(user_id, question, response.text, "online")
                return response.text
            else:
                return self.ask_offline(question, user_id)
                
        except Exception as e:
            logger.error(f"❌ Erreur Gemini: {e}")
            return self.ask_offline(question, user_id)
    
    def ask(self, question: str, user_id: str = "anonymous", force_offline: bool = False) -> str:
        """Pose une question au chatbot (choix automatique du mode)"""
        if force_offline or not self.gemini_available:
            response = self.ask_offline(question, user_id)
            mode = "offline"
        else:
            response = self.ask_online(question, user_id)
            mode = "online"
        
        # Ajouter à l'historique
        self._add_to_history(user_id, question, response, mode)
        
        return response
    
    def _add_to_history(self, user_id: str, question: str, response: str, mode: str):
        """Ajoute à l'historique des conversations"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "timestamp": time.time(),
            "question": question,
            "response": response,
            "mode": mode
        })
        
        # Garder seulement les 20 derniers messages
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Récupère l'historique des conversations"""
        if user_id in self.conversation_history:
            return self.conversation_history[user_id][-limit:]
        return []
    
    def get_available_topics(self) -> List[str]:
        """Retourne les sujets disponibles"""
        topics = [
            "Irrigation de base",
            "Soin des plantes",
            "Fonctionnement du système",
            "Dépannage",
            "Plantes spécifiques",
            "Impact météorologique",
            "Conservation d'eau"
        ]
        return topics
    
    def get_system_advice(self, sensor_data: Dict = None) -> str:
        """Donne des conseils basés sur les données des capteurs"""
        if not sensor_data:
            return "Aucune donnée de capteur disponible."
        
        advice_parts = []
        
        # Conseils basés sur l'humidité du sol
        soil_moisture = sensor_data.get("soil", {}).get("moisture_percent", 0)
        if soil_moisture < 30:
            advice_parts.append("⚠️ Le sol est très sec. L'irrigation est nécessaire.")
        elif soil_moisture < 50:
            advice_parts.append("📊 Humidité du sol faible. Surveillez les plantes.")
        elif soil_moisture > 80:
            advice_parts.append("💧 Sol très humide. Réduisez l'arrosage.")
        
        # Conseils basés sur la température
        temperature = sensor_data.get("dht22", {}).get("temperature", 0)
        if temperature > 30:
            advice_parts.append("🔥 Température élevée. Arrosez tôt le matin.")
        elif temperature < 10:
            advice_parts.append("❄️ Température basse. Réduisez la fréquence d'arrosage.")
        
        # Conseils basés sur la pluie
        if sensor_data.get("rain", {}).get("rain_detected", False):
            advice_parts.append("🌧️ Pluie détectée. L'irrigation est suspendue.")
        
        if not advice_parts:
            return "✅ Conditions optimales. Continuez le suivi régulier."
        
        return " | ".join(advice_parts)

# Instance globale
chatbot = EnhancedChatBot()