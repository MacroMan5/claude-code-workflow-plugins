---
description: Initialize new project with comprehensive documentation (overview, specs, tech stack, architecture)
argument-hint: "[project-description] [--file FILE] [--minimal] [--no-sync] [--no-arch]"
allowed-tools: Read, Write, Bash, Skill, Glob
model: claude-sonnet-4-5-20250929
---

# Init Project: Bootstrap Project Foundation

## Introduction

Transform a project idea into complete foundational documentation including project overview, technical specifications, technology stack selection, and system architecture design.

**Purpose**: Create the documentation foundation before writing any code - ensures alignment, reduces rework, and provides clear technical direction.

**Output Structure:**
```
./project-management/
├── PROJECT-OVERVIEW.md      # Vision, goals, features, success criteria
├── SPECIFICATIONS.md        # Functional/non-functional requirements, API contracts, data models
├── TECH-STACK.md           # Technology selections with rationale and trade-offs
├── ARCHITECTURE.md         # System design with mermaid diagrams
└── .meta/
    └── last-sync.json      # Tracking metadata for document sync
```

**Integration**: Generated documents serve as input for `/lazy plan` when creating user stories.

---

## When to Use

**Use `/lazy init-project` when:**
- Starting a brand new greenfield project
- Need structured project documentation before coding
- Want technology stack guidance and architecture design
- Transitioning from idea to implementation
- Building POC/MVP and need technical foundation

**Skip this command when:**
- Project already has established documentation
- Working on existing codebase
- Only need single user story (use `/lazy plan` directly)
- Quick prototype without formal planning

---

## Usage Examples

```bash
# From project description
/lazy init-project "Build a real-time task management platform with AI prioritization"

# From enhanced prompt file (recommended)
/lazy init-project --file enhanced_prompt.md

# Minimal mode (skip architecture, faster)
/lazy init-project "E-commerce marketplace" --minimal

# Skip architecture generation
/lazy init-project "API service" --no-arch

# Disable auto-sync tracking
/lazy init-project "Chat app" --no-sync
```

---

## Requirements

### Prerequisites
- Working directory is project root
- Git repository initialized (recommended)
- PROJECT-OVERVIEW.md should not already exist (will be overwritten)

### Input Requirements
- **Project description** (required): Either inline text or file path via `--file`
- **Sufficient detail**: Mention key features, tech preferences, scale expectations
- **Clear goals**: What problem does this solve?

### Optional Flags
- `--file FILE`: Read project description from file (STT enhanced prompt recommended)
- `--minimal`: Generate only PROJECT-OVERVIEW.md and SPECIFICATIONS.md (skip tech stack and architecture)
- `--no-arch`: Generate overview, specs, and tech stack but skip architecture diagrams
- `--no-sync`: Skip creating `.meta/last-sync.json` tracking file

---

## Execution

### Step 1: Parse Arguments and Load Project Description

**Parse flags:**
```python
args = parse_arguments("$ARGUMENTS")

# Extract flags
file_path = args.get("--file")
minimal_mode = "--minimal" in args
skip_arch = "--no-arch" in args
disable_sync = "--no-sync" in args

# Get project description
if file_path:
    # Read from file
    project_description = read_file(file_path)
    if not project_description:
        return error(f"File not found or empty: {file_path}")
else:
    # Use inline description
    project_description = remove_flags(args)
    if not project_description.strip():
        return error("No project description provided. Use inline text or --file FILE")
```

**Validation:**
- Project description must be non-empty
- If `--file` used, file must exist and be readable
- Minimum 50 characters for meaningful planning (warn if less)

---

### Step 2: Create Project Management Directory

**Setup directory structure:**
```bash
# Create base directory
mkdir -p ./project-management/.meta

# Check if PROJECT-OVERVIEW.md exists
if [ -f "./project-management/PROJECT-OVERVIEW.md" ]; then
    echo "Warning: PROJECT-OVERVIEW.md already exists and will be overwritten"
fi
```

**Output location**: Always `./project-management/` relative to current working directory.

---

### Step 3: Invoke Project Planner Skill

**Generate overview and specifications:**

