"""3-stage LLM Council orchestration."""

from typing import List, Dict, Any, Tuple
from openrouter import query_models_parallel, query_model
from config import COUNCIL_MODELS
from models import Role, ModelType
import requests

class Council() :

    def __init__(self) :

        self.models = COUNCIL_MODELS

        for model in self.models:
            model.pull()

            if model.model_type == ModelType.CUSTOM :
                model.create()
        
        self.chairman = self.models[0]
        self.models = self.models[1:]

        url = f"http://ollama:11434/api/tags"

        print(requests.get(url).json())

    async def stage1_collect_responses(self, user_query: str) -> List[Dict[str, Any]]:

    
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the user's request clearly and accurately. "
                    "Be concise but complete. If information is uncertain, say so."
                ),
            },
            {"role": "user", "content": user_query},
        ]

        # Appel parallèle des modèles
        responses = await query_models_parallel(self.models, messages)

        # Formatage des résultats
        stage1_results: List[Dict[str, Any]] = []
        for model_name, resp in (responses or {}).items():
            if resp is None:
                continue
            content = resp.get("content", "") if isinstance(resp, dict) else ""
            if content.strip():
                stage1_results.append({"model": model_name, "response": content})

        return stage1_results


    async def stage2_collect_rankings(
        self,
        user_query: str,
        stage1_results: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:

        # Create anonymized labels for responses (Response A, Response B, etc.)
        labels = [chr(65 + i) for i in range(len(stage1_results))]  # A, B, C, ...

        # Create mapping from label to model name
        label_to_model = {
            f"Response {label}": result['model']
            for label, result in zip(labels, stage1_results)
        }


        # Build the ranking prompt
        responses_text = "\n\n".join([
            f"Response {label}:\n{result['response']}"
            for label, result in zip(labels, stage1_results)
        ])

        ranking_prompt = f"""
            You are acting as a neutral evaluator.

            You are given a USER REQUEST and several ANONYMIZED RESPONSES.
            Your task is to objectively rank the responses from best to worst.

            USER REQUEST:
            {user_query}

            ANONYMIZED RESPONSES:
            {responses_text}

            Evaluation criteria (in order of importance):
            1. Accuracy – factual correctness, absence of hallucinations or false claims.
            2. Completeness – how well the response fully addresses the user request.
            3. Relevance – focus on the request without unnecessary or off-topic content.
            4. Clarity – clear structure, understandable reasoning, precise language.
            5. Usefulness – how actionable or helpful the response is to the user.

            Instructions:
            - Carefully read ALL responses before ranking.
            - Compare responses relative to each other, not against an ideal answer.
            - If two responses are similar, prefer the one that is more precise and less speculative.
            - Do NOT assume missing information; judge only what is written.

            Output format requirements (MANDATORY):
            - Provide ONLY the final ranking.
            - Do NOT include explanations, analysis, or commentary.
            - Use each response label exactly once.
            - Follow the exact format below.

            FORMAT OF FINAL RANKING:
            1. Response A
            2. Response B
            """


        messages = [{"role": "user", "content": ranking_prompt}]

        # Get rankings from all council models in parallel
        responses = await query_models_parallel(self.models, messages)

        # Format results
        stage2_results = []
        for model, response in responses.items():
            if response is not None:
                full_text = response.get('content', '')
                parsed = Council.parse_ranking_from_text(full_text)
                stage2_results.append({
                    "model": model,
                    "ranking": full_text,
                    "parsed_ranking": parsed
                })

        return stage2_results, label_to_model


    async def stage3_synthesize_final(
        self,
        user_query: str,
        stage1_results: List[Dict[str, Any]],
        stage2_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        # Build comprehensive context for chairman
        stage1_text = "\n\n".join([
            f"Model: {result['model']}\nResponse: {result['response']}"
            for result in stage1_results
        ])

        stage2_text = "\n\n".join([
            f"Model: {result['model']}\nRanking: {result['ranking']}"
            for result in stage2_results
        ])

        chairman_prompt = (
            "You are the Chairman of an LLM Council.\n"
            "Multiple models answered the user's request, then peer-reviewed and ranked those answers.\n\n"
            f"USER REQUEST:\n{user_query}\n\n"
            "STAGE 1 — INDIVIDUAL ANSWERS:\n"
            f"{stage1_text}\n\n"
            "STAGE 2 — PEER RANKINGS (JSON):\n"
            f"{stage2_text}\n\n"
            "Your task:\n"
            "- Produce a single best final answer to the user.\n"
            "- Incorporate correct points from the strongest answers.\n"
            "- Resolve contradictions by choosing the most plausible/standard interpretation.\n"
            "- Be clear, practical, and well-structured.\n"
        )

        messages = [{"role": "user", "content": chairman_prompt}]

        # Query the chairman model
        response = await query_model(self.chairman, messages)

        if response is None:
            # Fallback if chairman fails
            return {
                "model": self.chairman.model_name,
                "response": "Error: Impossible de générer la synthèse finale."
            }

        return {
            "model": self.chairman.model_name,
            "response": response.get('content', '')
        }


    def parse_ranking_from_text(ranking_text: str) -> List[str]:
        """
        Parse the FINAL RANKING section from the model's response.

        Args:
            ranking_text: The full text response from the model

        Returns:
            List of response labels in ranked order
        """
        import re

        # Look for "FINAL RANKING:" section
        if "FINAL RANKING:" in ranking_text:
            # Extract everything after "FINAL RANKING:"
            parts = ranking_text.split("FINAL RANKING:")
            if len(parts) >= 2:
                ranking_section = parts[1]
                # Try to extract numbered list format (e.g., "1. Response A")
                # This pattern looks for: number, period, optional space, "Response X"
                numbered_matches = re.findall(r'\d+\.\s*Response [A-Z]', ranking_section)
                if numbered_matches:
                    # Extract just the "Response X" part
                    return [re.search(r'Response [A-Z]', m).group() for m in numbered_matches]

                # Fallback: Extract all "Response X" patterns in order
                matches = re.findall(r'Response [A-Z]', ranking_section)
                return matches

        # Fallback: try to find any "Response X" patterns in order
        matches = re.findall(r'Response [A-Z]', ranking_text)
        return matches


    def calculate_aggregate_rankings(
        self,
        stage2_results: List[Dict[str, Any]],
        label_to_model: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        from collections import defaultdict
        """
        Calculate aggregate rankings across all models.

        Args:
            stage2_results: Rankings from each model
            label_to_model: Mapping from anonymous labels to model names

        Returns:
            List of dicts with model name and average rank, sorted best to worst
        """

        # Track positions for each model
        model_positions = defaultdict(list)

        for ranking in stage2_results:
            ranking_text = ranking['ranking']

            # Parse the ranking from the structured format
            parsed_ranking = Council.parse_ranking_from_text(ranking_text)

            for position, label in enumerate(parsed_ranking, start=1):
                if label in label_to_model:
                    model_name = label_to_model[label]
                    model_positions[model_name].append(position)

        # Calculate average position for each model
        aggregate = []
        for model, positions in model_positions.items():
            if positions:
                avg_rank = sum(positions) / len(positions)
                aggregate.append({
                    "model": model,
                    "average_rank": round(avg_rank, 2),
                    "rankings_count": len(positions)
                })

        # Sort by average rank (lower is better)
        aggregate.sort(key=lambda x: x['average_rank'])

        return aggregate


    async def generate_conversation_title(self, user_query: str) -> str:
        """
        Generate a short conversation title (3-5 words) reliably.
        Uses the chairman by default (already available), with a short prompt.
        """
        title_prompt = (
            "Generate a very short title (3 to 5 words maximum) summarizing the user's request.\n"
            "Constraints:\n"
            "- No quotes\n"
            "- No punctuation\n"
            "- No emojis\n"
            "- Use plain words\n\n"
            f"User request: {user_query}\n\n"
            "Title:"
        )

        messages = [{"role": "user", "content": title_prompt}]

        response = await query_model(self.chairman, messages, timeout=60.0)

        if response is None:
            return "New Conversation"

        title = (response.get("content") or "").strip()

        title = title.strip().strip('"').strip("'")

        # Collapse whitespace
        title = " ".join(title.split())

        # Hard fallback if model returns empty
        if not title:
            return "New Conversation"

        # Enforce max length
        if len(title) > 50:
            title = title[:47].rstrip() + "..."

        # If model still returned a full sentence, keep first ~5 words
        words = title.split()
        if len(words) > 6:
            title = " ".join(words[:5])

        return title



    async def run_full_council(self, user_query: str) -> Tuple[List, List, Dict, Dict]:
        import time
        
        # Stage 1: Collect individual responses
        stage1_start = time.time()
        stage1_results = await self.stage1_collect_responses(user_query)
        stage1_duration = time.time() - stage1_start

        # If no models responded successfully, return error
        if not stage1_results:
            return [], [], {
                "model": "error",
                "response": "Aucun modèle n'a réussi à répondre. Veuillez réessayer."
            }, {}

        # Stage 2: Collect rankings
        stage2_start = time.time()
        stage2_results, label_to_model = await self.stage2_collect_rankings(user_query, stage1_results)
        stage2_duration = time.time() - stage2_start

        # Calculate aggregate rankings
        aggregate_rankings = self.calculate_aggregate_rankings(stage2_results, label_to_model)

        # Stage 3: Synthesize final answer
        stage3_start = time.time()
        stage3_result = await self.stage3_synthesize_final(
            user_query,
            stage1_results,
            stage2_results
        )
        stage3_duration = time.time() - stage3_start

        # Prepare metadata
        metadata = {
            "label_to_model": label_to_model,
            "aggregate_rankings": aggregate_rankings,
            "timing": {
                "stage1_duration": round(stage1_duration, 2),
                "stage2_duration": round(stage2_duration, 2),
                "stage3_duration": round(stage3_duration, 2),
                "total_duration": round(stage1_duration + stage2_duration + stage3_duration, 2)
            }
        }

        return stage1_results, stage2_results, stage3_result, metadata
        
    
