# ZecPath AI Development Environment

Welcome to the AI backend ecosystem for the ZecPath project.

## Directory Structure
The architecture is divided into clear functional zones to ensure scalability and decoupling:

- `data/` : Local storage for raw inputs and intermediate processed data (gitignored).
- `parsers/` : Unstructured data extraction (CV parsers, job description parsers).
- `ats_engine/` : Core logic interacting with parsing and basic rule-validation.
- `screening_ai/` : Advanced matching logic (LLM/ML calls) comparing candidates to JDs.
- `interview_ai/` : Generation logic for evaluating candidates dynamically via automated interviews.
- `scoring/` : Algorithms that assess the candidate's metrics across parsers and screeners to generate final scores.
- `utils/` : Cross-cutting concerns such as custom logging, config handling, and database connections.
- `tests/` : Comprehensive integration and unit testing modules.

## Coding Standards
**Python Standards**
- Use `black` for formatting.
- Type hint thoroughly using `mypy` compatible hints.
- Validate logic using `flake8`.

**Docstrings**
- Document modules, classes, and significant functions.

**Logging**
- Never use `print()`. Import the custom logger from `utils.logger` to ensure activities are appropriately recorded.
- Logs will be automatically sent to the `logs/` directory.

## Local Environment Setup
1. Setup Python Virtual Environment:
```bash
python -m venv venv
venv\\Scripts\\activate
```
2. Install Required Libraries:
```bash
pip install -r requirements.txt
```
3. Run Sample Tests:
```bash
pytest
```
