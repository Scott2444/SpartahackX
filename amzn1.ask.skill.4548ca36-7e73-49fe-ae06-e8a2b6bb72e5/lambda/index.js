const Alexa = require('ask-sdk-core');
const AnswerChecker = require('./answerChecker');
const { fetchQuizData, defaultQuestions } = require('./quizlet');
const https = require('https');

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

const checker = new AnswerChecker(GEMINI_API_KEY);

let quizQuestions = defaultQuestions;

const shuffleArray = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
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
                .speak("No question to repeat. Say 'start quiz' to begin.")
                .reprompt("Say 'start quiz' to begin.")
                .getResponse();
        }

        const currentQuestion = (sessionAttributes.rephrasedQuestions && sessionAttributes.rephrasedQuestions[sessionAttributes.questionIndex - 1]) ||
                                quizQuestions[sessionAttributes.questionIndex - 1].question;
        const speakOutput = `The current question is: ${currentQuestion}`;

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

const StartQuizIntentHandler = {
    canHandle(handlerInput) {
        console.log("StartQuizIntentHandler was triggered.");
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest' &&
               Alexa.getIntentName(handlerInput.requestEnvelope) === 'StartQuizIntent';
    },
    async handle(handlerInput) {
        console.log("Handling StartQuizIntent...");
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();

        try {
            quizQuestions = await fetchQuizData();
        } catch (error) {
            console.error('Error fetching quiz data:', error);
            quizQuestions = defaultQuestions;
        }

        if (!quizQuestions || quizQuestions.length === 0) {
            return handlerInput.responseBuilder
                .speak("I couldn't load quiz questions. Please try again later.")
                .getResponse();
        }

        sessionAttributes.questionIndex = 0;
        sessionAttributes.score = 0;
        sessionAttributes.rephrasedQuestions = [];

        let firstDefinition = quizQuestions[0].question;
        let firstTerm = quizQuestions[0].answer;

        if (!firstDefinition.trim().endsWith("?")) {
            console.log("🔄 Rephrasing definition to a question...");
            firstDefinition = await rephraseDefinition(firstDefinition, firstTerm);
        }

        sessionAttributes.rephrasedQuestions[0] = firstDefinition;
        const speakOutput = `Let's begin! ${firstDefinition}`;

        sessionAttributes.questionIndex = 1;
        handlerInput.attributesManager.setSessionAttributes(sessionAttributes);

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
        
        if (!sessionAttributes.questionIndex || sessionAttributes.questionIndex === 0) {
            return handlerInput.responseBuilder
                .speak("No quiz in progress. Say 'start' to begin.")
                .reprompt("Say 'start' to begin.")
                .getResponse();
        }

        const currentScore = sessionAttributes.score || 0;
        const questionsAnswered = sessionAttributes.questionIndex - 1;
        const currentQuestion = (sessionAttributes.rephrasedQuestions && sessionAttributes.rephrasedQuestions[questionsAnswered]) ||
                                quizQuestions[questionsAnswered].question;
        
        const speakOutput = `Your current score is ${currentScore} out of ${questionsAnswered} questions answered. Let's continue with your current question: ${currentQuestion}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt('Please provide your answer.')
            .getResponse();
    }
};

const AnswerIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest' &&
               Alexa.getIntentName(handlerInput.requestEnvelope) === 'AnswerIntent';
    },
    async handle(handlerInput) {
        const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
        const answerGiven = Alexa.getSlotValue(handlerInput.requestEnvelope, 'Answer');

        if (typeof sessionAttributes.questionIndex === 'undefined') {
            return handlerInput.responseBuilder
                .speak("Please say 'start' to begin.")
                .reprompt("Say 'start' to begin.")
                .getResponse();
        }

        const currentQuestionIndex = sessionAttributes.questionIndex - 1;
        const currentQuestion = quizQuestions[currentQuestionIndex].question;
        let speakOutput = '';

        if (!answerGiven) {
            speakOutput = "I didn't catch your answer. Please try again.";
            return handlerInput.responseBuilder
                .speak(speakOutput)
                .reprompt("Please provide your answer.")
                .getResponse();
        }

        try {
            const isCorrect = await checker.checkAnswer(
                                    currentQuestion,
                                    quizQuestions[currentQuestionIndex].answer,  // The correct answer
                                    answerGiven  // The user's answer
                                );
            if (isCorrect) {
                sessionAttributes.score += 1;
                speakOutput = "Correct! ";
            } else {
                speakOutput = `Incorrect. The correct answer is: ${quizQuestions[currentQuestionIndex].answer}. `;
            }
        } catch (error) {
            console.error('Error checking answer:', error);
            speakOutput = "I'm having trouble validating your answer. Please try again later.";
        }

        if (sessionAttributes.questionIndex >= quizQuestions.length) {
            const finalScore = sessionAttributes.score;
            const totalQuestions = quizQuestions.length;
            const percentage = Math.round((finalScore / totalQuestions) * 100);

            speakOutput += `Quiz complete! Your final score is ${finalScore} out of ${totalQuestions}, or ${percentage}%. `;
            speakOutput += "Say 'start' to try again or 'exit' to end.";

            sessionAttributes.questionIndex = 0;
            sessionAttributes.score = 0;
            sessionAttributes.rephrasedQuestions = [];
        } else {
            const nextQuestion = quizQuestions[sessionAttributes.questionIndex];
            const nextDefinition = nextQuestion.question;
            const nextTerm = nextQuestion.answer;

            try {
                const rephrasedQuestion = await rephraseDefinition(nextDefinition, nextTerm);
                if (!sessionAttributes.rephrasedQuestions) {
                    sessionAttributes.rephrasedQuestions = [];
                }
                sessionAttributes.rephrasedQuestions[sessionAttributes.questionIndex] = rephrasedQuestion;
                speakOutput += `The next question is: ${rephrasedQuestion}`;
            } catch (error) {
                console.error('Error rephrasing question:', error);
                speakOutput += `The next question is: ${nextDefinition}`;
            }
            
            sessionAttributes.questionIndex += 1;
        }

        handlerInput.attributesManager.setSessionAttributes(sessionAttributes);

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt('Please provide your answer.')
            .getResponse();
    }
};

const CancelAndStopIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest' &&
               (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent' ||
                Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
    },
    handle(handlerInput) {
        const speakOutput = 'Thanks for playing! Goodbye!';
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

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest' &&
               Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
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

async function rephraseDefinition(definition, term) {
    return new Promise((resolve, reject) => {
        const apiKey = GEMINI_API_KEY;

        if (!apiKey) {
            console.error("❌ API key is missing! Check GEMINI_API_KEY.");
            reject("Missing API key");
            return;
        }

        const options = {
            hostname: 'generativelanguage.googleapis.com',
            path: `/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const requestData = JSON.stringify({
            contents: [{
                parts: [{
    text: `Rephrase the following flashcard pair into a proper question. The question must be worded so that the provided "Answer" is the correct response, using the "Definition" as the context. If the definition is already a question, leave it unchanged.

    Flashcard Pair:
    Definition: "${definition}"
    Answer: "${term}"
    
    For example, if the definition is "Canberra" and the answer is "Australia", a correct question would be: "Which country has Canberra as its capital city?" 
    For example, if the definition is "Lima" and the answer is "Peru", a correct question would be: "Which country has Lima as its capital city?" 
    For example, if the definition is "No soldier can be quartered in a home without the permission of the owner" and the answer is "3rd Amendment", a correct question would be: "Which amendment says that no soldier can be quartered in a home without the permission of the owner?" 
    
    Output a well-structured question.`

}]
            }],
        });

        console.log("🔵 Sending rephrase request to Gemini API...");

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    console.log("🟢 Gemini API Rephrase Response:", data);
                    const response = JSON.parse(data);

                    if (!response.candidates || !response.candidates[0].content || !response.candidates[0].content.parts) {
                        console.error("❌ Invalid API Response Format:", response);
                        reject("Invalid API response format");
                        return;
                    }

                    const rephrasedQuestion = response.candidates[0].content.parts[0].text.trim();
                    console.log("✅ Rephrased Question:", rephrasedQuestion);
                    resolve(rephrasedQuestion);
                } catch (error) {
                    console.error("❌ Error parsing rephrase API response:", error);
                    reject(error);
                }
            });
        });

        req.on('error', (error) => { 
            console.error("❌ Error making rephrase request:", error);
            reject(error); 
        });

        req.write(requestData);
        req.end();
    });
}

const ErrorHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        console.error(`Error handled: ${error.message}`);
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
        HelpIntentHandler,
        RepeatQuestionIntentHandler,
        ScoreIntentHandler,
        CancelAndStopIntentHandler,
        SessionEndedRequestHandler
    )
    .addErrorHandlers(ErrorHandler)
    .lambda();