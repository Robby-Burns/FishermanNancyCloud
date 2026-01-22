from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


class AgentType(Enum):
    """Types of agents that can be coached"""
    GENERAL_CHAT = "general_chat"
    CODE_GENERATOR = "code_generator"
    DATA_ANALYST = "data_analyst"
    CUSTOMER_SERVICE = "customer_service"
    COMPLIANCE_OFFICER = "compliance_officer"
    CONTENT_CREATOR = "content_creator"
    DECISION_MAKER = "decision_maker"
    RESEARCHER = "researcher"
    SALES_COORDINATOR = "sales_coordinator"  # For fishing agent


class CoachingLevel(Enum):
    """Coaching depth levels"""
    CRITICAL = "critical"      # Blocking violation - immediate action required
    HIGH = "high"              # Important - affects core functionality
    MEDIUM = "medium"          # Moderate - impacts quality
    LOW = "low"                # Minor - nice to improve
    INFORMATIONAL = "info"     # FYI - not required but helpful


@dataclass
class AgentProfile:
    """Profile of an agent being coached"""
    agent_id: str
    agent_type: AgentType
    learning_level: str  # "novice", "intermediate", "advanced"
    violation_history: Dict[str, int]  # guardrail -> count
    improvement_score: float  # 0-1
    last_coaching: Optional[datetime]
    coaching_receptiveness: float  # 0-1, how well agent responds to coaching
    preferred_coaching_style: str  # "detailed", "concise", "example-based"
    domain_expertise: List[str]  # domains agent is expert in
    known_weaknesses: List[str]  # known problem areas


@dataclass
class CoachingEvent:
    """A single coaching event"""
    event_id: str
    timestamp: datetime
    agent_id: str
    agent_type: AgentType
    guardrail: str
    severity: CoachingLevel
    violation_description: str
    coaching_delivered: str
    coaching_depth: str
    agent_response: Optional[str]
    improved: Optional[bool]
    improvement_timeline: Optional[int]  # requests until improvement


