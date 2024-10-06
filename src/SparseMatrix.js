class SparseMatrixJS {
    constructor(totalRows, totalColumns) {
        /**
         * Initializes the SparseMatrixJS instance.
         *
         * @param {number} totalRows - Total number of rows in the matrix.
         * @param {number} totalColumns - Total number of columns in the matrix.
         */
        this.dataMap = {};
        this.totalRows = totalRows;
        this.totalColumns = totalColumns;
    }

    static readMatrixFromFile(filePath) {
        /**
         * Reads a matrix from a file manually, using basic file input.
         *
         * @param {string} filePath - The path to the matrix file.
         * @returns {Promise<string[]>} A promise resolving to an array of matrix lines.
         */
        return new Promise((resolve, reject) => {
            const fs = require('fs');
            fs.readFile(filePath.replace(/\\/g, "/"), 'utf8', (err, content) => {
                if (err) {
                    reject(`File not found: ${filePath}`);
                } else {
                    const lines = content.split("\n").map(line => line.trim()).filter(line => line);
                    resolve(lines);
                }
            });
        });
    }

    static async fromFile(matrixFilePath) {
        /**
         * Loads a sparse matrix from a file and creates a SparseMatrixJS instance.
         *
         * @param {string} matrixFilePath - The path to the matrix file.
         * @returns {Promise<SparseMatrixJS>} A promise resolving to a SparseMatrixJS instance.
         */
        const fileContent = await SparseMatrixJS.readMatrixFromFile(matrixFilePath);

        if (fileContent.length < 2) {
            throw new Error(`File ${matrixFilePath} must have at least two lines for dimensions.`);
        }

        let totalRows, totalColumns;
        try {
            totalRows = parseInt(fileContent[0].split('=')[1]);
            totalColumns = parseInt(fileContent[1].split('=')[1]);
        } catch (error) {
            throw new Error(`Invalid matrix dimensions in ${matrixFilePath}.`);
        }

        const matrixInstance = new SparseMatrixJS(totalRows, totalColumns);

        fileContent.slice(2).forEach(line => {
            if (!line.startsWith("(") || !line.endsWith(")")) {
                throw new Error(`Invalid element format: ${line}`);
            }
            const [row, col, value] = line.slice(1, -1).split(',').map(val => parseInt(val.trim()));

            matrixInstance.setElement(row, col, value);
        });

        return matrixInstance;
    }

    setElement(row, col, value) {
        /**
         * Inserts a value into the sparse matrix.
         *
         * @param {number} row - Row index for the element.
         * @param {number} col - Column index for the element.
         * @param {number} value - The value to be inserted.
         */
        if (row >= this.totalRows) {
            this.totalRows = row + 1;
        }
        if (col >= this.totalColumns) {
            this.totalColumns = col + 1;
        }
        const key = `${row},${col}`;
        this.dataMap[key] = value;
    }

    getElement(row, col) {
        /**
         * Retrieves an element's value from a specific row and column in the matrix.
         *
         * @param {number} row - Row index.
         * @param {number} col - Column index.
         * @returns {number} Value at the given row and column or 0 if no element is present.
         */
        const key = `${row},${col}`;
        return this.dataMap[key] || 0;
    }

    addMatrices(otherMatrix) {
        /**
         * Adds two sparse matrices together.
         *
         * @param {SparseMatrixJS} otherMatrix - Another sparse matrix.
         * @returns {SparseMatrixJS} New matrix containing the result of the addition.
         */
        if (this.totalRows !== otherMatrix.totalRows || this.totalColumns !== otherMatrix.totalColumns) {
            throw new Error("Matrices have different dimensions.");
        }

        const resultMatrix = new SparseMatrixJS(this.totalRows, this.totalColumns);

        // Add elements from this matrix
        Object.keys(this.dataMap).forEach(key => {
            const [row, col] = key.split(',').map(Number);
            resultMatrix.setElement(row, col, this.dataMap[key]);
        });

        // Add elements from the other matrix
        Object.keys(otherMatrix.dataMap).forEach(key => {
            const [row, col] = key.split(',').map(Number);
            resultMatrix.setElement(row, col, resultMatrix.getElement(row, col) + otherMatrix.dataMap[key]);
        });

        return resultMatrix;
    }

    subtractMatrices(otherMatrix) {
        /**
         * Subtracts another sparse matrix from this one.
         *
         * @param {SparseMatrixJS} otherMatrix - Another sparse matrix.
         * @returns {SparseMatrixJS} New matrix representing the result of the subtraction.
         */
        if (this.totalRows !== otherMatrix.totalRows || this.totalColumns !== otherMatrix.totalColumns) {
            throw new Error("Matrices have different dimensions.");
        }

        const resultMatrix = new SparseMatrixJS(this.totalRows, this.totalColumns);

        Object.keys(otherMatrix.dataMap).forEach(key => {
            const [row, col] = key.split(',').map(Number);
            resultMatrix.setElement(row, col, this.getElement(row, col) - otherMatrix.dataMap[key]);
        });

        return resultMatrix;
    }

    multiplyMatrices(otherMatrix) {
        /**
         * Multiplies two sparse matrices together.
         *
         * @param {SparseMatrixJS} otherMatrix - Another sparse matrix.
         * @returns {SparseMatrixJS} Result matrix after multiplication.
         */
        if (this.totalColumns !== otherMatrix.totalRows) {
            throw new Error("Matrix multiplication is only possible when the number of columns in the first matrix equals the number of rows in the second matrix.");
        }

        const resultMatrix = new SparseMatrixJS(this.totalRows, otherMatrix.totalColumns);

        Object.keys(this.dataMap).forEach(key1 => {
            const [row1, col1] = key1.split(',').map(Number);
            Object.keys(otherMatrix.dataMap).forEach(key2 => {
                const [row2, col2] = key2.split(',').map(Number);
                if (col1 === row2) {
                    resultMatrix.setElement(row1, col2, resultMatrix.getElement(row1, col2) + this.dataMap[key1] * otherMatrix.dataMap[key2]);
                }
            });
        });

        return resultMatrix;
    }

    toString() {
        /**
         * Converts the sparse matrix to a string representation.
         *
         * @returns {string} Stringified representation of the matrix and its elements.
         */
        const matrixLines = [`rows=${this.totalRows}`, `cols=${this.totalColumns}`];
        Object.keys(this.dataMap).forEach(key => {
            const [row, col] = key.split(',');
            matrixLines.push(`(${row}, ${col}, ${this.dataMap[key]})`);
        });
        return matrixLines.join('\n');
    }

    async saveMatrixToFile(filePath) {
        /**
         * Saves the sparse matrix to a file.
         *
         * @param {string} filePath - The file path where the matrix will be saved.
         */
        const fs = require('fs');
        fs.writeFileSync(filePath, this.toString(), 'utf8');
    }
}

