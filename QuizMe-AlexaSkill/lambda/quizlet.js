const https = require('https');

// Function to fetch and format quiz data
const fetchQuizData = async () => {
  return new Promise((resolve, reject) => {
    https.get('https://8499-35-21-191-163.ngrok-free.app/data.json', (resp) => {
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


// module.exports = [
//   { question: "What organelle is known as the powerhouse of the cell?", answer: "mitochondria" },
//   { question: "Which process do plants use to make their own food using sunlight?", answer: "photosynthesis" },
//   { question: "What is the smallest unit of life?", answer: "cell" },
//   { question: "What type of division occurs when a cell splits into two identical cells?", answer: "mitosis" },
//   { question: "What molecule carries our genetic code?", answer: "DNA" },
//   { question: "What process allows organisms to maintain internal balance?", answer: "homeostasis" },
//   { question: "What biological catalyst speeds up chemical reactions in living things?", answer: "enzyme" },
//   { question: "What is the name for a protective layer around a cell?", answer: "membrane" },
//   { question: "What structure contains genetic material in the cell?", answer: "nucleus" },
//   { question: "What protein factory organelle makes proteins in the cell?", answer: "ribosome" }
// ];
