from langchain_core.messages import HumanMessage

class UserPrompts:
    """Manages the generation of user prompts for various NLP tasks related to German grammar."""

    def __init__(self):
        """Initializes the UserPrompts class."""
        pass

    def get_user_query(self, text: str) -> HumanMessage:
        """Generates a user message from the given text.

        Args:
            text: The input text from the user.

        Returns:
            A HumanMessage object containing the user's text.
        """
        return HumanMessage(content=text)
