# Data Entity Design Document for ZecPath AI Hiring System

This document outlines the standard JSON schemas and data entities designed for the ZecPath AI system. The goal of this structure is to create standardized, highly logical representations of candidates and job descriptions that an LLM or ML classifier can easily process and compare.

## 1. Candidate Profile (Resume Data)
**Purpose**: To represent unstructured resume text entirely as a clean, segmented JSON dictionary.

**Key Components**:
- `candidate_id` & `personal_info`: Extracts identity components to allow anonymized screening (by dropping `personal_info` during the AI grading step to reduce bias).
- `summary`: A synthesized overview for human readable previews and fast keyword scraping.
- `skills` (Array of Skill Objects): Explicitly broken down by category and proficiency.
- `experience` (Array of Experience Objects): Tracks granular work history, dates, and achievements.
- `education` & `certifications`: Proof of qualification.

## 2. Job Profile (Job Description Data)
**Purpose**: To define the rigid boundaries and absolute requirements of a role against which Candidate Profiles are matched.

**Key Components**:
- `job_id`, `job_title`, `department`: Basic metadata.
- `roles_and_responsibilities`: Array of natural language duties suitable for vector embedding alignment against Candidate experience nodes.
- `required_skills` (Array of Skill Objects): Specifies whether a skill is mandatory vs nice-to-have, preventing immediate elimination of strong candidates who lack a minor boolean skill.
- `experience_requirements` & `education_requirements`: Hard filters.

## 3. The Skill Object
Instead of simple arrays of strings (e.g., `["Python", "Java"]`), the Skill Object defines parameters:
- **Resume Side**: `{"name": "Python", "proficiency": "Expert"}`
- **JD Side**: `{"name": "Python", "is_mandatory": true, "min_experience_years": 5}`
**Why this is useful for AI**: An LLM can perform explicit logic ("Does the candidate's Python proficiency match the 5-year requirement?"). It provides context that a flat string cannot.

## 4. The Experience Object
Instead of raw text blocks, experience is parsed into structured chunks:
- `job_title`
- `company`
- `start_date` / `end_date`
- `description`
- `achievements` (Array of strings)
**Why this is useful for AI**: It allows temporal AI logic. The AI can calculate exactly how many cumulative years a person acted as a "Manager", and cross-check achievements against the semantic requirements of the Job Profile.

## Why this Structure is Production-Ready
1. **Bias Mitigation**: The `personal_info` object can be detached during the ATS screening process, preventing LLMs from utilizing name/location demographics in their judgment.
2. **Determinism**: Highly nested, structured JSON severely limits LLM hallucinations compared to asking an AI to "Read this raw PDF and grade it."
3. **Database Portability**: These JSON schemas map perfectly into MongoDB documents or PostgreSQL JSONB columns natively without requiring additional translation layers.
