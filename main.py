import logging
from config import settings # Assuming settings are loaded from config/__init__.py
from llm_interface import OpenAILLM # Or your preferred LLM implementation
from memory import SocialMemory
from agents import ToMAgent, DomainAgent, ResponseAgent
from utils.helpers import setup_logger, parse_json_from_string

# Setup logger for the main application
logger = setup_logger("MetamindApp", level=getattr(logging, settings.get("LOG_LEVEL", "INFO").upper()))

class MetamindApplication:
    def __init__(self):
        logger.info("Initializing Metamind Application...")
        
        # 1. Initialize LLM Interface
        # Ensure OPENAI_API_KEY is set in your app_config.py or environment
        self.llm = OpenAILLM(
            api_key=settings.OPENAI_API_KEY,
            chat_model_name=settings.OPENAI_MODEL_CHAT,
            completion_model_name=settings.OPENAI_MODEL_COMPLETION
        )
        logger.info(f"LLM Interface initialized with chat model: {settings.OPENAI_MODEL_CHAT}")

        # 2. Initialize Social Memory
        self.social_memory = SocialMemory()
        logger.info("Social Memory initialized.")

        # 3. Initialize Agents
        self.tom_agent = ToMAgent(llm_interface=self.llm, social_memory=self.social_memory, config=settings)
        self.domain_agent = DomainAgent(llm_interface=self.llm, social_memory=self.social_memory, config=settings)
        self.response_agent = ResponseAgent(llm_interface=self.llm, social_memory=self.social_memory, config=settings)
        logger.info("Agents (ToM, Domain, Response) initialized.")

    def process_user_input(self, user_utterance: str, conversation_context: list[str]) -> str:
        """
        Processes a single user utterance through the Metamind pipeline.
        """
        logger.info(f"Processing user input: '{user_utterance}'")
        logger.debug(f"Current conversation context: {conversation_context}")

        # Stage 1: Theory-of-Mind (ToM) Agent
        # Generate k hypotheses about the user's mental state
        # H_t = {h_1, h_2, ..., h_k}
        hypotheses_H_t = self.tom_agent.generate_hypotheses(user_utterance, conversation_context)
        if not hypotheses_H_t:
            logger.warning("ToM Agent did not generate any hypotheses.")
            return "I'm having trouble understanding that right now. Could you try rephrasing?"
        
        logger.info(f"ToM Agent generated {len(hypotheses_H_t)} hypotheses.")
        for i, h in enumerate(hypotheses_H_t):
            logger.debug(f"  Hypothesis {i+1}: Type='{h.get('type')}', Desc='{h.get('description')}'")

        # Stage 2: Domain Agent
        # Refine hypotheses and calculate probabilities
        # ~H_t = {~h_1, ~h_2, ..., ~h_k}
        refined_hypotheses_H_tilde_t = []
        for h_i in hypotheses_H_t:
            refined_h_i = self.domain_agent.refine_hypothesis(
                hypothesis=h_i,
                user_utterance=user_utterance,
                conversation_context=conversation_context
            )
            if refined_h_i:
                refined_hypotheses_H_tilde_t.append(refined_h_i)
        
        if not refined_hypotheses_H_tilde_t:
            logger.warning("Domain Agent did not produce any refined hypotheses.")
            if hypotheses_H_t:
                 selected_hypothesis = hypotheses_H_t[0] 
                 logger.info("Falling back to original ToM hypothesis due to no refined hypotheses.")
            else:
                return "I'm still processing that. Can you tell me more?"
        else:
            logger.info(f"Domain Agent refined {len(refined_hypotheses_H_tilde_t)} hypotheses.")
            selected_hypothesis = max(refined_hypotheses_H_tilde_t, key=lambda h: h.get('P_posterior', 0.0))
            logger.info(f"Selected hypothesis (P_posterior={selected_hypothesis.get('P_posterior', 0.0):.2f}): Type='{selected_hypothesis.get('type')}', Desc='{selected_hypothesis.get('description')}'")

        # Stage 3: Response Agent
        # Generate, validate, and optimize response o_t
        final_response = self.response_agent.generate_response(
            selected_hypothesis=selected_hypothesis,
            user_utterance=user_utterance,
            conversation_context=conversation_context
        )
        
        logger.info(f"Response Agent generated: '{final_response}'")

        # Update social memory (example - could be more sophisticated)
        self.social_memory.add_interaction(user_utterance, final_response)

        return final_response

def run_interactive_session(app: MetamindApplication):
    """
    Runs a simple interactive command-line session.
    """
    logger.info("Starting interactive Metamind session. Type 'quit' to exit.")
    conversation_history = [] # Stores (user_utterance, agent_response) tuples
    current_context_strings = [] # Stores just the string form for context passing

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                logger.info("Exiting interactive session.")
                break
            
            if not user_input.strip():
                continue

            # Pass the last few turns as context (simplistic context management)
            # You might want a more sophisticated way to manage C_t
            context_to_pass = current_context_strings[-5:] # Example: last 5 utterances/responses

            agent_response = app.process_user_input(user_input, context_to_pass)
            print(f"Metamind: {agent_response}")

            # Update history
            conversation_history.append((user_input, agent_response))
            current_context_strings.append(f"User: {user_input}")
            current_context_strings.append(f"Metamind: {agent_response}")

        except KeyboardInterrupt:
            logger.info("Session interrupted by user. Exiting.")
            break
        except Exception as e:
            logger.error(f"An error occurred during the session: {e}", exc_info=True)
            print("Sorry, an unexpected error occurred. Please try again.")
            # Optionally, re-initialize parts of the app or exit

if __name__ == "__main__":
    # This basic check ensures that app_config.py (and thus API keys) is set up.
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        logger.error("OpenAI API key is not configured. Please set OPENAI_API_KEY in config/app_config.py")
        print("ERROR: OpenAI API key not configured. Please create/update 'config/app_config.py'.")
        print("A template 'config/app_config.py' should have been created if it was missing.")
        exit(1)
    
    metamind_app = MetamindApplication()
    run_interactive_session(metamind_app)