```python
# Invoke project-planner skill
result = Skill(
    command="project-planner",
    context={
        "description": project_description,
        "output_dir": "./project-management/"
    }
)

# Skill generates:
# - PROJECT-OVERVIEW.md (vision, goals, features, constraints)
# - SPECIFICATIONS.md (requirements, API contracts, data models)

# Verify both files were created
assert exists("./project-management/PROJECT-OVERVIEW.md"), "PROJECT-OVERVIEW.md not created"
assert exists("./project-management/SPECIFICATIONS.md"), "SPECIFICATIONS.md not created"
```

**What project-planner does:**
1. Extracts project context (name, features, goals, constraints)
2. Generates PROJECT-OVERVIEW.md with vision and high-level features
3. Generates SPECIFICATIONS.md with detailed technical requirements
4. Validates completeness of both documents

**Expected output:**
- `PROJECT-OVERVIEW.md`: 2-3KB, executive summary format
- `SPECIFICATIONS.md`: 8-15KB, comprehensive technical details

---

### Step 4: Invoke Tech Stack Architect Skill (unless --minimal or --no-arch)

**Generate technology stack selection:**

```python
# Skip if minimal mode or no-arch flag
if not minimal_mode:
    # Read PROJECT-OVERVIEW.md for context
    overview_content = read_file("./project-management/PROJECT-OVERVIEW.md")

    # Invoke tech-stack-architect skill
    result = Skill(
        command="tech-stack-architect",
        context={
            "project_overview": overview_content,
            "specifications": read_file("./project-management/SPECIFICATIONS.md"),
            "output_dir": "./project-management/",
            "skip_architecture": skip_arch  # Only generate TECH-STACK.md if true
        }
    )

    # Skill generates:
    # - TECH-STACK.md (frontend, backend, database, DevOps choices with rationale)
    # - ARCHITECTURE.md (system design with mermaid diagrams) [unless skip_arch]

    # Verify tech stack file created
    assert exists("./project-management/TECH-STACK.md"), "TECH-STACK.md not created"

    if not skip_arch:
        assert exists("./project-management/ARCHITECTURE.md"), "ARCHITECTURE.md not created"
```

**What tech-stack-architect does:**
1. Reads PROJECT-OVERVIEW.md for requirements and constraints
2. Analyzes technology needs across 4 categories: Frontend, Backend, Database, DevOps
3. Generates TECH-STACK.md with choices, rationale, alternatives, trade-offs
4. Designs system architecture with component diagrams
5. Generates ARCHITECTURE.md with mermaid diagrams for structure, data flow, deployment

**Expected output:**
- `TECH-STACK.md`: 5-8KB, table-based technology selections
- `ARCHITECTURE.md`: 10-15KB, system design with 3-5 mermaid diagrams

---

### Step 5: Create Tracking Metadata (unless --no-sync)

**Generate sync tracking file:**

```python
if not disable_sync:
    metadata = {
        "initialized_at": datetime.now().isoformat(),
        "documents": {
            "PROJECT-OVERVIEW.md": {
                "created": datetime.now().isoformat(),
                "size_bytes": file_size("./project-management/PROJECT-OVERVIEW.md"),
                "checksum": sha256("./project-management/PROJECT-OVERVIEW.md")
            },
            "SPECIFICATIONS.md": {
                "created": datetime.now().isoformat(),
                "size_bytes": file_size("./project-management/SPECIFICATIONS.md"),
                "checksum": sha256("./project-management/SPECIFICATIONS.md")
            },
            "TECH-STACK.md": {
                "created": datetime.now().isoformat(),
                "size_bytes": file_size("./project-management/TECH-STACK.md"),
                "checksum": sha256("./project-management/TECH-STACK.md")
            } if not minimal_mode else None,
            "ARCHITECTURE.md": {
                "created": datetime.now().isoformat(),
                "size_bytes": file_size("./project-management/ARCHITECTURE.md"),
                "checksum": sha256("./project-management/ARCHITECTURE.md")
            } if not minimal_mode and not skip_arch else None
        },
        "flags": {
            "minimal": minimal_mode,
            "skip_architecture": skip_arch
        }
    }

    # Write metadata
    write_json("./project-management/.meta/last-sync.json", metadata)
```

**Purpose of tracking:**
- Detect manual changes to generated files
- Support future re-sync or update operations
- Track generation history

