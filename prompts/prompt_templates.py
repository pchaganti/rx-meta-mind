# Prompts for Stage 1: Theory-of-Mind (ToM) Agent
TOM_AGENT_PROMPTS = {
    "contextual_analysis": """
Contextual Analysis Task
Input:
- Analyze the user's current statement: {u_t}
- Within conversational context: {C_t}
Objective:
Generate 3-5 commonsense interpretations of the user’s unstated needs by:
1. Identifying key semantic triggers in the utterance
2. Mapping these triggers to plausible psychosocial motivations
3. Considering cultural and linguistic norms for indirect communication
Output Format:
- Interpretation 1: [Explanation] (Contextual Support: [Relevant C_t Excerpt])
- Interpretation 2: [...], etc.
""",
    "memory_integration": """
Memory Integration Task
Input:
- Proposed hypothesis: {selected_common_sense_interpretation}
- Social memory database: {M_t}
Step 1: Identify memory matching criteria
- Emotional patterns: [List relevant M_t emotion tags]
- Behavioral history: [Past interactions demonstrating similar intent]
- Preference alignment: [Stated/implied user preferences]
Step 2: Calculate hypothesis validity score (1-5)
- Consistency with historical patterns
- Absence of contradictory evidence
- Temporal relevance
Output Format:
"Hypothesis [X] shows [strong/weak] memory alignment (Score: [N]). Key corroborations: [List]."
""",
    "mental_state_typology": """
Mental State Typology Task
Processed Input:
- Utterance: {u_t}
- Top Hypothesis: {interpretation}
- Memory Correlations: {findings}
Classification Markers:
- Belief: Cognitive representations of reality
- Desire: Preferences or goal states
- Intention: Action-oriented plans
- Emotion: Affective states
- Thought: Conscious reasoning processes
Output Format:
- Primary Marker: [T] (Confidence: [%])
  Rationale: Psychological justification using Fiske’s social cognition framework
- Secondary Markers: [List]
  Interaction Effects: How the markers co-influence the hypothesis
""",
    "mental_state_space_planning": """
Mental State Space Planning
Parameters:
- Target diversity: 40% across marker types (example, can be configured)
- Hypothesis count: k = {k_count}
- Evidence threshold: Medium–High confidence (example, can be configured)
Guidelines for Generation:
1. For each identified marker type [T], generate 1–2 extra hypotheses
2. Ensure orthogonal reasoning paths across hypotheses
3. Include both surface-level interpretations and deep psychosocial explanations
User Input (u_t): {u_t}
Conversational Context (C_t): {C_t}
Social Memory (M_t): {M_t}
Output Format for Each Hypothesis (Generate {k_count} hypotheses):
- [Hypothesis #]:
  Type: [Belief/Desire/Intention/Emotion/Thought]
  Description: Two-sentence natural language explanation
  Evidential Basis:
    - Linguistic Signals: [Lexical/paralinguistic features]
    - Contextual Drivers: [C_t elements]
    - Memory Anchors: [M_t correlations]
"""
}

# Prompts for Stage 2: Domain Agent
DOMAIN_AGENT_PROMPTS = {
    "constraint_refinement": """
Domain Constraint Refinement Task
Input:
- Hypothesis: {h_i_explanation} (Type: {h_i_type}, ID: {h_i_id})
- Domain Rule Type: {domain_rule_type} (e.g., Cultural, Ethical, Role-Based)
- Constraint Specifications: {constraint_specifications}
Step 1: Constraint Identification
- Flag elements violating {domain_rule_type} norms.
- Highlight ambiguous social signals requiring disambiguation.
Step 2: Re-interpretation Protocol
- Cultural: Remap interpretations via Hofstede’s cultural–dimension framework.
- Ethical: Apply IEEE Ethically Aligned Design principles.
- Role-Based: Enforce Goffman’s facework theory on role-appropriate behaviour.
Step 3: Tone Alignment
- Appropriateness scaling (1=informal, 5=formal).
- Politeness markers from Brown & Levinson’s theory.
Output:
- Original Hypothesis ID: {h_i_id}
- Revised Hypothesis Explanation: [Socially compliant interpretation]
- Revised Hypothesis Type: [Potentially adjusted type]
- Modification Log:
  - Constrained Elements: [List]
  - Applied Transformations: [Techniques]
  - Residual Risk Assessment: [Concerns]
""",
    "conditional_probability": """
Estimate Contextual Plausibility (P_cond)
Given:
- Revised Hypothesis (~h_i): {h_tilde_i_explanation} (Type: {h_tilde_i_type})
- User Prompt (u_t): {u_t}
- Social Context (C_t): {C_t}
- Social Memory (M_t): {M_t}
Task: Assess the contextual plausibility of the revised hypothesis. Output a single probability score between 0.0 and 1.0.
Score:
""",
    "prior_probability": """
Estimate Prior Plausibility (P_prior)
Given:
- Revised Hypothesis (~h_i): {h_tilde_i_explanation} (Type: {h_tilde_i_type})
Task: Assess the general, context-independent plausibility of this type of hypothesis. Output a single probability score between 0.0 and 1.0.
Score:
"""
}

# Prompts for Stage 3: Response Agent
RESPONSE_AGENT_PROMPTS = {
    "response_synthesis": """
Response Synthesis Task
Given:
- Selected Hypothesis (~h*): {h_tilde_explanation} (Type: {h_tilde_type})
- User Input (u_t): {u_t}
- Social Memory (M_t): {M_t}
Task: Generate a natural language response that is empathetic, coherent, and aligned with the selected hypothesis and social memory.
Response:
""",
    "response_validation": """
Response Validation Task
Given:
- Generated Response (o_t): {o_t}
- Selected Hypothesis (~h*): {h_tilde_explanation} (Type: {h_tilde_type})
- User Input (u_t): {u_t}
- Conversational Context (C_t): {C_t}
- Social Memory (M_t): {M_t}
- Beta (Weight for Empathy vs. Coherence): {beta}
Task: Evaluate the response based on empathy and coherence. Provide:
1. Empathy Score (0.0-1.0): How well the response resonates with the user's inferred emotional or cognitive state.
2. Coherence Score (0.0-1.0): Consistency with conversational context and task constraints.
3. Overall Utility Score (calculated as beta * Empathy + (1-beta) * Coherence).
4. Critique: Brief textual feedback on why the response is good or how it could be improved.
Output Format:
Empathy: [score]
Coherence: [score]
Utility: [score]
Critique: [text]
""",
    "response_optimization": """
Response Optimization Task
Given:
- Original Response: {original_response}
- Critique of Original Response: {critique}
- Selected Hypothesis (~h*): {h_tilde_explanation} (Type: {h_tilde_type})
- User Input (u_t): {u_t}
- Conversational Context (C_t): {C_t}
- Social Memory (M_t): {M_t}
Task: Revise the original response based on the critique to improve its utility, empathy, and coherence.
Optimized Response:
"""
}