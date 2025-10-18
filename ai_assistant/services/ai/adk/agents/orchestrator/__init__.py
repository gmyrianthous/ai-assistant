"""Orchestrator agent package - routes requests to appropriate sub-agents."""

from ai_assistant.services.ai.adk.agents.orchestrator.agent import orchestrator_agent as root_agent

__all__ = ['root_agent']