---

### Step 6: Git Add (if in repository)

**Stage generated files:**

```bash
# Check if in git repo
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Add all generated files
    git add ./project-management/PROJECT-OVERVIEW.md
    git add ./project-management/SPECIFICATIONS.md

    if [ "$minimal_mode" = false ]; then
        git add ./project-management/TECH-STACK.md
        [ "$skip_arch" = false ] && git add ./project-management/ARCHITECTURE.md
    fi

    [ "$disable_sync" = false ] && git add ./project-management/.meta/last-sync.json

    echo "✓ Files staged for commit (git add)"
    echo "Note: Review files before committing"
else
    echo "Not a git repository - skipping git add"
fi
```

**Important**: Files are staged but NOT committed. User should review before committing.

---

### Step 7: Output Summary

**Display comprehensive summary:**

```markdown
## Project Initialization Complete

**Project Name**: {extracted from PROJECT-OVERVIEW.md}

**Documents Generated**:

1. ✅ **PROJECT-OVERVIEW.md** ({size}KB)
   - Vision and goals defined
   - {N} key features identified
   - {N} success criteria established
   - Constraints and scope documented

2. ✅ **SPECIFICATIONS.md** ({size}KB)
   - {N} functional requirements detailed
   - Non-functional requirements defined
   - {N} API endpoints documented (if applicable)
   - {N} data models specified
   - Development phases outlined

{if not minimal_mode:}
3. ✅ **TECH-STACK.md** ({size}KB)
   - Frontend stack selected: {tech}
   - Backend stack selected: {tech}
   - Database choices: {tech}
   - DevOps infrastructure: {tech}
   - Trade-offs and migration path documented

{if not skip_arch:}
4. ✅ **ARCHITECTURE.md** ({size}KB)
   - System architecture designed
   - {N} component diagrams included
   - Data flow documented
   - Security architecture defined
   - Scalability strategy outlined

{if not disable_sync:}
5. ✅ **Tracking metadata** (.meta/last-sync.json)
   - Document checksums recorded
   - Sync tracking enabled

**Location**: `./project-management/`

**Next Steps**:

1. **Review Documentation** (~15-20 minutes)
   - Read PROJECT-OVERVIEW.md for accuracy
   - Verify SPECIFICATIONS.md completeness
   - Check TECH-STACK.md technology choices
   - Review ARCHITECTURE.md diagrams

2. **Customize** (Optional)
   - Refine goals and success criteria
   - Add missing requirements
   - Adjust technology choices if needed
   - Enhance architecture diagrams

3. **Commit Initial Docs**
   ```bash
   git commit -m "docs: initialize project documentation

   - Add PROJECT-OVERVIEW.md with vision and goals
   - Add SPECIFICATIONS.md with technical requirements
   - Add TECH-STACK.md with technology selections
   - Add ARCHITECTURE.md with system design

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

4. **Start Planning User Stories**
   ```bash
   # Create first user story from specifications
   /lazy plan "Implement user authentication system"

   # Or plan from specific requirement
   /lazy plan --file ./project-management/SPECIFICATIONS.md --section "Authentication"
   ```

5. **Begin Implementation**
   ```bash
   # After creating user story
   /lazy code @US-1.1.md
   ```

**Estimated Time to Review/Customize**: 15-30 minutes

**Documentation Size**: {total}KB across {N} files

---

## Tips for Success

**Review Phase:**
- Don't skip the review - these docs guide all future development
- Check if technology choices match team skills
- Verify success criteria are measurable
- Ensure API contracts match business requirements

**Customization:**
- Feel free to edit generated docs manually
- Add project-specific constraints or requirements
- Refine architecture based on team preferences
- Update specs as you learn more

