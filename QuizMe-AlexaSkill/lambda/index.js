const Alexa = require('ask-sdk-core');

const { fetchQuizData, defaultQuestions } = require('./quizlet');

let quizQuestions = defaultQuestions;



const StartQuizIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'StartQuizIntent';
    },
    async handle(handlerInput) {
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        
        try {
            // Fetch fresh questions at the start of each quiz
            quizQuestions = await fetchQuizData();
        } catch (error) {
            console.error('Error fetching quiz data:', error);
            // Use default questions if fetch fails
            quizQuestions = defaultQuestions;
        }
        
        // Initialize or reset session data
        sessionAttributes.questionIndex = 0;
        sessionAttributes.score = 0;
        
        const firstQuestion = quizQuestions[0];
        const speakOutput = `Let's begin! The definition is: ${firstQuestion.question}?`;
        
        sessionAttributes.questionIndex = 1;
        handlerInput.attributesManager.setSessionAttributes(sessionAttributes);
        
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt('Please provide your answer.')
            .getResponse();
    }
};

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speakOutput = 'Welcome to Quiz Me! Say "start" to begin, or "help" for instructions.';
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};



const AnswerIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AnswerIntent';
    },
    handle(handlerInput) {
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        const answerGiven = Alexa.getSlotValue(handlerInput.requestEnvelope, 'Answer');
        
        if (typeof sessionAttributes.questionIndex === 'undefined') {
            return handlerInput.responseBuilder
                .speak("Please say 'start' to begin.")
                .reprompt("Say 'start' to begin.")
                .getResponse();
        }

        const currentQuestionIndex = sessionAttributes.questionIndex - 1;
        const correctAnswer = quizQuestions[currentQuestionIndex].answer.toLowerCase();
        let speakOutput = '';

        if (!answerGiven) {
            speakOutput = "I didn't catch your answer. Please try again.";
            return handlerInput.responseBuilder
                .speak(speakOutput)
                .reprompt("Please provide your answer.")
                .getResponse();
        }

        if (answerGiven.toLowerCase() === correctAnswer) {
            sessionAttributes.score += 1;
            speakOutput = "Correct! ";
        } else {
            speakOutput = `Incorrect. The correct answer is: ${quizQuestions[currentQuestionIndex].answer}. `;
        }

        if (sessionAttributes.questionIndex >= quizQuestions.length) {
            const finalScore = sessionAttributes.score;
            const totalQuestions = quizQuestions.length;
            const percentage = Math.round((finalScore / totalQuestions) * 100);
            
            speakOutput += `Quiz complete! Your final score is ${finalScore} out of ${totalQuestions}, or ${percentage}%. `;
            speakOutput += "Say 'start' to try again or 'exit' to end.";
            
            sessionAttributes.questionIndex = 0;
            sessionAttributes.score = 0;
        } else {
            const nextQuestion = quizQuestions[sessionAttributes.questionIndex];
            speakOutput += `The definition is: ${nextQuestion.question}?`;
            sessionAttributes.questionIndex += 1;
        }

        handlerInput.attributesManager.setSessionAttributes(sessionAttributes);

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt('Please provide your answer.')
            .getResponse();
    }
};


const RepeatQuestionIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'RepeatQuestionIntent';
    },
    handle(handlerInput) {
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        
        if (!sessionAttributes.questionIndex || sessionAttributes.questionIndex === 0) {
            return handlerInput.responseBuilder
                .speak("No question to repeat. Say 'start' to begin.")
                .reprompt("Say 'start' to begin.")
                .getResponse();
        }

        const currentQuestion = quizQuestions[sessionAttributes.questionIndex - 1];
        const speakOutput = `The current question is: ${currentQuestion.question}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt('Please provide your answer.')
            .getResponse();
    }
};

const ScoreIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ScoreIntent';
    },
    handle(handlerInput) {
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        
        if (!sessionAttributes.score) {
            return handlerInput.responseBuilder
                .speak("No quiz in progress. Say 'start' to begin.")
                .reprompt("Say 'start' to begin.")
                .getResponse();
        }

        const currentScore = sessionAttributes.score;
        const questionsAnswered = sessionAttributes.questionIndex - 1;
        const speakOutput = `Your current score is ${currentScore} out of ${questionsAnswered} questions answered.`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt('Say "continue" to return to the quiz.')
            .getResponse();
    }
};

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
    },
    handle(handlerInput) {
        const speakOutput = 'You can say "start" to begin, "repeat question" to hear the current question again, ' +
            '"score" to hear your current score, or "stop" to end the quiz. How can I help?';

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
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        let speakOutput = 'Thanks for playing! Goodbye!';
        
        if (sessionAttributes.score) {
            const currentScore = sessionAttributes.score;
            const questionsAnswered = sessionAttributes.questionIndex - 1;
            speakOutput = `Your final score was ${currentScore} out of ${questionsAnswered}. ${speakOutput}`;
        }

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const SessionEndedRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
    },
    handle(handlerInput) {
        return handlerInput.responseBuilder.getResponse();
    }
};

const ErrorHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        console.log(`Error handled: ${error.message}`);
        const speakOutput = 'Sorry, I had trouble understanding that. Please try again.';

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
        RepeatQuestionIntentHandler,
        ScoreIntentHandler,
        HelpIntentHandler,
        CancelAndStopIntentHandler,
        SessionEndedRequestHandler
    )
    .addErrorHandlers(ErrorHandler)
    .lambda();