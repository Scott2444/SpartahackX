const https = require('https');


const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

class AnswerChecker {
    constructor(apiKey) {
        this.apiKey = apiKey || GEMINI_API_KEY;
        if (!this.apiKey) {
            console.error("❌ GEMINI_API_KEY is missing!");
        }
    }

    async checkAnswer(question, answer, userAnswer) {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: 'generativelanguage.googleapis.com',
                path: `/v1beta/models/gemini-1.5-flash:generateContent?key=${this.apiKey}`,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            const requestData = JSON.stringify({
                contents: [{
                    parts: [{ text: `Question: ${question}\nCorrect Answer: ${answer}\nUser Answer: ${userAnswer}\nIs the user's answer correct, within reason?
                                     Keep in mind that the user answer is spoken response to the question, so it may be a similar-sounding word to the answer too.
                                     Answer with only "yes" or "no".` }]
                }],
            });

            console.log("🔵 Sending answer check request to Gemini API...");

            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', (chunk) => { data += chunk; });
                res.on('end', () => {
                    try {
                        console.log("🟢 Gemini API Response:", data);
                        const response = JSON.parse(data);

                        if (!response.candidates || !response.candidates[0].content || !response.candidates[0].content.parts) {
                            console.error("❌ Invalid API Response Format:", response);
                            reject("Invalid API response format");
                            return;
                        }

                        const aiResponse = response.candidates[0].content.parts[0].text.trim().toLowerCase();
                        console.log("✅ Parsed AI Response:", aiResponse);

                        resolve(aiResponse.includes('yes'));
                    } catch (error) {
                        console.error("❌ Error parsing API response:", error);
                        reject(error);
                    }
                });
            });

            req.on('error', (error) => { 
                console.error("❌ Error making answer check request:", error);
                reject(error); 
            });

            req.write(requestData);
            req.end();
        });
    }
}

module.exports = AnswerChecker;