**Next Phase:**
- Use generated docs as input to `/lazy plan`
- Reference TECH-STACK.md during implementation
- Keep ARCHITECTURE.md updated as system evolves
- Revisit SUCCESS CRITERIA monthly
```

---

## Validation

### Success Criteria

**Documents Generated:**
- ✅ PROJECT-OVERVIEW.md exists and is non-empty (>1KB)
- ✅ SPECIFICATIONS.md exists and is comprehensive (>5KB)
- ✅ TECH-STACK.md exists (unless --minimal) and has 4 categories
- ✅ ARCHITECTURE.md exists (unless --minimal or --no-arch) and has mermaid diagrams
- ✅ .meta/last-sync.json exists (unless --no-sync) with checksums

**Content Quality:**
- ✅ PROJECT-OVERVIEW.md has vision, goals, features, success criteria, constraints
- ✅ SPECIFICATIONS.md has functional requirements, API contracts, data models
- ✅ TECH-STACK.md has rationale and alternatives for each technology
- ✅ ARCHITECTURE.md has C4 diagram, component details, data flow diagrams

**Git Integration:**
- ✅ Files staged for commit (if in git repo)
- ✅ No automatic commit created (user reviews first)

### Error Conditions

**Handle gracefully:**
- Empty or insufficient project description → Return error with guidance
- File not found (--file flag) → Clear error message with path
- PROJECT-OVERVIEW.md already exists → Warn but continue (overwrite)
- Skill execution failure → Display error and suggest manual creation
- Not in git repo → Skip git operations, warn user

---

## Examples in Action

### Example 1: Full Initialization (Recommended)

```bash
$ /lazy init-project "Build a real-time task management platform with AI-powered prioritization, team collaboration, and GitHub integration. Target 1000 users, 99.9% uptime. Python backend, React frontend."

Initializing project...

Step 1/5: Generating project overview and specifications...
✓ PROJECT-OVERVIEW.md created (2.8KB)
✓ SPECIFICATIONS.md created (11.4KB)

Step 2/5: Designing technology stack...
✓ TECH-STACK.md created (6.2KB)
  - Frontend: React 18 + Zustand + Tailwind
  - Backend: FastAPI + SQLAlchemy
  - Database: PostgreSQL + Redis
  - DevOps: AWS ECS + GitHub Actions

Step 3/5: Architecting system design...
✓ ARCHITECTURE.md created (13.7KB)
  - Component architecture with mermaid diagrams
  - Authentication flow documented
  - Scalability strategy defined

Step 4/5: Creating tracking metadata...
✓ .meta/last-sync.json created

Step 5/5: Staging files for git...
✓ 5 files staged (git add)

## Project Initialization Complete

Project: TaskFlow Pro - Modern task management with AI

Documents Generated:
1. ✅ PROJECT-OVERVIEW.md (2.8KB)
2. ✅ SPECIFICATIONS.md (11.4KB) - 12 API endpoints, 6 data models
3. ✅ TECH-STACK.md (6.2KB) - Full stack defined
4. ✅ ARCHITECTURE.md (13.7KB) - 5 mermaid diagrams

Next Steps:
1. Review docs (15-20 min)
2. Commit: git commit -m "docs: initialize project"
3. Create first story: /lazy plan "User authentication"

Complete! Ready for user story planning.
```

### Example 2: Minimal Mode (Fast)

```bash
$ /lazy init-project "E-commerce marketplace with product catalog and checkout" --minimal

Initializing project (minimal mode)...

Step 1/2: Generating project overview and specifications...
✓ PROJECT-OVERVIEW.md created (1.9KB)
✓ SPECIFICATIONS.md created (8.3KB)

Step 2/2: Staging files...
✓ 2 files staged (git add)

## Project Initialization Complete (Minimal)

Project: E-Commerce Marketplace

Documents Generated:
1. ✅ PROJECT-OVERVIEW.md (1.9KB)
2. ✅ SPECIFICATIONS.md (8.3KB)

Skipped (minimal mode):
- TECH-STACK.md (technology selection)
- ARCHITECTURE.md (system design)

Note: Use full mode if you need tech stack guidance and architecture diagrams.

Next Steps:
1. Review specs
2. Manually define tech stack (or run: /lazy init-project --no-minimal)
3. Create stories: /lazy plan "Product catalog"
```

### Example 3: From Enhanced Prompt File

```bash
$ /lazy init-project --file enhanced_prompt.md

Reading project description from: enhanced_prompt.md

Initializing project...

Step 1/5: Generating project overview and specifications...
✓ PROJECT-OVERVIEW.md created (3.2KB)
✓ SPECIFICATIONS.md created (14.8KB)
  - Extracted 15 functional requirements
  - Defined 8 API contracts
  - Specified 9 data models

