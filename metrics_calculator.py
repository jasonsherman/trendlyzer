import re


class MetricsCalculator:
    def __init__(self):
        pass

    def calculate_metrics(self, text):
        """
        Calculate various metrics from the text

        Args:
            text (str): Input text to analyze

        Returns:
            dict: Dictionary containing various metrics
        """
        # Basic text metrics
        word_count = len(text.split())
        line_count = len(text.splitlines())

        # Conversation detection
        total_conversations = self._count_conversations(text)

        # Determine if document is conversational
        is_conversational = total_conversations > 0

        return {
            "word_count": word_count,
            "line_count": line_count,
            "total_conversations": total_conversations,
            "mode": "Conversational Document" if is_conversational else "Normal Document"
        }

    def _count_conversations(self, text):
        """
        Count the number of conversations in the text

        Args:
            text (str): Input text to analyze

        Returns:
            int: Number of conversations detected
        """
        # Look for common conversation patterns
        patterns = [
            r'Q:\s*',  # Questions
            r'A:\s*',  # Answers
            r'Customer:\s*',  # Customer messages
            r'Agent:\s*',  # Agent messages
            r'User:\s*',  # User messages
            r'Support:\s*'  # Support messages
        ]

        total = 0
        for pattern in patterns:
            total += len(re.findall(pattern, text, re.IGNORECASE))

        return total
