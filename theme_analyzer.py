class ThemeAnalyzer:
    def __init__(self):
        # Define common themes and their keywords
        self.themes = {
            "Lead Capture": ["lead", "contact", "sign up", "register", "subscribe"],
            "Customer Support": ["support", "help", "service", "assistance", "customer"],
            "Sales": ["sale", "price", "cost", "discount", "offer"],
            "Product": ["product", "feature", "specification", "function", "capability"],
            "Marketing": ["marketing", "campaign", "promotion", "advertisement", "brand"],
            "Technical": ["technical", "spec", "requirement", "implementation", "system"]
        }

    def analyze_themes(self, text):
        """
        Analyze text for common themes based on keyword matching

        Args:
            text (str): Input text to analyze

        Returns:
            dict: Dictionary containing theme counts
        """
        text = text.lower()
        theme_counts = {theme: 0 for theme in self.themes.keys()}

        for theme, keywords in self.themes.items():
            for keyword in keywords:
                theme_counts[theme] += text.count(keyword.lower())

        return theme_counts
