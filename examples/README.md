# LangGraph Agent Framework Examples

This directory contains example implementations that demonstrate different use cases of the LangGraph Agent Framework. Each example showcases specific features and capabilities of the framework.

## Overview

1. [Research Assistant](#research-assistant) - Single-agent web research workflow
2. [Code Review System](#code-review-system) - Multi-agent code analysis workflow
3. [Creative Writing System](#creative-writing-system) - Multi-agent collaborative writing workflow

## Research Assistant

**File**: `research_assistant.py`

A single-agent implementation that helps users research topics using web search and content analysis.

### Features
- Web search using DuckDuckGo
- Webpage content scraping and analysis
- Information synthesis and summarization
- Source citation

### Components
1. **Tools**:
   - `web_search`: DuckDuckGo-based search tool
   - `scrape_webpage`: Content extraction tool

2. **Agent Configuration**:
   ```python
   agent = create_single_agent(
       system_message=system_message,
       tools=[search_tool, scrape_tool],
       model="gpt-3.5-turbo"
   )
   ```

3. **Workflow**:
   1. Receive research question
   2. Search web for relevant information
   3. Scrape and analyze content
   4. Synthesize findings
   5. Present summary with citations

### Usage
```bash
python research_assistant.py
```

Choose from preset questions or enter your own research topic.

## Code Review System

**File**: `code_review.py`

A multi-agent system that performs comprehensive code reviews with specialized reviewers.

### Features
- AST-based code analysis
- Multiple specialized reviewers
- Coordinated review process
- Detailed feedback compilation

### Components
1. **Agents**:
   - **Coordinator**: Manages review process
   - **Style Reviewer**: Checks code style and best practices
   - **Security Reviewer**: Analyzes security and performance

2. **Code Analysis Tool**:
   ```python
   class CodeAnalysisTool:
       @staticmethod
       def analyze_code(code: str) -> Dict[str, any]:
           # Analyzes Python code using AST
           # Returns metrics about functions, classes, complexity
   ```

3. **Workflow**:
   1. Code analysis
   2. Distribution to reviewers
   3. Specialized reviews
   4. Feedback synthesis

### Usage
```bash
python code_review.py
```

The system will analyze the provided code sample and generate a comprehensive review.

## Creative Writing System

**File**: `creative_writing.py`

A multi-agent collaborative writing system with specialized roles for different aspects of story creation.

### Features
- Genre-specific prompts
- Character development
- Scene crafting
- Editorial review
- Collaborative storytelling

### Components
1. **Agents**:
   - **Coordinator**: Lead writer managing story development
   - **Character Writer**: Character development specialist
   - **Scene Writer**: Setting and action specialist
   - **Editor**: Review and refinement specialist

2. **Genre Support**:
   ```python
   genres = ["fantasy", "scifi", "mystery", "romance", "general"]
   ```

3. **Workflow**:
   1. Genre and prompt selection
   2. Story outline development
   3. Character and scene creation
   4. Editorial review
   5. Final story compilation

### Usage
```bash
python creative_writing.py
```

Select a genre and let the system generate a collaborative story.

## Best Practices for Using Examples

1. **Configuration**:
   - Set up OpenAI API key in `.env` file
   - Install required dependencies
   - Adjust model parameters as needed

2. **Customization**:
   - Modify system messages for different behaviors
   - Add or remove tools as needed
   - Adjust workflow patterns

3. **Extension**:
   - Use these examples as templates
   - Combine features from different examples
   - Create new specialized agents

## Common Patterns

1. **Agent Configuration**:
   ```python
   config = AgentConfig(
       name="agent_name",
       role=AgentRole.ROLE_TYPE,
       system_message="Instructions",
       tools=optional_tools
   )
   ```

2. **Workflow Creation**:
   ```python
   workflow = create_multi_agent_workflow(
       agent_configs=agents,
       communication_pattern="sequential"
   )
   ```

3. **Execution**:
   ```python
   result = workflow.run(
       initial_message="Task description",
       metadata={"max_turns": N}
   )
   ```

## Error Handling

Each example includes error handling for common issues:
- API failures
- Tool execution errors
- Invalid inputs
- Resource limitations

## Performance Considerations

1. **Memory Usage**:
   - Message history management
   - State checkpointing
   - Content length limits

2. **API Costs**:
   - Efficient tool usage
   - Appropriate model selection
   - Turn limit configuration

3. **Execution Time**:
   - Concurrent operations where possible
   - Efficient communication patterns
   - Appropriate timeout settings

## Contributing

Feel free to:
1. Add new examples
2. Improve existing implementations
3. Extend tool capabilities
4. Enhance documentation

## License

MIT License - See main project license for details.
