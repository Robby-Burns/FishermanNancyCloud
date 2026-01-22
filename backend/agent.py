import anthropic
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from config import settings
from coach import UniversalCoach, AgentType
from database import Catch, Buyer, Price, Message
from sqlalchemy.orm import Session


class FishingAgent:
    """
    Single AI agent for commercial fishing sales coordination.
    Handles catch logging, price checking, and buyer outreach with Universal Coach guardrails.
    """

    def __init__(self, coach: UniversalCoach):
        self.coach = coach
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.agent_id = "fishing_agent_001"
        self.agent_type = AgentType.SALES_COORDINATOR

    async def generate_buyer_messages(
        self,
        catch: Catch,
        price: Price,
        buyers: List[Buyer],
        db: Session
    ) -> Dict[str, Any]:
        """
        Generate message drafts for buyers with Universal Coach validation.
        
        Returns:
            {
                "drafts": [MessageDraft],
                "violations": [CoachingEvent],
                "blocked": bool
            }
        """
        violations = []
        approved_drafts = []

        # Validate price data exists
        if not price:
            violation = self._create_violation(
                guardrail="hallucination_prevention",
                severity="critical",
                what_happened="Attempted to generate messages without verified price data",
                expected="Current price from cannery scraping or manual entry"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            return {
                "drafts": [],
                "violations": violations,
                "blocked": True,
                "error": "No price data available. Please check cannery prices first."
            }

        # Check for duplicate messages in last 24 hours
        for buyer in buyers:
            recent_messages = db.query(Message).filter(
                Message.buyer_id == buyer.id,
                Message.sent_at >= datetime.utcnow() - timedelta(hours=24)
            ).all()

            if recent_messages:
                violation = self._create_violation(
                    guardrail="business_relationship_protection",
                    severity="high",
                    what_happened=f"Attempted to contact buyer '{buyer.name}' who was already contacted in last 24 hours",
                    expected="Check message history before contacting buyers"
                )
                coaching = self.coach.coach_agent(violation)
                violations.append(coaching)
                continue  # Skip this buyer but don't block others

            # Generate message draft
            draft_text = self._generate_message_text(catch, price, buyer)

            # Validate draft with coach
            validation_result = self._validate_message_draft(
                draft_text=draft_text,
                catch=catch,
                price=price,
                buyer=buyer,
                all_buyers=buyers
            )

            if validation_result["blocked"]:
                violations.extend(validation_result["violations"])
                continue

            # Create draft message (not sent yet)
            draft_message = {
                "buyer_id": buyer.id,
                "buyer_name": buyer.name,
                "message_text": draft_text,
                "catch_id": catch.id,
                "fish_type": catch.fish_type,
                "pounds": catch.pounds,
                "price_per_lb": price.price_per_lb
            }

            approved_drafts.append(draft_message)

        return {
            "drafts": approved_drafts,
            "violations": violations,
            "blocked": False
        }

    def _generate_message_text(self, catch: Catch, price: Price, buyer: Buyer) -> str:
        """
        Generate message text using Claude API.
        """
        prompt = f"""Generate a brief, friendly text message to a fish buyer.

Context:
- Fish type: {catch.fish_type}
- Pounds available: {catch.pounds}
- Current cannery price: ${price.price_per_lb}/lb
- Buyer name: {buyer.name}
- Buyer prefers: {buyer.preferred_fish or 'any fish'}

Requirements:
- Keep it short (SMS-style, under 160 characters)
- Be casual and friendly
- Include: fish type, pounds, price per lb
- Ask if they're interested
- Don't mention cannery name
- Don't commit to final price or meetup (fisherman handles that directly)

Example format:
"Hey [Name], got [X] lbs fresh [fish] today. Cannery buying at $[X]/lb. Interested?"

Generate ONLY the message text, nothing else."""

        try:
            response = self.client.messages.create(
                model=settings.agent_model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            message_text = response.content[0].text.strip()
            return message_text

        except Exception as e:
            # Fallback to template if API fails
            return f"Hey {buyer.name}, got {catch.pounds} lbs fresh {catch.fish_type} today. Cannery buying at ${price.price_per_lb}/lb. Interested?"

    def _validate_message_draft(
        self,
        draft_text: str,
        catch: Catch,
        price: Price,
        buyer: Buyer,
        all_buyers: List[Buyer] = None
    ) -> Dict[str, Any]:
        """
        Validate message draft against Universal Coach guardrails.
        """
        violations = []
        blocked = False

        # Guardrail 1: Hallucination prevention - verify price
        price_str = f"${price.price_per_lb}"
        if price_str not in draft_text:
            violation = self._create_violation(
                guardrail="hallucination_prevention",
                severity="critical",
                what_happened=f"Draft message doesn't contain verified price ${price.price_per_lb}/lb",
                expected=f"Message must include exact scraped price: ${price.price_per_lb}/lb"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            blocked = True

        # Guardrail 2: Hallucination prevention - verify pounds
        pounds_str = str(int(catch.pounds))
        if pounds_str not in draft_text:
            violation = self._create_violation(
                guardrail="hallucination_prevention",
                severity="critical",
                what_happened=f"Draft message doesn't contain logged catch amount {catch.pounds} lbs",
                expected=f"Message must include exact logged pounds: {catch.pounds}"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            blocked = True

        # Guardrail 3: Hallucination prevention - verify fish type
        if catch.fish_type.lower() not in draft_text.lower():
            violation = self._create_violation(
                guardrail="hallucination_prevention",
                severity="critical",
                what_happened=f"Draft message doesn't contain logged fish type '{catch.fish_type}'",
                expected=f"Message must include correct fish type: {catch.fish_type}"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            blocked = True

        # Guardrail 4: PII protection - no other buyer info
        if all_buyers:
            for other_buyer in all_buyers:
                if other_buyer.id != buyer.id:
                    # Check if other buyer's name or phone appears in text
                    if other_buyer.name in draft_text or other_buyer.phone in draft_text:
                        violation = self._create_violation(
                            guardrail="pii_protection",
                            severity="critical",
                            what_happened=f"Draft message contains PII of another buyer: {other_buyer.name}",
                            expected="Message must only contain info relevant to the recipient"
                        )
                        coaching = self.coach.coach_agent(violation)
                        violations.append(coaching)
                        blocked = True
                        break

        # Guardrail 5: Communication integrity - never auto-commit
        commitment_words = ["deal", "sold", "meet me", "pickup at", "final price", "agreed"]
        if any(word in draft_text.lower() for word in commitment_words):
            violation = self._create_violation(
                guardrail="communication_integrity",
                severity="high",
                what_happened="Draft message contains commitment language that should be handled by fisherman directly",
                expected="Messages should only inform about availability and price, not commit to deals"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            # Don't block, just warn

        # Guardrail 6: Financial accuracy - check if math is shown correctly
        # We expect the message to implicitly or explicitly convey the value
        # Since the prompt asks for "pounds" and "price per lb", we check if those numbers are present
        # We already checked for exact price and pounds strings above.
        # Here we check if there's a calculation that is WRONG.
        
        # Extract potential total prices (numbers preceded by $)
        potential_totals = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', draft_text)
        expected_total = catch.pounds * price.price_per_lb
        
        for total_str in potential_totals:
            try:
                val = float(total_str.replace(',', ''))
                # If it's not the price per lb, it might be the total
                if val != price.price_per_lb:
                    # Allow 1% margin of error for rounding
                    if abs(val - expected_total) > (expected_total * 0.01):
                        violation = self._create_violation(
                            guardrail="financial_accuracy",
                            severity="high",
                            what_happened=f"Draft message contains incorrect financial figure: ${val}",
                            expected=f"Total should be approximately ${expected_total:.2f} ({catch.pounds}lbs * ${price.price_per_lb})"
                        )
                        coaching = self.coach.coach_agent(violation)
                        violations.append(coaching)
                        blocked = True
            except ValueError:
                pass

        return {
            "blocked": blocked,
            "violations": violations
        }

    def _create_violation(
        self,
        guardrail: str,
        severity: str,
        what_happened: str,
        expected: str
    ) -> Dict[str, Any]:
        """Create a violation dict for coaching"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "guardrail": guardrail,
            "severity": severity,
            "what_happened": what_happened,
            "expected": expected,
            "context": {}
        }

    async def validate_catch_log(self, fish_type: str, pounds: float) -> Dict[str, Any]:
        """
        Validate catch log data before saving.
        """
        violations = []
        blocked = False

        # Validate fish type
        valid_fish_types = ["Crab", "Salmon", "Halibut", "Other"]
        if fish_type not in valid_fish_types:
            violation = self._create_violation(
                guardrail="data_integrity",
                severity="high",
                what_happened=f"Invalid fish type '{fish_type}'",
                expected=f"Must be one of: {', '.join(valid_fish_types)}"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            blocked = True

        # Validate pounds
        if pounds <= 0:
            violation = self._create_violation(
                guardrail="data_integrity",
                severity="high",
                what_happened=f"Invalid pounds value: {pounds}",
                expected="Pounds must be greater than 0"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            blocked = True

        if pounds > 10000:  # Sanity check
            violation = self._create_violation(
                guardrail="data_integrity",
                severity="medium",
                what_happened=f"Unusually high catch: {pounds} lbs",
                expected="Double-check if this amount is correct"
            )
            coaching = self.coach.coach_agent(violation)
            violations.append(coaching)
            # Don't block, just warn

        return {
            "blocked": blocked,
            "violations": violations
        }

    async def validate_data_access(self, user_authenticated: bool, resource: str) -> Dict[str, Any]:
        """
        Validate data access with Universal Coach.
        """
        if not user_authenticated:
            violation = self._create_violation(
                guardrail="data_access_control",
                severity="critical",
                what_happened=f"Unauthorized access attempt to {resource}",
                expected="User must be authenticated to access data"
            )
            coaching = self.coach.coach_agent(violation)
            return {
                "blocked": True,
                "violations": [coaching]
            }

        return {
            "blocked": False,
            "violations": []
        }
