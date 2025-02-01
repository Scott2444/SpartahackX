/* @file text_to_json.js
 *
 * Usage:
 * 1) Export quizlet set
 * 2) Set delimeters to:
 *      a) Between term and definition = <ans>
 *      b) Between rows = \n
 */

const fs = require('fs');

export function convertTermsToJson(inputText) {
    // Handle empty or invalid input
    if (!inputText || typeof inputText !== 'string') {
        throw new Error('Input must be a non-empty string');
    }

    // Split the input text into lines and filter out empty lines
    const lines = inputText.split('\n').filter(line => line.trim());

    // Process each line and create term-definition pairs
    const terms = lines.map(line => {
        // Split on <ans> delimiter
        const [term, definition] = line.split('<ans>');

        // Validate that we have both term and definition
        if (!term || !definition) {
            throw new Error(`Invalid format in line: ${line}`);
        }

        return {
            term: term.trim(),
            definition: definition.trim()
        };
    });

    // Create the final JSON structure
    return {
        flashcards: terms
    };
}

function convertAndSaveToFile(inputText, outputFilePath) {
    try {
        // Convert the text to JSON
        const jsonResult = convertTermsToJson(inputText);

        // Convert to formatted JSON string
        const jsonString = JSON.stringify(jsonResult, null, 2);

        // Write to file
        fs.writeFileSync(outputFilePath, jsonString, 'utf8');

        console.log(`Successfully wrote JSON to ${outputFilePath}`);
        return true;
    } catch (error) {
        console.error('Error:', error.message);
        return false;
    }
}

/*
// Example usage:
const input = `France<ans>Paris
Japan<ans>Tokyo
Brazil<ans>Brasilia
Canada<ans>Ottawa
Australia<ans>Canberra`;

// Specify the output file path
const outputFile = 'flashcards.json';

// Convert and save
convertAndSaveToFile(input, outputFile);
*/