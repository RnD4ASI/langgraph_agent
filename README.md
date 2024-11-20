# LangGraph Agent Framework

A flexible framework for creating single and multi-agent workflows using LangGraph. This framework allows you to create customizable agent workflows for various applications, from simple single-agent tasks to complex multi-agent collaborations.

## Features

- Support for both single-agent and multi-agent workflows
- Customizable agent roles and hierarchies
- Flexible communication patterns between agents
- Built-in state management and checkpointing
- Easy-to-use configuration system
- Example implementations for common use cases

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Framework Structure

- `agent_framework.py`: Core framework implementation
- `examples/`: Example implementations
  - `research_assistant.py`: Web research assistant using DuckDuckGo
  - `code_review.py`: Multi-agent code review system
  - `creative_writing.py`: Collaborative story writing system

## Usage

### Single Agent Workflow

```python
from agent_framework import create_single_agent

# Create a single agent
agent = create_single_agent(
    system_message="Your system message here",
    tools=[],  # Optional tools
    model="gpt-3.5-turbo"  # Optional model specification
)

# Run the agent
result = agent.graph.invoke({
    "messages": [HumanMessage(content="Your message here")],
    "metadata": {"max_turns": 5}
})
```

### Multi-Agent Workflow

```python
from agent_framework import AgentConfig, AgentRole, create_multi_agent_workflow

# Create agent configurations
agents = [
    AgentConfig(
        name="coordinator",
        role=AgentRole.COORDINATOR,
        system_message="Coordinator system message"
    ),
    AgentConfig(
        name="executor",
        role=AgentRole.EXECUTOR,
        system_message="Executor system message"
    )
]

# Create workflow
workflow = create_multi_agent_workflow(
    agent_configs=agents,
    communication_pattern="sequential"  # or "broadcast"
)

# Run workflow
result = workflow.run(
    initial_message="Your task description",
    metadata={"max_turns": 10}
)
```

## Example Applications

### 1. Research Assistant
Run: `python examples/research_assistant.py`
- Web search and information gathering
- Content analysis and summarization
- Source citation

### 2. Code Review System
Run: `python examples/code_review.py`
- Multi-agent code analysis
- Style and best practices review
- Security and performance review
- Coordinated feedback compilation

### 3. Creative Writing System
Run: `python examples/creative_writing.py`
- Collaborative story development
- Character and scene specialization
- Editorial review and refinement
- Genre-specific writing

## Customization

### Adding New Agent Roles

1. Define a new role in `AgentRole` enum
2. Create appropriate system messages
3. Configure tools and functions as needed
4. Create agent configuration

### Modifying Communication Patterns

The framework supports different communication patterns:
- Sequential: Agents work in sequence
- Broadcast: All agents receive all messages

Custom patterns can be implemented by modifying the graph structure in `MultiAgentWorkflow._build_graph()`.

## Best Practices

1. Keep system messages clear and focused
2. Use appropriate tools for specific tasks
3. Configure reasonable turn limits
4. Implement proper error handling
5. Use checkpointing for long-running workflows

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements and bug fixes.

## License

MIT License
