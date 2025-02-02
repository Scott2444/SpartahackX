const https = require('https');


// Function to fetch and format quiz data
const fetchQuizData = async () => {
  return new Promise((resolve, reject) => {
    https.get('https://quiz-me-api.onrender.com/quiz_data.json', (resp) => {
      let data = '';

      resp.on('data', (chunk) => {
        data += chunk;
      });

      resp.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          // Transform the data into our quiz format
          const quizData = jsonData.terms.map(item => ({
            question: item.definition, // Use definition as the question
            answer: item.term         // Use term as the answer
          }));
          resolve(quizData);
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', (error) => {
      reject(error);
    });
  });
};

// Export both the function and a default array in case fetch fails
module.exports = {
  fetchQuizData,
  defaultQuestions: [
    {
      question: "Paris",
      answer: "France"
    }
  ]
};

// Export both the function and a default array in case fetch fails
module.exports = {
  fetchQuizData,
  defaultQuestions: [
    {
      question: "Paris",
      answer: "France"
    }
  ]
};
