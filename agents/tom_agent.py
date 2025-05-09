from typing import Dict, List, Any, Optional, Tuple
from .base_agent import BaseAgent

class ToMAgent(BaseAgent):
    """
    Theory-of-Mind (ToM) Agent: Generates mental state hypotheses.
    Implements the first stage of the Metamind system.
    """
    def __init__(self, config: Dict[str, Any], llm_interface: Any, social_memory_interface: Any):
        """
        Initialize the ToM Agent.
        
        Args:
            config: Configuration for the ToM Agent.
            llm_interface: Interface to the language model.
            social_memory_interface: Interface to the social memory.
        """
        super().__init__(config, llm_interface)
        self.social_memory = social_memory_interface
        self.hypothesis_count_k = config.get("hypothesis_count_k", 7) 

    def process(self, user_input: str, conversation_context: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Generate a set of mental state hypotheses based on user input and context.
        
        Args:
            user_input: Current user utterance.
            conversation_context: Previous conversation history.
            
        Returns:
            A list of candidate mental state hypotheses.
        """
        commonsense_interpretations = self._contextual_analysis(user_input, conversation_context)
        hypotheses = []
        formatted_context = self._format_conversation_context(conversation_context)
        social_memory_summary = str(self.social_memory.get_summary(user_id="default_user"))

        for i in range(self.hypothesis_count_k):
        
            prompt = self._format_prompt(
                template=self.tom_prompts["hypothesis_generation_template"],
                u_t=user_input,
                C_t=formatted_context,
                M_t=social_memory_summary,
                T_focus=self._get_next_hypothesis_type_focus(i) # Ensure diversity
            )
            
            raw_hypothesis_data = self.llm.generate(prompt)
            parsed_hypothesis = self._parse_hypothesis_generation(raw_hypothesis_data, i)
            if parsed_hypothesis:
                hypotheses.append(parsed_hypothesis)
        
        return hypotheses

    def _contextual_analysis(self, user_input: str, conversation_context: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Perform contextual analysis to generate initial interpretations.
        (Corresponds to 'Contextual Analysis Task' in details.tex)
        """

        prompt = self._format_prompt(self.tom_prompts["contextual_analysis"], u_t=user_input, C_t=self._format_conversation_context(conversation_context))
        response = self.llm.generate(prompt)
        interpretations = self._parse_contextual_analysis_response(response)
        return interpretations

    def _get_next_hypothesis_type_focus(self, index: int) -> str:
        """
        Helper to cycle through hypothesis types for diversity.
        """
        types = ["Belief", "Desire", "Intention", "Emotion", "Thought"]
        return types[index % len(types)]

    def _parse_hypothesis_generation(self, llm_response: str, hypothesis_index: int) -> Optional[Dict[str, Any]]:
        """
        Parse the LLM response for the 'Mental State Space Planning' task.
        Expected format (from details.tex):
        - Type: [Belief/Desire/Intention/Emotion/Thought]
        - Description: Two-sentence natural language explanation
        - Evidential Basis: ...
        """
    
        try:
           
            lines = llm_response.strip().split('\n')
            hypothesis_type = "Unknown"
            description = llm_response 
            
            for line in lines:
                if line.lower().startswith("type:"):
                    hypothesis_type = line.split(":", 1)[1].strip()
                elif line.lower().startswith("description:"):
                    description = line.split(":", 1)[1].strip()
            
            return {
                "id": f"hyp_{hypothesis_index + 1}",
                "explanation": description,
                "type": hypothesis_type,
                "evidential_basis": {"linguistic_signals": "N/A", "contextual_drivers": "N/A", "memory_anchors": "N/A"} # Placeholder
            }
        except Exception as e:
            print(f"[ToMAgent] Error parsing hypothesis: {e}\nResponse: {llm_response}")
            return None