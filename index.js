const Alexa = require('ask-sdk-core');
const axios = require('axios');

// Store quiz state in memory
const quizState = {
  currentCards: [],
  wrongCards: [],
  currentCardIndex: 0
};

// Your web server URL (update this with your actual URL when deployed)
const SERVER_URL = process.env.SERVER_URL || 'http://localhost:3000';

const LaunchRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
  },
  handle(handlerInput) {
    const speakOutput = 'Welcome to Quiz Me! Visit our website to create a quiz and get a PIN. Then say "start quiz with PIN" followed by your number.';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  }
};

const StartQuizIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'StartQuizIntent';
  },
  async handle(handlerInput) {
    try {
      console.log('StartQuizIntent triggered with full input:', JSON.stringify(handlerInput.requestEnvelope, null, 2));
      
      const pin = handlerInput.requestEnvelope.request.intent.slots.pin.value;
      console.log('Received PIN:', pin);
      
      // Convert pin to string and remove any spaces or special characters
      const normalizedPin = pin.toString().replace(/\s+/g, '');
      console.log('Normalized PIN:', normalizedPin);
      console.log('Server URL:', SERVER_URL);

      try {
        // Fetch quiz data from your server
        console.log('Fetching quiz data from:', `${SERVER_URL}/api/quiz/${normalizedPin}`);
        const response = await axios.get(`${SERVER_URL}/api/quiz/${normalizedPin}`);
        console.log('Server response:', response.data);
        const cards = response.data;

        if (!Array.isArray(cards) || cards.length === 0) {
          console.log('Invalid quiz data received:', cards);
          throw new Error('Invalid quiz data received');
        }

        // Shuffle cards
        quizState.currentCards = cards.sort(() => Math.random() - 0.5);
        quizState.currentCardIndex = 0;
        quizState.wrongCards = [];
        
        const speakOutput = `Great! I found ${cards.length} questions. Let's begin. ${cards[0].term}`;
        
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt(speakOutput)
          .getResponse();

      } catch (error) {
        console.error('Error fetching quiz:', error);
        if (error.response && error.response.status === 404) {
          return handlerInput.responseBuilder
            .speak("I couldn't find a quiz with that PIN. Please check the PIN and try again.")
            .reprompt("Please try again with a valid PIN.")
            .getResponse();
        }
        throw error;
      }

    } catch (error) {
      console.error('Error starting quiz:', error);
      const speakOutput = 'Sorry, I had trouble starting the quiz. Please try again.';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .reprompt(speakOutput)
        .getResponse();
    }
  }
};

const AnswerIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AnswerIntent';
  },
  handle(handlerInput) {
    const userAnswer = handlerInput.requestEnvelope.request.intent.slots.answer.value.toLowerCase();
    const currentCard = quizState.currentCards[quizState.currentCardIndex];
    
    if (!currentCard) {
      return handlerInput.responseBuilder
        .speak('Please start a quiz first by providing a PIN.')
        .reprompt('Please provide a PIN to start the quiz.')
        .getResponse();
    }
    
    try {
      // Simple answer comparison
      const correctAnswer = currentCard.definition.toLowerCase();
      const isCorrect = userAnswer.includes(correctAnswer) || correctAnswer.includes(userAnswer);
      
      let speakOutput;
      if (isCorrect) {
        if (quizState.currentCardIndex === quizState.currentCards.length - 1 && quizState.wrongCards.length === 0) {
          speakOutput = 'Correct! Congratulations, you\'ve completed the quiz!';
          // Reset quiz state
          quizState.currentCards = [];
          quizState.currentCardIndex = 0;
        } else {
          quizState.currentCardIndex++;
          if (quizState.currentCardIndex >= quizState.currentCards.length) {
            if (quizState.wrongCards.length > 0) {
              // Start reviewing wrong cards
              quizState.currentCards = [...quizState.wrongCards];
              quizState.wrongCards = [];
              quizState.currentCardIndex = 0;
              speakOutput = `Correct! Now let's review the questions you got wrong. ${quizState.currentCards[0].term}`;
            }
          } else {
            speakOutput = `Correct! Next question: ${quizState.currentCards[quizState.currentCardIndex].term}`;
          }
        }
      } else {
        // Add current card to wrong cards if not already there
        quizState.wrongCards.push(currentCard);
        speakOutput = `Incorrect. The correct answer was: ${currentCard.definition}. Let's try another one. ${quizState.currentCards[quizState.currentCardIndex].term}`;
      }
      
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .reprompt(speakOutput)
        .getResponse();
    } catch (error) {
      console.error('Error processing answer:', error);
      const speakOutput = 'Sorry, I had trouble processing your answer. Please try again.';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .reprompt(speakOutput)
        .getResponse();
    }
  }
};

const HelpIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
  },
  handle(handlerInput) {
    const speakOutput = 'Visit our website to create a quiz and get a PIN. Then say "start quiz with PIN" followed by your number. I will read each question, and you can respond with your answer.';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  }
};

const CancelAndStopIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
        || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
  },
  handle(handlerInput) {
    const speakOutput = 'Thanks for studying with Quiz Me. Goodbye!';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  }
};

const ErrorHandler = {
  canHandle() {
    return true;
  },
  handle(handlerInput, error) {
    console.error('Error handling request:', error);
    const speakOutput = 'Sorry, I had trouble processing your request. Please try again.';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  }
};

exports.handler = Alexa.SkillBuilders.custom()
  .addRequestHandlers(
    LaunchRequestHandler,
    StartQuizIntentHandler,
    AnswerIntentHandler,
    HelpIntentHandler,
    CancelAndStopIntentHandler
  )
  .addErrorHandlers(ErrorHandler)
  .lambda();
