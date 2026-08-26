"""Factories for building ADK objects used in tests."""

from google.adk.events import Event
from google.genai.types import Content as ADKContent
from google.genai.types import FunctionCall
from google.genai.types import Part


class ADKEventFactory:
    """Factory for ADK events emitted by agents during a run."""

    @staticmethod
    def with_text(text: str, author: str = 'test_agent', is_final: bool = False) -> Event:
        """
        Create an event carrying a text part.

        Args:
            text: The text content of the event.
            author: Agent name emitting the event.
            is_final: Whether the event is a final (non-partial) response.

        Returns:
            Event: The constructed ADK event.
        """
        return Event(
            author=author,
            content=ADKContent(role='model', parts=[Part(text=text)]),
            partial=not is_final,
        )

    @staticmethod
    def final_response(text: str, author: str = 'test_agent') -> Event:
        """
        Create a final (non-partial) response event with a text part.

        Args:
            text: The text content of the event.
            author: Agent name emitting the event.

        Returns:
            Event: The constructed ADK event, for which is_final_response() is True.
        """
        return Event(
            author=author,
            content=ADKContent(role='model', parts=[Part(text=text)]),
            partial=False,
        )

    @staticmethod
    def with_function_call(function_name: str, author: str = 'test_agent') -> Event:
        """
        Create an event carrying a function (tool) call part.

        Args:
            function_name: Name of the function being called.
            author: Agent name emitting the event.

        Returns:
            Event: The constructed ADK event.
        """
        return Event(
            author=author,
            content=ADKContent(
                role='model',
                parts=[Part(function_call=FunctionCall(name=function_name, args={}))],
            ),
        )
