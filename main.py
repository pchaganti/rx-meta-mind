import logging
from config import LLM_CONFIG, TOM_AGENT_CONFIG, DOMAIN_AGENT_CONFIG, RESPONSE_AGENT_CONFIG, SOCIAL_MEMORY_CONFIG, MENTAL_STATE_TYPES
from llm_interface import OpenAILLM 
from memory import SocialMemory
from agents import ToMAgent, DomainAgent, ResponseAgent
from utils.helpers import setup_logger, parse_json_from_string

logger = setup_logger("MetamindApp", level=logging.INFO) 

class MetamindApplication:
    def __init__(self):
        logger.info("Initializing Metamind Application...")
        
        # 1. Initialize LLM Interface
        self.llm = OpenAILLM(LLM_CONFIG)
        logger.info(f"LLM Interface initialized with chat model: {LLM_CONFIG['model_name']}")

        # 2. Initialize Social Memory
        self.social_memory = SocialMemory(llm_interface=self.llm)
        logger.info("Social Memory initialized.")

        # 3. Initialize Agents
        self.tom_agent = ToMAgent(llm_interface=self.llm, social_memory_interface=self.social_memory, config=TOM_AGENT_CONFIG)
        self.domain_agent = DomainAgent(llm_interface=self.llm, social_memory_interface=self.social_memory, config=DOMAIN_AGENT_CONFIG)
        self.response_agent = ResponseAgent(llm_interface=self.llm, config=RESPONSE_AGENT_CONFIG)
        logger.info("Agents (ToM, Domain, Response) initialized.")

    def process_user_input(self, user_utterance: str, conversation_context: list[str]) -> str:
        """
        Processes a single user utterance through the Metamind pipeline.
        """
        logger.info(f"Processing user input: '{user_utterance}'")
        logger.debug(f"Current conversation context: {conversation_context}")

        # Stage 1: Theory-of-Mind (ToM) Agent
        # ToMAgent.process is expected to return List[Dict[str, Any]]
        hypotheses_H_t = self.tom_agent.process(user_input=user_utterance, conversation_context=conversation_context)
        
        if not hypotheses_H_t:
            logger.warning("ToM Agent did not generate any hypotheses.")
            return "I'm having trouble understanding that right now. Could you try rephrasing?"
        
        logger.info(f"ToM Agent generated {len(hypotheses_H_t)} hypotheses.")
        for i, h in enumerate(hypotheses_H_t):
            # Assuming 'explanation' field exists based on ToMAgent._parse_hypothesis_generation
            logger.debug(f"  Hypothesis {i+1}: Type='{h.get('type')}', Desc='{h.get('explanation')}'")

        # Stage 2: Domain Agent
        # DomainAgent.process is expected to take List[Dict[str, Any]] and return Dict[str, Any]
        # It should handle refinement of all hypotheses and selection internally.
        selected_hypothesis = self.domain_agent.process(
            hypotheses=hypotheses_H_t,
            user_input=user_utterance,
            conversation_context=conversation_context
        )
        
        if not selected_hypothesis or selected_hypothesis.get("type") == "Error":
            logger.warning("Domain Agent did not select a suitable hypothesis.")
            # Fallback to the first ToM hypothesis or a generic message
            if hypotheses_H_t:
                selected_hypothesis = hypotheses_H_t[0]
                logger.info("Falling back to the first ToM hypothesis.")
            else:
                return "I'm still trying to process that. Can you provide more details?"
        
        logger.info(f"Domain Agent selected hypothesis (Score={selected_hypothesis.get('score', 0.0):.2f}): Type='{selected_hypothesis.get('type')}', Desc='{selected_hypothesis.get('explanation')}'")

        # Stage 3: Response Agent
        # ResponseAgent.process expects selected_hypothesis, user_input, conversation_context, and social_memory
        # The social_memory parameter in ResponseAgent.process is Dict[str, Any]
        social_memory_data_for_response = self.social_memory.get_summary(user_id="default_user") # Example
        if not isinstance(social_memory_data_for_response, dict):
             social_memory_data_for_response = {"summary": str(social_memory_data_for_response)} # Ensure it's a dict

        response_details = self.response_agent.process(
            selected_hypothesis=selected_hypothesis,
            user_input=user_utterance,
            conversation_context=conversation_context,
            social_memory=social_memory_data_for_response 
        )
        
        final_response = response_details.get("response", "I'm not sure how to respond to that.")
        logger.info(f"Response Agent generated: '{final_response}' (Revisions: {response_details.get('revisions_done',0)})")

        # Update social memory
        self.social_memory.update_memory_from_interaction("default_user",user_utterance,final_response,conversation_context)
        
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

            context_to_pass = current_context_strings[-10:]

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

if __name__ == "__main__":
    if not LLM_CONFIG["api_key"] or LLM_CONFIG["api_key"] == "your_api_key_here":
        logger.error("OpenAI API key is not configured. Please set 'api_key' in config.py")
        print("ERROR: OpenAI API key not configured. Please update 'config.py'.")
        exit(1)
    
    metamind_app = MetamindApplication()
    run_interactive_session(metamind_app)