Step 2/5: Designing technology stack...
✓ TECH-STACK.md created (7.1KB)

Step 3/5: Architecting system design...
✓ ARCHITECTURE.md created (16.4KB)

...

Complete! High-quality docs generated from enhanced prompt.
```

---

## Integration with Other Commands

### With `/lazy plan`

```bash
# Initialize project foundation
/lazy init-project "Project description"

# Create first user story (references SPECIFICATIONS.md automatically)
/lazy plan "Implement authentication"
# → project-manager uses SPECIFICATIONS.md for context
# → Generates US-1.1.md aligned with project specs
```

### With `/lazy code`

```bash
# During implementation
/lazy code @US-1.1.md
# → context-packer loads TECH-STACK.md and ARCHITECTURE.md
# → Implementation follows defined architecture patterns
# → Technology choices match TECH-STACK.md
```

### With `/lazy review`

```bash
# During story review
/lazy review US-1.1
# → reviewer-story agent checks alignment with SPECIFICATIONS.md
# → Validates implementation matches ARCHITECTURE.md
# → Ensures success criteria from PROJECT-OVERVIEW.md are met
```

---

## Environment Variables

```bash
# Skip architecture generation by default
export LAZYDEV_INIT_SKIP_ARCH=1

# Minimal mode by default
export LAZYDEV_INIT_MINIMAL=1

# Disable sync tracking
export LAZYDEV_INIT_NO_SYNC=1

# Custom output directory
export LAZYDEV_PROJECT_DIR="./docs/project"
```

---

## Troubleshooting

### Issue: "Insufficient project description"

**Problem**: Description too vague or short.

**Solution**:
```bash
# Provide more detail
/lazy init-project "Build task manager with:
- Real-time collaboration
- AI prioritization
- GitHub/Jira integration
- Target: 10k users, 99.9% uptime
- Stack preference: Python + React"

# Or use enhanced prompt file
/lazy init-project --file enhanced_prompt.md
```

### Issue: "PROJECT-OVERVIEW.md already exists"

**Problem**: Running init-project in directory that's already initialized.

**Solution**:
```bash
# Review existing docs first
ls -la ./project-management/

# If you want to regenerate (will overwrite)
/lazy init-project "New description"

# Or work with existing docs
/lazy plan "First feature"
```

### Issue: "Skill execution failed"

**Problem**: project-planner or tech-stack-architect skill error.

**Solution**:
```bash
# Check skill files exist
ls .claude/skills/project-planner/SKILL.md
ls .claude/skills/tech-stack-architect/SKILL.md

# Try minimal mode (skips tech-stack-architect)
/lazy init-project "Description" --minimal

# Manual fallback: create docs manually using templates
# See .claude/skills/project-planner/SKILL.md for templates
```

### Issue: "No technology preferences detected"

**Problem**: TECH-STACK.md has generic choices that don't match needs.

**Solution**:
```bash
# Be specific about tech preferences in description
/lazy init-project "API service using FastAPI, PostgreSQL, deployed on AWS ECS with GitHub Actions CI/CD"

# Or edit TECH-STACK.md manually after generation
# File is meant to be customized
```

---

## Key Principles

1. **Documentation-First**: Create foundation before writing code
2. **Smart Defaults**: Skills generate opinionated but reasonable choices
3. **Customizable**: All generated docs are meant to be refined
4. **Integration**: Docs feed into planning and implementation commands
5. **Version Control**: Track docs alongside code
6. **Living Documents**: Update as project evolves
7. **No Lock-In**: Skip sections with flags, edit freely

---

## Related Commands

- `/lazy plan` - Create user stories from initialized project
- `/lazy code` - Implement features following architecture
- `/lazy review` - Validate against project specifications
- `/lazy docs` - Generate additional documentation

---

## Skills Used

- `project-planner` - Generates PROJECT-OVERVIEW.md and SPECIFICATIONS.md
- `tech-stack-architect` - Generates TECH-STACK.md and ARCHITECTURE.md
- `output-style-selector` (automatic) - Formats output optimally

---

**Version:** 1.0.0
**Status:** Production-Ready
**Philosophy:** Document first, build second. Clear foundation, faster development.