function getUserInput(promptText) {
    /**
     * Collects user input from the terminal.
     *
     * @param {string} promptText - Text displayed as a prompt to the user.
     * @returns {Promise<string>} A promise resolving to the user input.
     */
    const readline = require('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(promptText, (input) => {
            rl.close();
            resolve(input);
        });
    });
}

async function executeMatrixOperations() {
    /**
     * Handles matrix operations based on user input.
     */
    try {
        const operations = {
            'A': { operationName: 'Matrix Addition', method: 'addMatrices' },
            'B': { operationName: 'Matrix Subtraction', method: 'subtractMatrices' },
            'C': { operationName: 'Matrix Multiplication', method: 'multiplyMatrices' }
        };

        console.log("Available MATRIX Operations:");
        console.log("(A) Addition");
        console.log("(B) Subtraction");
        console.log("(C) Multiplication");

        const operationChoice = await getUserInput("Choose an operation (A, B, C): ");
        if (!operations[operationChoice]) {
            throw new Error("Invalid option selected.");
        }

        const matrixFile1 = await getUserInput("Enter path for the first matrix file: ");
        const matrixFile2 = await getUserInput("Enter path for the second matrix file: ");

        console.log(`Loading first matrix from ${matrixFile1}...`);
        const matrix1 = await SparseMatrixJS.fromFile(matrixFile1);
        console.log(`First matrix loaded with dimensions ${matrix1.totalRows}x${matrix1.totalColumns}`);

        console.log(`Loading second matrix from ${matrixFile2}...`);
        const matrix2 = await SparseMatrixJS.fromFile(matrixFile2);
        console.log(`Second matrix loaded with dimensions ${matrix2.totalRows}x${matrix2.totalColumns}`);

        const selectedOperation = operations[operationChoice];
        const resultMatrix = matrix1[selectedOperation.method](matrix2);
        console.log(`${selectedOperation.operationName} Result:`);
        console.log(resultMatrix.toString());

        const saveFilePath = await getUserInput("Enter path to save the result matrix: ");
        await resultMatrix.saveMatrixToFile(saveFilePath);
        console.log(`Matrix saved successfully to ${saveFilePath}`);

    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}

executeMatrixOperations();
