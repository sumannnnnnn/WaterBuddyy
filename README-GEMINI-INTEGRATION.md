# Google Gemini API Integration for WaterBuddy

This document explains how to set up and use the Google Gemini API integration in WaterBuddy.

## Overview

We've integrated Google's Gemini API into WaterBuddy to provide more advanced AI capabilities in the chatbot assistant. The integration:

1. Replaces the simulated AI with a real AI model from Google
2. Provides more natural, context-aware responses
3. Maintains the same water tracking functionality
4. Falls back to basic responses if the API isn't configured

## Setup Requirements

To use the Gemini API integration, you need:

1. A Google AI Studio account
2. A Gemini API key
3. The `google-generativeai` Python package

### Installation Steps

1. Install the required Python package:
   ```
   pip install google-generativeai
   ```
   Note: This requires Rust to be installed for some platforms. If you encounter issues, you can get Rust from [https://rustup.rs/](https://rustup.rs/)

2. Get a Gemini API key:
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Sign up or log in with your Google account
   - Navigate to "API keys" in your profile
   - Create a new API key

3. Configure the API key in WaterBuddy:
   - Option 1: Set it in the application settings page
   - Option 2: Set an environment variable named `GEMINI_API_KEY`
   - Option 3: Test it in the test page at `/test_gemini`

## Using the Integration

Once configured, the WaterBuddy chatbot will automatically use Google's Gemini API for generating responses. You should notice:

- More natural conversation
- Better understanding of complex questions
- More detailed hydration advice
- Improved personality and engagement

If you don't provide an API key, the system will fall back to basic templated responses.

## Testing the Integration

The application includes a test page at `/test_gemini` where you can:

1. Configure your API key
2. Test sample prompts
3. Verify the API is working correctly

## Troubleshooting

If you encounter issues:

- Check that the API key is entered correctly
- Ensure the `google-generativeai` package is installed
- Check for error messages in the Python console
- Try using the test page to diagnose problems

## Implementation Details

The integration uses:

- `gemini_api.py`: Main API integration and fallback logic
- `gemini_helper.py`: Helper functions for context formatting
- Settings UI for managing the API key

The integration is designed to handle connection issues gracefully and fall back to basic functionality if the API is unavailable. 