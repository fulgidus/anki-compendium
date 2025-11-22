"""
Custom Anki card generation using genanki (Stage 8 - NO LangChain).
"""
import random
from typing import Any

import genanki


class AnkiCardGenerator:
    """Generate Anki flashcard decks from Q&A pairs using genanki."""

    def __init__(
        self,
        deck_name: str = "Generated Deck",
        deck_description: str = "",
        model_name: str = "Basic Model",
    ):
        """
        Initialize Anki card generator.

        Args:
            deck_name: Name of the Anki deck
            deck_description: Deck description
            model_name: Name of the note model/template
        """
        self.deck_name = deck_name
        self.deck_description = deck_description
        self.model_name = model_name

        # Generate unique IDs (required by genanki)
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.model_id = random.randrange(1 << 30, 1 << 31)

        # Create Anki model (card template)
        self.model = self._create_model()

        # Create Anki deck
        self.deck = genanki.Deck(
            deck_id=self.deck_id,
            name=self.deck_name,
            description=self.deck_description,
        )

    def _create_model(self) -> genanki.Model:
        """
        Create an Anki note model with front/back template.

        Returns:
            genanki Model with fields and card template
        """
        return genanki.Model(
            model_id=self.model_id,
            name=self.model_name,
            fields=[
                {"name": "Question"},
                {"name": "Answer"},
                {"name": "Context"},
                {"name": "Explanation"},
                {"name": "Difficulty"},
                {"name": "Source"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": """
<div class="card-front">
  <div class="question">{{Question}}</div>
  {{#Context}}
  <div class="context">Context: {{Context}}</div>
  {{/Context}}
</div>
""",
                    "afmt": """
<div class="card-back">
  <div class="question">{{Question}}</div>
  <hr id="answer">
  <div class="answer">{{Answer}}</div>
  {{#Explanation}}
  <div class="explanation">
    <strong>Explanation:</strong> {{Explanation}}
  </div>
  {{/Explanation}}
  {{#Difficulty}}
  <div class="difficulty">Difficulty: {{Difficulty}}</div>
  {{/Difficulty}}
  {{#Source}}
  <div class="source">Source: {{Source}}</div>
  {{/Source}}
</div>
""",
                }
            ],
            css="""
.card {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #333;
  background-color: #fff;
  padding: 20px;
}

.card-front, .card-back {
  max-width: 800px;
  margin: 0 auto;
}

.question {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #2c3e50;
}

.context {
  font-size: 16px;
  font-style: italic;
  color: #7f8c8d;
  margin-top: 10px;
  padding: 10px;
  background-color: #ecf0f1;
  border-radius: 5px;
}

.answer {
  font-size: 20px;
  margin: 20px 0;
  color: #27ae60;
  line-height: 1.6;
}

.explanation {
  font-size: 16px;
  color: #555;
  margin-top: 15px;
  padding: 10px;
  background-color: #f9f9f9;
  border-left: 4px solid #3498db;
  text-align: left;
}

.difficulty {
  font-size: 14px;
  color: #95a5a6;
  margin-top: 10px;
}

.source {
  font-size: 12px;
  color: #bdc3c7;
  margin-top: 10px;
  font-style: italic;
}

hr#answer {
  border: none;
  border-top: 2px solid #ecf0f1;
  margin: 20px 0;
}
""",
        )

    def add_card(
        self,
        question: str,
        answer: str,
        context: str = "",
        explanation: str = "",
        difficulty: str = "",
        source: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """
        Add a flashcard to the deck.

        Args:
            question: Question text
            answer: Answer text
            context: Additional context for the question
            explanation: Explanation of the answer
            difficulty: Difficulty level (easy, medium, hard)
            source: Source document or page
            tags: List of Anki tags
        """
        note = genanki.Note(
            model=self.model,
            fields=[question, answer, context, explanation, difficulty, source],
            tags=tags or [],
        )
        self.deck.add_note(note)

    def add_cards_from_qa_pairs(
        self,
        qa_pairs: list[dict[str, Any]],
        tags: list[str] | None = None,
        source: str = "",
    ) -> None:
        """
        Add multiple flashcards from Q&A pair dictionaries.

        Args:
            qa_pairs: List of Q&A dictionaries with keys:
                - question (required)
                - answer (required)
                - context (optional)
                - explanation (optional)
                - difficulty (optional)
            tags: Default tags for all cards
            source: Default source for all cards
        """
        for qa in qa_pairs:
            self.add_card(
                question=qa.get("question", ""),
                answer=qa.get("answer", ""),
                context=qa.get("context", ""),
                explanation=qa.get("explanation", ""),
                difficulty=qa.get("difficulty", qa.get("difficulty_rating", "")),
                source=source,
                tags=tags or [],
            )

    def export_to_file(self, output_path: str) -> None:
        """
        Export the deck to an .apkg file.

        Args:
            output_path: Path to save the .apkg file
        """
        package = genanki.Package(self.deck)
        package.write_to_file(output_path)

    def get_card_count(self) -> int:
        """
        Get the number of cards in the deck.

        Returns:
            Number of notes/cards in the deck
        """
        return len(self.deck.notes)


def create_anki_deck(
    qa_pairs: list[dict[str, Any]],
    deck_name: str = "Generated Deck",
    tags: list[str] | None = None,
    source: str = "",
    output_path: str = "output.apkg",
) -> str:
    """
    High-level function to create an Anki deck from Q&A pairs.

    Args:
        qa_pairs: List of Q&A dictionaries
        deck_name: Name of the Anki deck
        tags: Tags to apply to all cards
        source: Source document identifier
        output_path: Output .apkg file path

    Returns:
        Path to the generated .apkg file
    """
    generator = AnkiCardGenerator(deck_name=deck_name)
    generator.add_cards_from_qa_pairs(qa_pairs, tags=tags, source=source)
    generator.export_to_file(output_path)

    return output_path