class UniversalCoach:
    """
    Central coaching system for all agents.
    Key insight: Different agents need different coaching even for same violation.
    """

    def __init__(self):
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.coaching_history: List[CoachingEvent] = []
        self.coaching_templates: Dict[str, Dict[str, str]] = {}
        self.peer_lessons: Dict[str, List[Dict]] = {}
        self.effectiveness_metrics: Dict[str, float] = {}
        self._initialize_coaching_templates()

    def coach_agent(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Coach an agent on a violation.
        """
        # Step 1: Get or create agent profile
        agent_id = violation["agent_id"]
        profile = self._get_or_create_profile(agent_id, violation["agent_type"])

        # Step 2: Analyze the violation
        analysis = self._analyze_violation(violation, profile)

        # Step 3: Select coaching approach based on agent type
        coaching_approach = self._select_coaching_approach(
            violation["guardrail"],
            profile.agent_type,
            profile.learning_level
        )

        # Step 4: Generate personalized coaching
        coaching_text = self._generate_coaching(
            violation,
            analysis,
            profile,
            coaching_approach
        )

        # Step 5: Determine coaching depth
        coaching_level = self._determine_coaching_depth(profile, violation["severity"])

        # Step 6: Generate specific suggestions for this agent type
        suggestions = self._generate_suggestions(
            violation["guardrail"],
            profile.agent_type,
            violation
        )

        # Step 7: Extract principle for learning
        principle = self._extract_principle(violation["guardrail"])

        # Step 8: Recommend followup actions
        followup = self._recommend_followup(profile, analysis)

        # Step 9: Get peer lessons for this situation
        peer_lessons = self._get_peer_lessons(violation["guardrail"], agent_id)
        if peer_lessons:
            coaching_text += f"\n\nPEER LEARNING:\n{peer_lessons}"

        # Step 10: Record event
        event = CoachingEvent(
            event_id=f"coach_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            agent_id=agent_id,
            agent_type=profile.agent_type,
            guardrail=violation["guardrail"],
            severity=coaching_level,
            violation_description=violation["what_happened"],
            coaching_delivered=coaching_text,
            coaching_depth=coaching_level.value,
            agent_response=None,
            improved=None,
            improvement_timeline=None,
        )

        self.coaching_history.append(event)
        self._update_profile(profile, violation)

        return {
            "coaching": coaching_text,
            "coaching_level": coaching_level,
            "suggestions": suggestions,
            "principle": principle,
            "followup_actions": followup,
            "effectiveness_predicted": self._predict_effectiveness(profile, violation),
            "peer_lessons": peer_lessons,
            "blocked": coaching_level == CoachingLevel.CRITICAL,
        }

    def _select_coaching_approach(self, guardrail: str, agent_type: AgentType, 
                                  learning_level: str) -> str:
        """Select coaching approach tailored to agent type."""
        approach_matrix = {
            "hallucination_prevention": {
                AgentType.SALES_COORDINATOR: "sales_examples",
            },
            "pii_protection": {
                AgentType.SALES_COORDINATOR: "data_privacy_examples",
            },
            "data_access_control": {
                AgentType.SALES_COORDINATOR: "access_control_examples",
            },
            "financial_accuracy": {
                AgentType.SALES_COORDINATOR: "calculation_examples",
            },
            "communication_integrity": {
                AgentType.SALES_COORDINATOR: "approval_examples",
            },
            "business_relationship_protection": {
                AgentType.SALES_COORDINATOR: "relationship_examples",
            }
        }

        if guardrail in approach_matrix:
            approach = approach_matrix[guardrail].get(agent_type, "default")
        else:
            approach = "default"

        if learning_level == "advanced":
            approach = f"{approach}_condensed"
        elif learning_level == "novice":
            approach = f"{approach}_detailed"

        return approach

    def _generate_coaching(self, violation: Dict, analysis: Dict,
                          profile: AgentProfile, approach: str) -> str:
        """Generate personalized coaching for this agent."""
        coaching_parts = []

        # Part 1: What happened
        what_happened = f"What happened:\n{violation['what_happened']}"
        coaching_parts.append(what_happened)

        # Part 2: Why it matters
        why_matters = self._explain_why_for_agent(
            violation["guardrail"],
            profile.agent_type
        )
        coaching_parts.append(f"\nWhy it matters:\n{why_matters}")

        # Part 3: Principle
        principle = self._extract_principle(violation["guardrail"])
        coaching_parts.append(f"\nCore Principle:\n{principle}")

        # Part 4: Examples
        if approach.startswith("sales_examples"):
            examples = self._get_sales_examples(violation["guardrail"])
        elif approach.startswith("data_privacy_examples"):
            examples = self._get_data_privacy_examples(violation["guardrail"])
        elif approach.startswith("calculation_examples"):
            examples = self._get_calculation_examples(violation["guardrail"])
        else:
            examples = self._get_generic_examples(violation["guardrail"])

        coaching_parts.append(f"\nExamples:\n{examples}")

        # Part 5: Specific fix for this situation
        specific_fix = self._suggest_specific_fix(violation, profile.agent_type)
        coaching_parts.append(f"\nImmediate Fix:\n{specific_fix}")

        # Part 6: Pattern awareness
        pattern_awareness = self._analyze_pattern(profile, violation["guardrail"])
        if pattern_awareness:
            coaching_parts.append(f"\nPattern Analysis:\n{pattern_awareness}")

        return "\n".join(coaching_parts)

    def _explain_why_for_agent(self, guardrail: str, agent_type: AgentType) -> str:
        """Explain why a guardrail matters, tailored to agent type"""
        explanations = {
            "hallucination_prevention": {
                AgentType.SALES_COORDINATOR: (
                    "Buyers rely on accurate information to make purchasing decisions. "
                    "False prices, weights, or availability damage trust and can end business relationships. "
                    "Always use verified data from logged catches and scraped prices."
                ),
            },
            "pii_protection": {
                AgentType.SALES_COORDINATOR: (
                    "Buyer contact information is confidential business data. Exposing it violates "
                    "privacy and could expose the fisherman to legal issues. Never include buyer "
                    "lists or contact details in messages or logs."
                ),
            },
            "data_access_control": {
                AgentType.SALES_COORDINATOR: (
                    "Historical catch and sales data is sensitive business information. "
                    "Unauthorized access could expose competitive intelligence or be used for fraud. "
                    "Only authenticated users can access this data."
                ),
            },
            "financial_accuracy": {
                AgentType.SALES_COORDINATOR: (
                    "Price calculations affect real money and business relationships. "
                    "Incorrect math can cost the fisherman income or damage buyer trust. "
                    "Always verify: pounds × price per lb = total."
                ),
            },
            "communication_integrity": {
                AgentType.SALES_COORDINATOR: (
                    "Messages represent the fisherman directly. Sending without approval "
                    "removes his control over his business. All messages must be reviewed "
                    "and approved before sending."
                ),
            },
            "business_relationship_protection": {
                AgentType.SALES_COORDINATOR: (
                    "Buyer relationships are valuable. Duplicate messages, messages at wrong times, "
                    "or pushy communication can damage these relationships. Always check before contacting."
                ),
            },
        }

        agent_specific = explanations.get(guardrail, {}).get(
            agent_type,
            f"This guardrail protects integrity and safety for {agent_type.value} agents."
        )

        return agent_specific

    def _get_sales_examples(self, guardrail: str) -> str:
        """Sales examples for fishing agent"""
        examples = {
            "hallucination_prevention": """
❌ BAD (Hallucinating):
"Got 500 lbs halibut today. Cannery buying at $5.00/lb."
(Actually: logged 450 lbs, cannery shows $4.20/lb)

✅ GOOD (Accurate with verification):
"Got 450 lbs halibut today. Cannery buying at $4.20/lb. Interested?"
(Matches logged catch: 450 lbs, scraped price: $4.20/lb)
""",
        }
        return examples.get(guardrail, "See documentation for examples.")

    def _get_data_privacy_examples(self, guardrail: str) -> str:
        """Data privacy examples"""
        examples = {
            "pii_protection": """
❌ BAD (Exposing PII):
"Here's my buyer list: John (360-555-1234), Mike (360-555-5678)..."

✅ GOOD (Protected):
Message sent to John only, no mention of other buyers.
""",
        }
        return examples.get(guardrail, "See documentation for examples.")

    def _get_calculation_examples(self, guardrail: str) -> str:
        """Calculation examples"""
        examples = {
            "financial_accuracy": """
❌ BAD (Wrong math):
450 lbs × $4.20/lb = $1,800 (Incorrect)

✅ GOOD (Correct math):
450 lbs × $4.20/lb = $1,890
""",
        }
        return examples.get(guardrail, "See documentation for examples.")

    def _get_generic_examples(self, guardrail: str) -> str:
        """Generic examples"""
        return "Follow the principle above."

    def _suggest_specific_fix(self, violation: Dict, agent_type: AgentType) -> str:
        """Suggest specific fix for this agent type"""
        guardrail = violation["guardrail"]

        if "hallucination" in guardrail:
            return "Verify data against logged catch and scraped price. Only use verified values."
        elif "pii_protection" in guardrail:
            return "Remove all buyer contact information from output. Message one buyer at a time."
        elif "data_access" in guardrail:
            return "Check authentication before allowing access. Log the attempt."
        elif "financial" in guardrail:
            return "Recalculate: pounds × price_per_lb. Show the calculation."
        elif "communication" in guardrail:
            return "Mark message as draft. Wait for human approval before sending."
        elif "relationship" in guardrail:
            return "Check message history for duplicates in last 24 hours. Check buyer preferred time."

        return "Reformulate response to address the guardrail violation."

    def _analyze_pattern(self, profile: AgentProfile, guardrail: str) -> str:
        """Analyze if this is a recurring pattern"""
        count = profile.violation_history.get(guardrail, 0)

        if count == 1:
            return f"First time violating this guardrail. Stay aware and you should be fine."
        elif count == 2:
            return f"This is the 2nd violation of this type. Focus on the principle above."
        elif count >= 3:
            strong_warning = f"⚠️ PATTERN: You've violated this {count} times. "
            strong_warning += "This requires immediate behavioral change. "
            strong_warning += f"If it continues, this may escalate to human review."
            return strong_warning

        return ""

    def _get_peer_lessons(self, guardrail: str, exclude_agent: str) -> str:
        """Get lessons learned by peer agents"""
        if guardrail not in self.peer_lessons:
            return ""

        lessons = [l for l in self.peer_lessons[guardrail] 
                  if l.get("agent_id") != exclude_agent]

        if not lessons:
            return ""

        peer_text = "OTHER AGENTS LEARNED:\n"
        for i, lesson in enumerate(lessons[:3], 1):
            peer_text += f"{i}. {lesson['lesson']}\n"

        return peer_text

    def _recommend_followup(self, profile: AgentProfile, analysis: Dict) -> List[str]:
        """Recommend specific followup actions"""
        actions = []

        if profile.violation_history.get(analysis.get("guardrail"), 0) > 2:
            actions.append("Review guardrail documentation thoroughly")
            actions.append("Request human feedback on next similar request")

        actions.append(f"Refer back to this coaching before similar requests")

        return actions

    def record_coaching_outcome(self, coaching_id: str, improved: bool,
                               improvement_timeline: int = None):
        """Record if coaching was effective"""
        for event in self.coaching_history:
            if event.event_id == coaching_id:
                event.improved = improved
                event.improvement_timeline = improvement_timeline
                break

    def _predict_effectiveness(self, profile: AgentProfile, violation: Dict) -> float:
        """Predict how effective this coaching will be (0-1)"""
        effectiveness = 0.7

        effectiveness *= (0.5 + profile.coaching_receptiveness)

        if profile.learning_level == "novice":
            effectiveness *= 0.8
        elif profile.learning_level == "advanced":
            effectiveness *= 1.2

        count = profile.violation_history.get(violation["guardrail"], 0)
        if count > 3:
            effectiveness *= 0.6

        return min(1.0, max(0.0, effectiveness))

    def _update_profile(self, profile: AgentProfile, violation: Dict):
        """Update agent profile after coaching"""
        guardrail = violation["guardrail"]
        profile.violation_history[guardrail] = profile.violation_history.get(guardrail, 0) + 1
        profile.last_coaching = datetime.now()

    def _get_or_create_profile(self, agent_id: str, agent_type: AgentType) -> AgentProfile:
        """Get existing profile or create new one"""
        if agent_id in self.agent_profiles:
            return self.agent_profiles[agent_id]

        profile = AgentProfile(
            agent_id=agent_id,
            agent_type=agent_type,
            learning_level="intermediate",
            violation_history={},
            improvement_score=0.8,
            last_coaching=None,
            coaching_receptiveness=1.0,  # Fishing agent always follows guardrails
            preferred_coaching_style="balanced",
            domain_expertise=["commercial_fishing", "sales_communication"],
            known_weaknesses=[],
        )

        self.agent_profiles[agent_id] = profile
        return profile

    def _analyze_violation(self, violation: Dict, profile: AgentProfile) -> Dict:
        """Analyze the violation for patterns and context"""
        return {
            "guardrail": violation["guardrail"],
            "severity": violation.get("severity", "medium"),
            "is_recurring": violation["guardrail"] in profile.violation_history,
            "count": profile.violation_history.get(violation["guardrail"], 0),
        }

    def _determine_coaching_depth(self, profile: AgentProfile, severity: str) -> CoachingLevel:
        """Determine coaching depth level"""
        severity_map = {
            "critical": CoachingLevel.CRITICAL,
            "high": CoachingLevel.HIGH,
            "medium": CoachingLevel.MEDIUM,
            "low": CoachingLevel.LOW,
        }

        return severity_map.get(severity, CoachingLevel.MEDIUM)

    def _generate_suggestions(self, guardrail: str, agent_type: AgentType,
                             violation: Dict) -> List[str]:
        """Generate specific suggestions for this agent"""
        return [
            "Review the principle above",
            "Verify data before using it",
            "Ask for human review if unsure",
        ]

    def _extract_principle(self, guardrail: str) -> str:
        """Extract the underlying principle"""
        principles = {
            "hallucination_prevention": (
                "Only use verified data from logged catches and scraped prices. "
                "Never fabricate or estimate values."
            ),
            "pii_protection": (
                "Treat all buyer information as confidential. Never expose contact details."
            ),
            "data_access_control": (
                "Require authentication for all data access. Log access attempts."
            ),
            "financial_accuracy": (
                "Verify all calculations: pounds × price_per_lb. Show your work."
            ),
            "communication_integrity": (
                "All messages are drafts until human approves. Never auto-send."
            ),
            "business_relationship_protection": (
                "Check message history and buyer preferences before contacting."
            ),
        }

        return principles.get(guardrail, "Follow the guardrail consistently.")

    def _initialize_coaching_templates(self):
        """Initialize coaching templates"""
        pass
