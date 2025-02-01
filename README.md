# Quizlet Quiz Alexa Skill

An Alexa skill that lets you study your Quizlet flashcards through voice interaction. The skill uses Google's Gemini AI to intelligently evaluate your answers, allowing for natural language responses rather than requiring exact matches.

## How It Works

1. Visit the companion website
2. Paste your Quizlet URL and get a 4-digit PIN
3. Use the PIN with Alexa to start studying
4. Answer questions naturally - the AI understands various phrasings

## Features

- Easy PIN-based access to Quizlet sets
- Natural language answer evaluation using Gemini AI
- Tracks wrong answers and reshuffles them for additional practice
- Provides immediate feedback on answers
- Supports conversational responses (e.g., "I think the answer is...")
- PINs expire after 24 hours for security

## Prerequisites

1. An Amazon Developer Account (for the Alexa skill)
2. An AWS Account (for DynamoDB)
3. A Google Cloud Account (for Gemini AI API access)
4. Node.js and npm installed

## Setup

### 1. Environment Variables
Create a `.env` file with the following:
```env
# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key

# AWS Configuration for DynamoDB
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Web Server Configuration
PORT=3000
API_BASE_URL=http://localhost:3000
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start the Web Server
```bash
npm start
```
The web interface will be available at http://localhost:3000

### 4. Deploy the Alexa Skill

1. Create a new Alexa-hosted skill:
   - Use Node.js as the runtime
   - Choose "Custom" model
   - Set invocation name to "quizlet quiz"

2. Upload the interaction model:
   - Go to the "Build" tab
   - Copy contents of `models/en-US.json` to the JSON editor
   - Build the model

3. Deploy the code:
   - Go to the "Code" tab
   - Copy contents of `index.js` to the editor
   - Set the environment variables:
     - GEMINI_API_KEY
     - API_BASE_URL (your deployed web server URL)
   - Deploy

## Usage

1. Get a PIN:
   - Visit http://localhost:3000 (or your deployed URL)
   - Paste your Quizlet URL
   - Get a 4-digit PIN

2. Start the quiz:
   ```
   User: "Alexa, open quizlet quiz"
   Alexa: "Welcome to Quizlet Quiz! To start, visit our website..."
   User: "Start quiz with PIN 1234"
   Alexa: "Great! I found X flashcards. Let's begin..."
   ```

3. Answer questions:
   - Respond naturally to each term
   - The AI will evaluate if your answer captures the correct meaning
   - Wrong answers will be reshuffled for additional practice

## Development

### Project Structure
- `public/` - Web frontend files
  - `index.html` - Main webpage
  - `styles.css` - Styling
  - `script.js` - Frontend logic
- `server.js` - Web server and API endpoints
- `index.js` - Alexa skill logic
- `models/` - Alexa interaction models

### Local Development
1. Run the web server: `npm start`
2. Test the Alexa skill in the developer console
3. Use ngrok for local testing with Alexa

## Notes

- The web server uses DynamoDB to store PIN-URL mappings
- PINs expire after 24 hours
- The skill uses in-memory storage for quiz state
- Gemini AI API calls may add latency to response times
- Ensure your Quizlet sets are publicly accessible

## License

ISC
