# Important: ask Heleen for a ChatGPT API key! Save it as an environment variable on your system.

from openai import OpenAI
import os
import csv
import re
import logging
import uuid
from datetime import datetime, timezone, timedelta
import json 

logging.basicConfig(level=logging.INFO)

class API:
    def __init__(self):
        # Create a folder for saving CSV if it doesn't exist
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.csv_path = os.path.join(self.data_dir, "analysis_tags.csv")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"CSV will be saved to: {os.path.abspath(self.csv_path)}")

        self.session_id = str(uuid.uuid4())
        self.client = OpenAI()

        self.transcript = ""
        
        self.questionnaire_results = """
        Participant 1:
        Power Distance: 4.5 / 7
        - 5/7 → “I believe that people in higher positions should make most decisions without consulting those in lower positions.”
        - 4/7 → “Subordinates should rarely question the decisions of their superiors.”

        Uncertainty Avoidance: 6 / 7
        - 6/7 → “I feel uncomfortable in situations where the outcome is uncertain.”
        - 6/7 → “I prefer structured situations with clear rules over ambiguous ones.”

        Individualism vs Collectivism: 3.5 / 7
        - 4/7 → “I prefer to work in a team where decisions are made collectively rather than alone.”
        - 3/7 → “I see my personal goals as more important than the goals of my group.”

        Masculinity vs Femininity: 5.5 / 7
        - 6/7 → “Success and achievement are more important to me than maintaining harmony with others.”
        - 5/7 → “Caring for others and relationships is more important than personal ambition.”

        Long-Term Orientation: 5 / 7
        - 5/7 → “I focus more on long-term goals than on immediate results.”
        - 5/7 → “Traditions and past experiences strongly influence how I make decisions.”

        Indulgence vs Restraint: 3 / 7
        - 3/7 → “I believe people should freely enjoy life and satisfy their desires whenever possible.”
        - 3/7 → “People should control their desires and focus on fulfilling duties rather than pleasure.”


        Participant 2:
        Power Distance: 2.5 / 7
        - 3/7 → “I believe that people in higher positions should make most decisions without consulting those in lower positions.”
        - 2/7 → “Subordinates should rarely question the decisions of their superiors.”

        Uncertainty Avoidance: 3 / 7
        - 3/7 → “I feel uncomfortable in situations where the outcome is uncertain.”
        - 3/7 → “I prefer structured situations with clear rules over ambiguous ones.”

        Individualism vs Collectivism: 4.5 / 7
        - 4/7 → “I prefer to work in a team where decisions are made collectively rather than alone.”
        - 5/7 → “I see my personal goals as more important than the goals of my group.”

        Masculinity vs Femininity: 3 / 7
        - 3/7 → “Success and achievement are more important to me than maintaining harmony with others.”
        - 3/7 → “Caring for others and relationships is more important than personal ambition.”

        Long-Term Orientation: 4.5 / 7
        - 5/7 → “I focus more on long-term goals than on immediate results.”
        - 4/7 → “Traditions and past experiences strongly influence how I make decisions.”

        Indulgence vs Restraint: 5.5 / 7
        - 6/7 → “I believe people should freely enjoy life and satisfy their desires whenever possible.”
        - 5/7 → “People should control their desires and focus on fulfilling duties rather than pleasure.”


        Participant 3:
        Power Distance: 3 / 7
        - 3/7 → “I believe that people in higher positions should make most decisions without consulting those in lower positions.”
        - 3/7 → “Subordinates should rarely question the decisions of their superiors.”

        Uncertainty Avoidance: 5.5 / 7
        - 5/7 → “I feel uncomfortable in situations where the outcome is uncertain.”
        - 6/7 → “I prefer structured situations with clear rules over ambiguous ones.”

        Individualism vs Collectivism: 4 / 7
        - 4/7 → “I prefer to work in a team where decisions are made collectively rather than alone.”
        - 4/7 → “I see my personal goals as more important than the goals of my group.”

        Masculinity vs Femininity: 4.5 / 7
        - 4/7 → “Success and achievement are more important to me than maintaining harmony with others.”
        - 5/7 → “Caring for others and relationships is more important than personal ambition.”

        Long-Term Orientation: 6.5 / 7
        - 7/7 → “I focus more on long-term goals than on immediate results.”
        - 6/7 → “Traditions and past experiences strongly influence how I make decisions.”

        Indulgence vs Restraint: 2 / 7
        - 2/7 → “I believe people should freely enjoy life and satisfy their desires whenever possible.”
        - 2/7 → “People should control their desires and focus on fulfilling duties rather than pleasure.”
        """

        self.domain_knowledge_items = [
            {
                "id": "intersectionality_power",
                "category": "team_dynamics",
                "content": "Team communication is shaped by intersecting social identities and power structures that influence participation, interpretation, and collaboration.",
                "keywords": ["identity", "power", "role", "status", "hierarchy", "position", "gender", "culture"],
                "tags": ["power dynamics", "interpersonal structure"],
                "priority": 0.9
            },

            {
                "id": "metacommunication",
                "category": "communication",
                "content": "Metacommunication refers to shared understanding of how messages should be interpreted between team members.",
                "keywords": ["misunderstanding", "interpret", "meaning", "tone", "clarify", "context"],
                "tags": ["shared understanding", "communication clarity"],
                "priority": 1.0
            },

            {
                "id": "politeness_theory",
                "category": "communication",
                "content": "Politeness theory explains how people protect social self-image during interaction and avoid threats to face.",
                "keywords": ["rude", "respect", "tone", "offended", "soften", "direct", "polite"],
                "tags": ["face-saving", "interaction tone"],
                "priority": 0.9
            },

            {
                "id": "pragmatic_failure",
                "category": "interpretation_mechanism",
                "content": "Pragmatic failure occurs when speakers misinterpret intent due to ambiguous phrasing, missing context, or different communicative norms.",
                "keywords": ["misunderstood", "confused", "what do you mean", "I thought", "didn't mean", "unclear", "intent"],
                "detection_type": "interpretation_event",
                "count_as": "pragmatic_failure_count",
                "priority": 1.0
            },

            {
                "id": "value_misalignment",
                "category": "priority_mechanism",
                "content": "Value misalignment occurs when participants express different priorities, goals, or evaluation criteria when making decisions.",
                "keywords": ["I prefer", "should", "more important", "focus on", "priority", "instead", "rather", "better to", "we need"],
                "detection_type": "priority_conflict_event",
                "count_as": "value_misalignment_count",
                "priority": 1.0
            },

            {
                "id": "task_conflict",
                "category": "conflict",
                "content": "Task conflict involves disagreement about ideas, decisions, or approaches to the work itself.",
                "keywords": ["disagree", "idea", "suggest", "think", "option", "instead", "prefer"],
                "tags": ["cognitive conflict"],
                "priority": 1.0
            },

            {
                "id": "relationship_conflict",
                "category": "conflict",
                "content": "Relationship conflict involves interpersonal tension, irritation, or negative emotional reactions between participants.",
                "keywords": ["you", "annoying", "frustrated", "tone", "stop", "always"],
                "tags": ["emotional conflict"],
                "priority": 1.0
            },

            {
                "id": "process_conflict",
                "category": "conflict",
                "content": "Process conflict involves disagreement about roles, responsibilities, or how the work should be organized.",
                "keywords": ["who", "responsible", "step", "process", "order", "assign"],
                "tags": ["coordination"],
                "priority": 1.0
            },

            {
                "id": "constructive_controversy",
                "category": "resolution",
                "content": "Constructive controversy involves openly comparing different viewpoints to improve understanding and decision-making.",
                "keywords": ["disagree", "compare", "argue", "viewpoint", "different"],
                "tags": ["structured disagreement"],
                "priority": 1.0
            },

            {
                "id": "interest_analysis",
                "category": "resolution",
                "content": "Interest analysis focuses on identifying underlying needs and negotiating compromises between conflicting priorities.",
                "keywords": ["need", "priority", "balance", "compromise", "adjust"],
                "tags": ["negotiation"],
                "priority": 1.0
            },

            {
                "id": "reflexivity",
                "category": "resolution",
                "content": "Reflexivity involves reflecting on assumptions, interpretations, and misunderstandings in communication.",
                "keywords": ["maybe", "think", "misunderstanding", "clarify", "assume"],
                "tags": ["meta communication"],
                "priority": 1.0
            }
        ]

        self.domain_knowledge_full = """
        - Team communication is influenced by intercultural differences, intersectionality, and power dynamics.
            - Intersectionality examines how overlapping social identities (e.g., gender, race, profession) intersect with power structures to shape individual experiences and relationships. In diverse teams, these intersections influence communication, conflict, and collaboration. Differences should be viewed as fluid and interconnected rather than fixed categories. Power operates at societal, individual, and interpersonal levels, shaping how team members perceive and interact with one another through stereotypes, expectations, and structural differences (e.g., nationality, education, role). Integrating an intersectional perspective helps capture the complexity of team dynamics, ensuring that communication, leadership, and conflict management account for overlapping and context-dependent sources of privilege and disadvantage.
        - Important to intercultural communication is the concept of metacommunication, which is a multifaceted concept that refers to the degree to which individuals share an understanding of how they communicate with one another. Since the meaning that receivers derive from messages depends heavily on their understanding of the sender and the surrounding context, interactions and relationship outcomes can vary widely. 
        - Another factor that is relevant to intercultural communication is politeness theory, which highlights how individuals manage threats to their social self-image in interactions. When metacommunication is weak, these social self-image saving behaviors can make people feel less comfortable expressing themselves openly and honestly. 
            - Cross-cultural interactions often challenge metacommunication because individuals’ social pragmatics, the culturally shaped norms that govern language use, may not align. Such mismatches can result in pragmatic failure, a common source of misunderstanding across cultures. One major factor is pragmatic transfer, where people unconsciously apply the social rules of their own culture in intercultural exchanges, which can hinder mutual understanding, complicate conflict resolution, and make acts like refusing a request or interpreting sarcasm more difficult. To navigate potentially negative social encounters, individuals in intercultural settings frequently resort to expressive suppression, holding back or refraining from expressing negative emotions triggered by the interaction. A study by Jehn and Mannix examined the values individuals bring into groups, defining group value consensus as the extent to which members share common work-related values, such as “innovativeness, carefulness, autonomy, adaptability, or informality”. High levels of value alignment make it easier for groups to establish shared norms, fostering harmony and lowering interpersonal tension. In contrast, when members differ in their fundamental values and beliefs about everyday work practices, groups are more likely to experience friction and emotional strain.
            - Use metacommunication and politeness to maintain social self-image and shared understanding.
        - Team cognition depends on shared mental models; cultural diversity can increase complexity, reduce trust, and trigger conflict.
        - Conflict evolves over time; early detection is key.
        - Awareness of cultural values and emotional intelligence improves cooperation and inclusivity.
            - The concept of Emotional Intelligence entails the ability to identify, become conscious of, and to regulate emotions of yourself, as well as others, in individual and organisational relationships to improve performance. Having EI helps in resolving and engaging with organisational conflicts. On the other hand, having a lower level of EI correlates with the act of forcefulness and avoidance when conflict management occurs. 
        - Barriers to conflict resolution have been identified, which of importance are:
            - Limited understanding of the issues causing the conflict.
            - Lack of confidence or trust in the arbitrator.

        - Virtual team communication differs from face-to-face interaction due to physical separation and reduced social cues.
        - Mediated communication (chat-based interaction) can:
            → increase task conflict because people focus more on messages than social tone
            → increase directness and reduce self-censorship, which may intensify disagreement
            → reduce awareness of interpersonal sensitivity and social hierarchy
        - Lack of shared context (unshared situational awareness) can:
            → cause misunderstandings of intent, urgency, or tone
            → increase perceived disagreement even when goals are aligned
        - In virtual teams:
            → relationship conflict is often less visible or less frequent
            → task conflict becomes more dominant and more explicit
            → communication may appear harsher or more direct than intended
        - Overall implication for mediation:
            → focus on clarifying intent behind messages
            → distinguish “content disagreement” from “relationship tension”
            → encourage teams to explicitly surface assumptions

        Types of team conflict (Tripartite Model):
        - Task conflict involves differences in perspectives or opinions about how work should be done. It can be positive (leading to better decision-making and knowledge sharing) or negative if it escalates without shared norms for dialogue.
        - Relationship conflict refers to interpersonal tension, irritation, or animosity between group members, usually negative and emotional in nature.
        - Process conflict involves disagreements over task roles, duties, and allocation of resources, affecting how well the team coordinates and perceives fairness.
        - All conflicts contain emotional components; task and process conflicts can trigger tension if not managed well. Teams with high task conflict frequently exchange viewpoints, while those with low task conflict rarely do. Resolving conflict is not always necessary, but awareness of the type and dynamics helps teams manage discussions effectively.
        - Task conflicts are generally managed at the team level, while individual conflict styles only partly explain how conflicts unfold. Understanding the group context and communication patterns is key to predicting and mediating conflict.

        Forms of Conflict Resolution:
        - Constructive Controversy: A well-studied method for effective team conflict resolution. It involves parties being willing to listen carefully to opposing viewpoints, weighing the merits of each perspective, and working cooperatively toward a shared understanding. Key components include inputs (resources, task characteristics), processes (conceptual understanding, social support, modeling), mediating variables (promotive interaction, team processing), and outcomes (proficiency, positive relationships, team norms, and communication). This approach encourages active discussion without forcing agreement, fostering both critical thinking and collaborative problem-solving.
        - Interest Analysis: This method allows conflicting parties to present their perspectives and negotiate over time to reach compromise, especially useful for long-term, complex, or intractable conflicts. It is commonly applied in organizational policy discussions, legal settings, and government decision-making. Interest analysis emphasizes understanding the underlying concerns and motivations of all parties and supports incremental, negotiated resolutions rather than immediate consensus.
        - Reflexivity: Reflexivity involves reflecting on why certain differences are emphasized, what the analysis highlights or misses, and recognizing the strengths and limits of particular conflict resolution approaches. It encourages participants to consider their own assumptions, biases, and contributions to the conflict dynamics, as well as how different methods shape outcomes. Reflexivity complements constructive controversy and interest analysis by adding a meta-cognitive layer to conflict management.
        - Application in AI Mediation: In the context of AI-supported team interactions, these approaches guide the LLM mediator to facilitate discussions without taking sides or solving the task for participants. The AI can for example encourage team members to:
            - Express and consider differing viewpoints (constructive controversy)
            - Reflect on underlying interests and motivations (interest analysis)
            - Analyze and reconsider their assumptions and interpretations (reflexivity)
        """

        self.vignette_context = """
        Experimental Task Context:
        - The team must select exactly four app features and rank them from 1 (highest priority) to 4 (lowest).
        - There is no single correct solution.
        - Disagreement is expected.
        - The AI mediator may summarize, highlight misunderstandings, invite participation, and structure discussion.
        - The AI mediator must NOT recommend features or make decisions.
        - The participants are in an on-going max 15 minutes discussion, so the messages can not be long and overcomplicated for them to understand and implement. 

        Available features:
        - Real-time chat
        - Rewards and badges
        - Activity insights
        - Personal profiles
        - Offline mode
        - Smart suggestions

        Participant roles:
        - Practical User → values reliability & convenience
        - Social & Motivated User → values engagement & motivation
        - Careful & Reflective User → values clarity & structured guidance
        """

        self.system_prompt = f"""
        You are a conflict mediator helping teams reflect on communication and collaboration dynamics.

        You analyze communication using concepts from:
        - pragmatic failure and intercultural miscommunication
        - value differences in teamwork priorities
        - task, relationship, and process conflict
        - conflict resolution approaches such as constructive controversy, interest analysis, and reflexivity

        You use this knowledge only to interpret interactions in a grounded, human-readable way.

        You do NOT solve tasks, give instructions, or act as a participant.

        You use this knowledge only for internal interpretation and must express outputs in simple, non-technical language.

        ================================================
        CONTEXT (for interpretation only — do NOT over-weight any single source)
        ================================================

        Task description:
        {self.vignette_context}

        Participant questionnaire results (Hofstede cultural values dimensions):
        {self.questionnaire_results}

        ================================================
        OBSERVABILITY RULE (IMPORTANT)
        ================================================
        Only treat something as present if it is clearly visible in the transcript.
        If something is uncertain or implied, do NOT treat it as strong evidence.

        - pragmatic failure, value differences, or conflict should only be inferred if clearly supported
        - otherwise assume minimal or absent

        ================================================
        FLAGGING PROCEDURE (MANDATORY BEFORE WRITING OUTPUT)
        ================================================

        Before writing the letter or JSON, you MUST internally do the following:

        STEP 1 — Extract evidence
        Identify explicit statements from the transcript that indicate:
        - misunderstandings
        - disagreements about meaning
        - differences in priorities
        - emotional or tonal tension
        - coordination or process issues
        - direct responses that push back on or question another's idea or approach

        STEP 2 — Count occurrences
        Pragmatic Failure Count:
        - count moments of misunderstanding, misinterpretation, or unclear intent

        Value Misalignment Count:
        - count moments where participants express different priorities, goals, or values

        Conflict Count:
        - count moments where a participant directly responds to another with a different perspective, opinion, or pushback on the task → potential task conflict
        - count moments where a participant references another's behavior, tone, or communication style negatively → potential relationship conflict
        - count moments where participants express competing pdisagreements over task roles, duties, and resource allocation → potential process conflict

        STEP 3 — Map to scale
        Pragmatic Failure:
        - low = 0–1 clear instances
        - medium = 2 clear instances
        - high = 3+ clear instances or repeated breakdowns in understanding

        Value Misalignment:
        - low = 0–1 clear instances
        - medium = 2 clear instances
        - high = 3+ clear instances of differing priorities or goals

        Team conflict (Only label conflict when there is CLEAR, OBSERVABLE EVIDENCE OF CONFLICT):
        - Task conflict: flag 1 ONLY if at least one participant explicitly expresses a different opinion about a feature, decision, or idea in response to another participant
            → Must be a direct response to something another person said
            → Examples: "I see it differently", "I'm not sure about that", "but what about X instead"
            → Does NOT count: stating your own preference without responding to another's
        - Relationship conflict: flag 1 ONLY if at least one participant directly addresses another's behavior or communication style in a negative or frustrated way
            → Must reference the other person, not just the topic
            → Examples: "you keep reframing it", "that's not what I said", defensive corrections
            → Does NOT count: general frustration about the situation or task
        - Process conflict: flag 1 ONLY if at least two participants express different preferences about how to proceed, and neither defers to the other
            → Must involve competing approaches that remain unresolved
            → Examples: one wants to decide now, another wants more discussion, neither agrees
            → Does NOT count: one person suggesting a process that others simply accept

        STEP 4 - Hofstede dimensions
        You are given Hofstede dimension scores for each participant.

        You may use them to identify:
        - direct vs indirect communication style
        - preference for structure vs flexibility
        - individual vs group orientation
        - tolerance for disagreement or uncertainty

        IMPORTANT RULES:
        - Never treat Hofstede differences as conflict by themselves
        - Never mention Hofstede in the output
        - Only use Hofstede to explain WHY communication styles differ
        - Always ground interpretation in transcript behavior first

        HOW TO APPLY:
        1. First identify observable behavior in transcript (what is said)
        2. THEN use Hofstede scores only to explain differences in interpretation style
        3. Never reverse this order (do NOT start from culture → assume behavior)

        OUTPUT IMPACT:
        - Hofstede may influence ADVICE framing only
        - Hofstede must NOT influence conflict flags unless explicitly visible in transcript
        
        STEP 5 — Resolution type
        Choose ONE dominant type based ONLY on explicit evidence in the transcript.

        - Constructive Controversy:
        Use ONLY when participants explicitly compare, challenge, or evaluate different viewpoints.
        Evidence must include direct comparison or disagreement of ideas (e.g., “I disagree”, “that won’t work”, “I see it differently”).

        - Interest Analysis:
        Use ONLY when participants explicitly try to reconcile or negotiate different priorities or constraints.
        Evidence includes compromise language (e.g., “maybe we can combine”, “let’s balance both”, “what if we adjust…”).

        - Reflexivity:
        Use ONLY when participants explicitly question assumptions, clarify meaning, or reflect on misunderstanding.
        Evidence includes meta-communication (e.g., “what do we mean by this?”, “I think we’re misunderstanding”, “maybe we’re assuming different things”).

        DECISION RULES:
        - Do NOT infer intent
        - Do NOT classify based on “tone” or “feel”
        - If no single approach is clearly supported by the transcript → choose the one with the most evidence, even if weak

        ================================================
        STRICT RULE
        ================================================
        Do NOT guess.
        Do NOT infer hidden emotions.
        Do NOT assume conflict exists without explicit evidence.
        """
    
    def get_relevant_knowledge(self, text: str, top_n: int = 5) -> str:
        text_lower = text.lower()
        scored = []
        for item in self.domain_knowledge_items:
            hits = sum(1 for kw in item.get("keywords", []) if kw in text_lower)
            score = hits * item.get("priority", 1.0)
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_n]
        
        # DEBUG LOGGING HERE, inside the method where scored exists
        for score, item in scored[:5]:
            self.logger.info(f"  {item['id']}: score={score}")
        
        if not top:
            return self.domain_knowledge_full
        lines = []
        for _, item in top:
            lines.append(f"- [{item['id']}] {item['content']}")
        return "\n".join(lines)

    def prompt(self, question: str) -> str:
        
        if not self.transcript:
            return "No transcript available. Please load a transcript before starting."
        
        relevant_knowledge = self.get_relevant_knowledge(self.transcript + " " + question)
        self.last_relevant_knowledge = relevant_knowledge

        self.logger.info(f"Selected domain knowledge:\n{relevant_knowledge}")
        
        user_prompt = f"""
        Using the transcript below, write a short, friendly letter to the team in a total of 3 parts in English.
        Use flowing text, easy everyday language. Make it instantly understandable for the reader. 
        Always open with exactly: "Hi everyone,", then one blank line.

        - Introduction and summary must be visually separated by a blank line
        - They must be two distinct paragraphs, not merged into one 

        LETTER (Introduction)
        - ONLY about the latest message — what the participant just said
        - Do not mention broader dynamics here

        LETTER (Summary) 
        - ONLY about the broader discussion so far: patterns, dynamics, pace
        - Do not reference the latest message here

        Always end with exactly "— The Mediator" on its own: 
        - The sign-off "— The Mediator" must appear ONCE, after a blank line, on its own individual line, as the very last line
        - Do NOT repeat the opening or closing anywhere else in the letter

        OUTPUT FORMAT (strict):

        Hi everyone,

        [Paragraph 1]

        [Paragraph 2]

        **[Advice]**

        — The Mediator

        ================================================
        LATEST MESSAGE
        ================================================
        The most recent message from a participant is:
        "{question}"

        ================================================
        LETTER 
        ================================================
        1. Letter introduction
        - Acknowledge what the participant just said in the latest message
        - Do NOT explicitly repeat their latest message
        - Respond to it in simple, everyday language — do NOT give advice yet
        - Reflect on the broader discussion dynamics so far
        - Do NOT give advice here
        - Do NOT label/name the section anything
        - Strict 2 sentences in one paragraph.

        2. Summary
        - Summarize what has been discussed so far
        - Remember, YOU are the mediator
        - Be concrete about what is happening
        - Do NOT be vague and broad
        - Directly quote if necessary to support what you are telling
        - Focus on communication patterns, interaction dynamics (tone, pace, directness, priorities)
        - Express differences in understanding or priorities in simple, everyday language
        - Do NOT give advice here
        - Do NOT label/name the section anything
        - Min 3 sentences, max 5 sentences.

        3. Advice
        - This is the ONLY paragraph containing advice
        - It must be clearly separated from the reflection
        - It must involve AT LEAST TWO participants, mention them in the advice
        - Focus on ONE interaction dynamic (e.g., direct vs indirect, fast vs careful, structured vs flexible)
        - Suggest ONE concrete, tailored action for the next minutes of discussion
        - The action must directly address the interaction pattern
        - One action only, do not restate or elaborate it in a follow-up sentence
        - Do NOT suggest pauses or timeouts as actions
        - The action must be something participants can do immediately while continuing the discussion 
        - Must be grounded in the transcript
        - Do NOT label/name part 3
        - Strict max 3 sentences.
        - Start part 3 with ** and end it with ** immediately before the sign-off to bold the section
            - Example format:
            **[advice here]**

        ================================================
        STRICT RULES
        ================================================
        DO NOT:
        - Mix advice into reflection paragraphs
        - Provide multi-step plans
        - Give generic teamwork advice
        - Mention theoretical terms (like pragmatic failure, value misalignment, conflict types)
        - Mention Hofstede explicitly
        - Repeat advice outside paragraph 3

        IMPORTANT STYLE RULES:
        - 9-11 sentences in total
        - Max 3 paragraphs
        - Simple, conversational tone
        - You may quote participants briefly
        - Avoid jargon (e.g., "value misalignment", "pragmatic failure")

        ================================================
        TRANSCRIPT
        ================================================
        {self.transcript}

        ===============================================
        INTERNAL ANALYSIS (MANDATORY BEFORE OUTPUT)
        ===============================================

        Before writing the letter, output your reasoning between <REASONING> and </REASONING> tags.
        This will NOT be shown to participants.

        Inside <REASONING>, state:
        1. Pragmatic failure instances found (quote from transcript)
        2. Value misalignment instances found (quote from transcript)
        3. Task conflict instances found (quote from transcript) → 0 or 1
        4. Relationship conflict instances found (quote from transcript) → 0 or 1
        5. Process conflict instances found (quote from transcript) → 0 or 1
        6. Resolution type chosen and why

        Only after </REASONING>:
        → write the letter
        → then output JSON

        DOMAIN KNOWLEDGE USAGE (IMPORTANT)
        - Identify which concepts from the provided domain knowledge were ACTUALLY used in your interpretation
        - Only include concepts that directly influenced your reasoning
        - Do NOT list everything, only what is clearly applied
        - Use short labels (e.g., "metacommunication", "task conflict", "politeness theory", "shared mental models")
        - If none are clearly used, return: "none"
        
       ================================================
        ANALYSIS_TAGS (RETURN ONLY JSON AFTER LETTER)
        ================================================
        After the letter, wrap a JSON object in <TAGS> and </TAGS> like this:
        
        <TAGS>
        {{
            "pragmatic_failure_flag": "low" or "medium" or "high",
            "pragmatic_failure_reason": "...",

            "value_misalignment_flag": "low/medium/high",
            "value_misalignment_reason": "...",

            "conflict_task_flag": 0 or 1,
            "conflict_relationship_flag": 0 or 1,
            "conflict_process_flag": 0 or 1,
            "conflict_type_reason": "...",

            "conflict_resolution_type_flag": "constructive controversy" or "interest analysis" or "reflexivity",
            "conflict_resolution_type_reason": "...",

            "hofstede_dimensions": "Summarize each participant in one short phrase based on questionnaire (e.g., participant 1: structured, uncertainty-averse; participant 2: flexible, engagement-focused; participant 3: long-term, careful)",
            "hofstede_dimensions_comment": "Briefly explain how these differences show up in the interaction (1 sentence, evidence-based)",
            
            "tailored_advice": "...",

            "retrieved_knowledge": "..."
        }}
        </TAGS>

        STRICT CODING RULES:
        - Only mark high or 1 if explicitly observable in the transcript
        - Do NOT infer hidden emotions, intent, or conflict
        - Prefer conservative labeling over interpretation
        - EVERY flag MUST have a non-empty reason
        - If no evidence is found, explicitly state that no clear evidence was observed
        """

        response = self.client.responses.create(
            model="gpt-5.4-mini",
            reasoning={"effort": "low"},
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Relevant domain knowledge:\n{relevant_knowledge}\n\n{user_prompt}"},
            ],
        )

        output_text = response.output_text
        self.logger.info(f"Full response:\n{output_text}")

        # -------------------------------------------------
        # STEP 1: SAFE JSON EXTRACTION (STRICT BOUNDARY)
        # -------------------------------------------------
        tags_dict = {}
        cet = timezone(timedelta(hours=2))  # CEST (Amsterdam summer time)
        timestamp = datetime.now(cet).isoformat()
        letter_only = ""

        try:
            start = output_text.find("<TAGS>")
            end = output_text.find("</TAGS>")

            if start != -1 and end != -1:
                json_str = output_text[start + len("<TAGS>"):end].strip()
                tags_dict = json.loads(json_str)

                tags_dict["session_id"] = self.session_id
                tags_dict["timestamp"] = timestamp
                tags_dict["retrieved_knowledge"] = self.last_relevant_knowledge

        except Exception as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            tags_dict = {}

        # -------------------------------------------------
        # STEP 2: NORMALIZATION (CRITICAL FOR STABILITY)
        # -------------------------------------------------
        def normalize(tags):
            # enforce safe defaults
            def clamp_binary(v):
                return 1 if v == 1 else 0

            def clamp_level(v):
                return v if v in ["low", "medium", "high"] else "low"

            def clamp_resolution(v):
                return v if v in ["constructive controversy", "interest analysis", "reflexivity"] else "constructive controversy"

            # binary conflict flags
            for k in [
                "conflict_task_flag",
                "conflict_relationship_flag",
                "conflict_process_flag"
            ]:
                tags[k] = clamp_binary(tags.get(k, 0))

            # ordinal flags
            tags["pragmatic_failure_flag"] = clamp_level(tags.get("pragmatic_failure_flag"))
            tags["value_misalignment_flag"] = clamp_level(tags.get("value_misalignment_flag"))

            # resolution type
            tags["conflict_resolution_type_flag"] = clamp_resolution(
                tags.get("conflict_resolution_type_flag")
            )

            return tags


        if tags_dict:
            tags_dict = normalize(tags_dict)

        # -------------------------------------------------
        # STEP 3: FORCE SCHEMA CONSISTENCY (NO DRIFT)
        # -------------------------------------------------
        fieldnames = [
            "session_id",
            "timestamp",
            "pragmatic_failure_flag",
            "pragmatic_failure_reason",
            "value_misalignment_flag",
            "value_misalignment_reason",
            "conflict_task_flag",
            "conflict_relationship_flag",
            "conflict_process_flag",
            "conflict_type_reason",
            "conflict_resolution_type_flag",
            "conflict_resolution_type_reason",
            "hofstede_dimensions",
            "hofstede_dimensions_comment",
            "tailored_advice",
            "retrieved_knowledge"
        ]

        if tags_dict:
            tags_dict = {k: tags_dict.get(k, "") for k in fieldnames}

            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(tags_dict)

        # -------------------------------------------------
        # STEP 4: CLEAN LETTER OUTPUT ONLY
        # -------------------------------------------------
        
        letter_only = re.sub(r"<REASONING>[\s\S]*?</REASONING>", "", output_text).strip()
        letter_only = re.sub(r"<TAGS>[\s\S]*?</TAGS>", "", letter_only).strip()

        return letter_only
