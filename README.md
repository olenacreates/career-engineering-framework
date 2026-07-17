# Career Engineering Framework

> Helping professionals transform fragmented career experience into structured knowledge, intentional positioning, and informed career decisions.

## Overview

Career Engineering Framework is an open framework for applying systems thinking and engineering principles to career development.

Instead of treating CVs, cover letters, interview preparation and career planning as separate activities, the framework helps professionals build a reusable professional knowledge base that evolves throughout a person's career.

The first MVP focuses on transforming an unstructured Career Brain Dump into structured professional knowledge that becomes the foundation for career positioning, analytics, and future career artifacts such as a Master CV.

## Vision

Professionals don't lack experience.

They lack a structured way to understand, organize and reuse it.

Career Engineering Framework transforms fragmented professional experience into structured knowledge that helps people make intentional career decisions throughout their careers.

## Current Status

🚧 Sprint 1 preparation

Current focus:
Building the first MVP — Career Knowledge Extraction Engine.

## Local setup

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your Anthropic API key:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   ```

> **Never commit `.env`.** It holds your secret API key and is already
> listed in `.gitignore`. Only `.env.example` (with placeholder values)
> belongs in version control.