# Overview

This project consists of two distinct applications that share the same codebase: a **Companion AI** voice-activated assistant designed for Raspberry Pi hardware, and a **web application** built with React and Express. The Companion AI is a Python-based voice assistant that uses speech recognition, text-to-speech, and OpenAI's GPT-4o model to provide conversational AI functionality optimized for ARM architecture. The web application is a full-stack TypeScript solution with a React frontend using shadcn/ui components and an Express backend with database capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Python Companion AI Architecture

**Modular Component Design**: The AI companion follows a clean separation of concerns with dedicated modules for voice handling (`VoiceHandler`), speech synthesis (`SpeechEngine`), AI processing (`AIBrain`), and system utilities. The main application (`CompanionAI`) orchestrates these components through a centralized controller pattern.

**Voice Processing Pipeline**: Audio input flows through Google Speech Recognition for speech-to-text conversion, gets processed by the AI brain for response generation, and outputs through pyttsx3 for text-to-speech synthesis. This creates a continuous conversation loop optimized for real-time interaction.

**Configuration Management**: Centralized configuration through the `Config` class allows easy customization of voice settings, AI personality, hardware parameters, and API credentials without code modifications.

**Hardware Abstraction**: The system includes GPIO capability flags and hardware detection utilities to seamlessly run on both development machines and Raspberry Pi hardware without code changes.

## Web Application Architecture

**Full-Stack TypeScript**: The web application uses TypeScript throughout the stack with React for the frontend and Express for the backend, ensuring type safety and better developer experience.

**Component-Based Frontend**: Built with React Router (wouter), React Query for state management, and shadcn/ui component library providing a modern, accessible interface with Tailwind CSS styling.

**Express Backend with Middleware**: The server uses Express with custom middleware for request logging, error handling, and development-specific features like Vite integration for hot reloading.

**Database Integration**: Uses Drizzle ORM with PostgreSQL support, including migration management and type-safe database operations through generated schemas.

**Development Tooling**: Integrates Vite for fast development builds, ESBuild for production bundling, and development-specific tooling like runtime error overlays and hot module replacement.

# External Dependencies

**AI Services**: OpenAI GPT-4o API for natural language processing and conversation generation, requiring API key authentication for all AI-powered interactions.

**Voice Processing**: Google Speech Recognition service for speech-to-text conversion and pyttsx3 library for local text-to-speech synthesis without external API dependencies.

**Database**: PostgreSQL database through Neon serverless platform (@neondatabase/serverless) with Drizzle ORM for type-safe database operations and schema management.

**UI Framework**: shadcn/ui component system built on Radix UI primitives, providing accessible and customizable React components with Tailwind CSS integration.

**Development Infrastructure**: Replit-specific integrations for development environment, Vite for frontend tooling, and various development utilities for debugging and performance monitoring.

**Hardware Libraries**: Python libraries for Raspberry Pi GPIO control (when enabled), audio device management through speech_recognition, and system monitoring utilities for performance tracking.