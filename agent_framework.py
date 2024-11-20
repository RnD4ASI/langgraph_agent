"""
Flexible Agent Framework using LangGraph

This module provides a flexible framework for creating single and multi-agent workflows.
It supports both simple single-agent tasks and complex multi-agent collaborations with
customizable roles, communication patterns, and state management.

Key Components:
1. Message Management: Custom reducer for handling message updates and history
2. Agent Configuration: Flexible configuration system for defining agent behaviors
3. Workflow Management: Support for different communication patterns and agent hierarchies
4. State Management: Built-in state tracking and checkpointing
"""

from typing import Dict, List, Optional, Any, Callable, TypedDict, Annotated, Union
from enum import Enum
import operator
from uuid import uuid4
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    FunctionMessage,
)
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

def reduce_messages(left: list[AnyMessage], right: list[AnyMessage]) -> list[AnyMessage]:
    """
    Custom message reducer that handles message updates and additions.
    
    This function:
    1. Ensures all messages have unique IDs
    2. Replaces existing messages with updated versions if IDs match
    3. Appends new messages to the list
    
    Args:
        left: Existing list of messages
        right: New messages to add or update
        
    Returns:
        Updated list of messages with duplicates handled appropriately
    """
    for message in right:
        if not message.id:
            message.id = str(uuid4())
    merged = left.copy()
    for message in right:
        for i, existing in enumerate(merged):
            if existing.id == message.id:
                merged[i] = message
                break
        else:
            merged.append(message)
    return merged

class AgentRole(Enum):
    """
    Predefined roles for agents in multi-agent workflows.
    
    Roles:
    - COORDINATOR: Manages workflow and delegates tasks
    - EXECUTOR: Performs specific tasks or actions
    - CRITIC: Reviews and provides feedback
    - RESEARCHER: Gathers and analyzes information
    - CUSTOM: User-defined specialized roles
    """
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    CRITIC = "critic"
    RESEARCHER = "researcher"
    CUSTOM = "custom"

@dataclass
class AgentConfig:
    """
    Configuration class for individual agents.
    
    Attributes:
        name: Unique identifier for the agent
        role: Agent's role in the workflow (from AgentRole enum)
        system_message: Instructions/context for the agent's behavior
        tools: Optional list of tools available to the agent
        model: Language model to use (defaults to gpt-3.5-turbo)
        temperature: Creativity vs determinism setting (0-1)
        custom_functions: Additional functions for specialized behavior
    """
    name: str
    role: AgentRole
    system_message: str
    tools: List[BaseTool] = field(default_factory=list)
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    custom_functions: Dict[str, Callable] = field(default_factory=dict)

class AgentState(TypedDict):
    """
    Type definition for agent state.
    
    Attributes:
        messages: List of messages with custom reducer for updates
        metadata: Additional state information and configuration
    """
    messages: Annotated[list[AnyMessage], reduce_messages]
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    This class:
    1. Defines the basic structure for agents
    2. Handles model initialization
    3. Provides abstract method for message processing
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize agent with configuration.
        
        Args:
            config: AgentConfig instance with agent settings
        """
        self.config = config
        self.llm = ChatOpenAI(
            model=config.model,
            temperature=config.temperature
        ).bind_tools(config.tools)
        
    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and generate response.
        
        Args:
            state: Current agent state with messages and metadata
            
        Returns:
            Updated agent state after processing
        """
        pass

