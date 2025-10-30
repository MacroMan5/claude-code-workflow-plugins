# Credits & Acknowledgments

LAZY_DEV Framework is built on the shoulders of giants. This project would not have been possible without the inspiration, patterns, and open-source contributions from the following projects and developers.

---

## Core Inspirations

### Claude Code Ecosystem

**Anthropic Claude Code**
- Official patterns for agents, hooks, and skills
- Documentation and best practices
- Website: https://docs.claude.com/claude-code
- License: Proprietary (Anthropic)

**Model Context Protocol (MCP)**
- Memory persistence protocol
- Cross-session knowledge management
- Repository: https://github.com/modelcontextprotocol/servers
- Package: `@modelcontextprotocol/server-memory`
- License: MIT

---

## PROJECT_INSPIRATION Sources

### 1. Claude Code Hooks Mastery
**Author**: IndyDevDan (disler)
- YouTube: [@indydevdan](https://youtube.com/@indydevdan)
- Course: [Principles of AI Coding](https://agenticengineer.com/principled-ai-coding)

**Patterns Borrowed**:
- Hook system architecture (UserPromptSubmit, PreToolUse, PostToolUse, Stop)
- UV single-file script patterns
- TTS integration patterns
- Event-driven automation

**License**: MIT (assumed from GitHub patterns)

---

### 2. Claude Code Multi-Agent Observability
**Author**: IndyDevDan (disler)
- YouTube: [@indydevdan](https://youtube.com/@indydevdan)
- Videos:
  - https://youtu.be/9ijnN985O_c
  - https://youtu.be/aA9KP7QIQvM
- Course: [Tactical Agentic Coding](https://agenticengineer.com/tactical-agentic-coding)

**Patterns Borrowed**:
- Event streaming architecture
- Multi-agent observability patterns
- Hook-to-WebSocket pipeline
- Real-time event visualization

**License**: MIT

---

### 3. Big 3 Super Agent
**Author**: IndyDevDan
- YouTube: [Demo Video](https://youtu.be/Ur3TJm0BckQ)
- Course: [Tactical Agentic Coding](https://agenticengineer.com/tactical-agentic-coding)

**Patterns Borrowed**:
- Multi-agent orchestration (Voice + Claude Code + Gemini)
- Voice-controlled agent coordination
- Git worktree-based agent sessions
- Parallel agent execution

**License**: MIT

---

### 4. Claude Code Sub-Agent Collective
**Author**: vanzan01
- GitHub: [claude-code-sub-agent-collective](https://github.com/vanzan01/claude-code-sub-agent-collective)
- NPM Package: `claude-code-collective`

**Patterns Borrowed**:
- TDD-enforced agent system
- Hub-and-spoke routing architecture
- NPX-based installation framework
- Contract validation for agent handoffs

**License**: MIT

---

### 5. Every Marketplace
**Author**: EveryInc
- GitHub: [@EveryInc](https://github.com/EveryInc)
- NPM Package: `@EveryInc/every-marketplace`
- Article: [Compounding Engineering Story](https://every.to/source-code/my-ai-had-already-fixed-the-code-before-i-saw-it)

**Patterns Borrowed**:
- Plugin marketplace structure
- Compounding engineering philosophy
- Multi-agent code review system
- Quality gate automation

**License**: MIT

---

### 6. RealtimeSTT (Voice Interface)
**Author**: Kolja Beigel (KoljaB)
- GitHub: [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT)
- PyPI Package: `RealtimeSTT`
- Email: kolja.beigel@web.de

**Patterns Borrowed**:
- Real-time speech-to-text pipeline
- Voice activity detection (WebRTC + Silero VAD)
- Wake word detection
- Audio streaming architecture

**Related Project**: [Linguflex](https://github.com/KoljaB/Linguflex)

**License**: MIT

---

### 7. Faster Whisper
**Author**: SYSTRAN
- GitHub: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- PyPI Package: `faster-whisper`

**Patterns Borrowed**:
- Fast Whisper transcription with CTranslate2
- GPU-accelerated speech-to-text
- Batched inference pipeline

**License**: MIT

---

### 8. Always-On AI Assistant
**Author**: Unknown (community project)
- YouTube Demo: https://youtu.be/zoBwIi4ZiTA

**Patterns Borrowed**:
- Voice interface integration with RealtimeSTT
- Wake word detection patterns
- Typer command framework

**License**: MIT (assumed)

---

## Open Source Dependencies

### Python Packages
- **black** - Code formatting
- **ruff** - Fast linting and formatting
- **mypy** - Static type checking
- **pytest** - Testing framework
- **pytest-cov** - Test coverage
- **typer** - CLI framework (for STT enhancer)
- **rich** - Terminal formatting
- **anthropic** - Claude API client

### Node.js Packages
- **@modelcontextprotocol/server-memory** - MCP Memory server

### System Tools
- **gh** (GitHub CLI) - PR creation and GitHub integration
- **git** - Version control
- **uv** - Python package manager

---

## Special Thanks

### Community & Educators

**IndyDevDan / disler**
- For pioneering Claude Code hooks, multi-agent observability, and providing comprehensive courses on agentic engineering
- Multiple reference implementations that shaped LAZY_DEV's architecture

**vanzan01**
- For the TDD-first agent collective pattern that inspired our quality pipeline

**Kolja Beigel (KoljaB)**
- For RealtimeSTT library that enables voice-to-prompt functionality

**EveryInc Team**
- For the compounding engineering philosophy and marketplace patterns

**SYSTRAN**
- For Faster Whisper that enables efficient speech processing

**Anthropic**
- For Claude Code, Claude API, and excellent documentation

---

## Philosophy & Approach

LAZY_DEV synthesizes patterns from all these sources into a cohesive framework:

1. **Hooks** (from claude-code-hooks-mastery) → Safety, automation, enrichment
2. **Multi-Agent** (from big-3-super-agent, sub-agent-collective) → Specialized agents with TDD
3. **Quality Gates** (from every-marketplace) → Fail-fast pipelines
4. **Voice Interface** (from RealtimeSTT, faster-whisper) → Voice-to-prompt enhancement
5. **Memory Persistence** (from MCP) → Cross-session knowledge graph
6. **Observability** (from multi-agent-observability) → Event logging and metrics

---

## License

LAZY_DEV Framework is released under the **MIT License**.

All credited projects above use compatible open-source licenses (primarily MIT).

---

## Contributing

If you see your work referenced here and would like:
- Additional attribution
- Corrections to credits
- Link updates
- Removal of references

Please open an issue at: https://github.com/MacroMan5/claude-code-workflow-plugins/issues

---

**LAZY_DEV** - Standing on the shoulders of giants 🚀

Built with inspiration from the Claude Code community.