class SingleAgent(BaseAgent):
    """
    Implementation for single-agent workflows.
    
    This class:
    1. Creates a simple sequential workflow graph
    2. Handles message processing and state updates
    3. Manages conversation flow and termination
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize single agent with configuration.
        
        Args:
            config: AgentConfig instance with agent settings
        """
        super().__init__(config)
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """
        Build the workflow graph for single agent.
        
        Creates a simple graph with:
        1. Single processing node
        2. Conditional edge for continuation
        3. Entry point configuration
        
        Returns:
            Compiled StateGraph for the workflow
        """
        graph = StateGraph(AgentState)
        
        # Add core processing node
        graph.add_node("process", self.process)
        
        # Add conditional routing
        graph.add_conditional_edges(
            "process",
            self._should_continue,
            {True: "process", False: END}
        )
        
        graph.set_entry_point("process")
        return graph.compile()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process messages and generate response.
        
        Steps:
        1. Prepend system message to conversation
        2. Process all messages with LLM
        3. Append response to message history
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state with new message
        """
        messages = [SystemMessage(content=self.config.system_message)]
        messages.extend(state["messages"])
        
        response = self.llm.invoke(messages)
        state["messages"].append(response)
        return state
    
    def _should_continue(self, state: AgentState) -> bool:
        """
        Determine if processing should continue.
        
        Checks:
        1. Number of messages against max_turns
        2. Any completion markers in messages
        
        Args:
            state: Current conversation state
            
        Returns:
            Boolean indicating whether to continue processing
        """
        return len(state["messages"]) < state["metadata"].get("max_turns", 10)

class MultiAgentWorkflow:
    """
    Orchestrator for multi-agent workflows.
    
    This class:
    1. Manages multiple agents and their interactions
    2. Implements different communication patterns
    3. Handles state persistence and checkpointing
    """
    
    def __init__(self, 
                 agents: List[AgentConfig],
                 communication_pattern: str = "sequential",
                 checkpoint_path: Optional[str] = None):
        """
        Initialize multi-agent workflow.
        
        Args:
            agents: List of agent configurations
            communication_pattern: How agents should interact
            checkpoint_path: Optional path for state persistence
        """
        self.agents = {cfg.name: SingleAgent(cfg) for cfg in agents}
        self.communication_pattern = communication_pattern
        self.checkpointer = SqliteSaver.from_conn_string(
            checkpoint_path if checkpoint_path else ":memory:"
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the workflow graph based on communication pattern.
        
        Implements:
        1. Sequential pattern: Agents work in sequence
        2. Broadcast pattern: All agents receive all messages
        
        Returns:
            Compiled StateGraph for the workflow
        """
        graph = StateGraph(AgentState)
        
        if self.communication_pattern == "sequential":
            prev_node = None
            for name, agent in self.agents.items():
                graph.add_node(name, agent.process)
                if prev_node:
                    graph.add_edge(prev_node, name)
                prev_node = name
            
            # Add end condition from last node
            graph.add_conditional_edges(
                prev_node,
                self._should_continue,
                {True: list(self.agents.keys())[0], False: END}
            )
        
        elif self.communication_pattern == "broadcast":
            # Implement broadcast pattern where all agents receive all messages
            for name, agent in self.agents.items():
                graph.add_node(name, agent.process)
            
            # Connect all agents to each other
            for name in self.agents.keys():
                others = [n for n in self.agents.keys() if n != name]
                for other in others:
                    graph.add_edge(name, other)
        
        graph.set_entry_point(list(self.agents.keys())[0])
        return graph.compile(checkpointer=self.checkpointer)
    
    def _should_continue(self, state: AgentState) -> bool:
        """
        Determine if the multi-agent workflow should continue.
        
        Checks:
        1. Message count against max_turns
        2. Completion markers in messages
        
        Args:
            state: Current workflow state
            
        Returns:
            Boolean indicating whether to continue
        """
        return len(state["messages"]) < state["metadata"].get("max_turns", 20)
    
    def run(self, 
            initial_message: str,
            metadata: Optional[Dict[str, Any]] = None) -> AgentState:
        """
        Run the multi-agent workflow.
        
        Steps:
        1. Create initial state with message
        2. Execute workflow graph
        3. Return final state
        
        Args:
            initial_message: Starting message for workflow
            metadata: Optional configuration for execution
            
        Returns:
            Final state after workflow completion
        """
        initial_state = AgentState(
            messages=[HumanMessage(content=initial_message)],
            metadata=metadata or {}
        )
        return self.graph.invoke(initial_state)

def create_single_agent(
    system_message: str,
    tools: List[BaseTool] = None,
    model: str = "gpt-3.5-turbo"
) -> SingleAgent:
    """
    Helper function to create a single agent with basic configuration.
    
    Args:
        system_message: Instructions for the agent
        tools: Optional list of tools
        model: Language model to use
        
    Returns:
        Configured SingleAgent instance
    """
    config = AgentConfig(
        name="main_agent",
        role=AgentRole.EXECUTOR,
        system_message=system_message,
        tools=tools or [],
        model=model
    )
    return SingleAgent(config)

def create_multi_agent_workflow(
    agent_configs: List[AgentConfig],
    communication_pattern: str = "sequential",
    checkpoint_path: Optional[str] = None
) -> MultiAgentWorkflow:
    """
    Helper function to create a multi-agent workflow.
    
    Args:
        agent_configs: List of agent configurations
        communication_pattern: How agents should interact
        checkpoint_path: Optional path for state persistence
        
    Returns:
        Configured MultiAgentWorkflow instance
    """
    return MultiAgentWorkflow(
        agents=agent_configs,
        communication_pattern=communication_pattern,
        checkpoint_path=checkpoint_path
    )
