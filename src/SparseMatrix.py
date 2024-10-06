class CompressedMatrix:
    def __init__(self, total_rows, total_cols):
        """
        Creates a CompressedMatrix object with specified rows and columns.

        :param total_rows: Number of rows in the matrix.
        :param total_cols: Number of columns in the matrix.
        """
        self.data = {}
        self.total_rows = total_rows
        self.total_cols = total_cols

    @staticmethod
    def read_matrix_file(filepath):
        """
        Reads the matrix content from a file manually (no built-in path libraries).

        :param filepath: Location of the matrix file.
        :return: A list containing the lines read from the file.
        """
        try:
            with open(filepath.replace("\\", "/"), "r") as file:
                content = file.readlines()
                return [line.strip() for line in content if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Unable to locate file: {filepath}")

    @staticmethod
    def build_from_file(matrix_filepath):
        """
        Builds a compressed matrix by reading from a given file.

        :param matrix_filepath: The location of the matrix file.
        :return: An instance of CompressedMatrix.
        """
        file_content = CompressedMatrix.read_matrix_file(matrix_filepath)

        if len(file_content) < 2:
            raise ValueError(f"File {matrix_filepath} must contain at least two lines to define dimensions.")
        
        # Extract the matrix dimensions
        try:
            total_rows = int(file_content[0].split('=')[1])
            total_cols = int(file_content[1].split('=')[1])
        except (IndexError, ValueError):
            raise ValueError(f"Invalid dimensions in file {matrix_filepath}.")

        matrix = CompressedMatrix(total_rows, total_cols)

        # Process each matrix element
        for line in file_content[2:]:
            if not line.startswith("(") or not line.endswith(")"):
                raise ValueError(f"Invalid entry format: {line}")

            elements = line[1:-1].split(',')
            try:
                r = int(elements[0].strip())
                c = int(elements[1].strip())
                val = int(elements[2].strip())
            except (IndexError, ValueError):
                raise ValueError(f"Incorrect element format in file: {line}")

            matrix.insert_element(r, c, val)

        return matrix

    def insert_element(self, r, c, val):
        """
        Inserts a value at a specific location in the matrix.

        :param r: Row index.
        :param c: Column index.
        :param val: Value to insert.
        """
        if r >= self.total_rows:
            self.total_rows = r + 1
        if c >= self.total_cols:
            self.total_cols = c + 1

        index = f"{r},{c}"
        self.data[index] = val

    def retrieve_element(self, r, c):
        """
        Retrieves the value at a given matrix position.

        :param r: Row index.
        :param c: Column index.
        :return: The value at the given position or 0 if it doesn't exist.
        """
        index = f"{r},{c}"
        return self.data.get(index, 0)

    def matrix_add(self, other):
        """
        Adds two compressed matrices.

        :param other: Another CompressedMatrix.
        :return: A new CompressedMatrix that is the result of the addition.
        """
        if self.total_rows != other.total_rows or self.total_cols != other.total_cols:
            raise ValueError(f"Matrices must have matching dimensions.")

        result = CompressedMatrix(self.total_rows, self.total_cols)

        # Add elements from the current matrix
        for index, value in self.data.items():
            r, c = map(int, index.split(','))
            result.insert_element(r, c, value)

        # Add elements from the other matrix
        for index, value in other.data.items():
            r, c = map(int, index.split(','))
            result.insert_element(r, c, result.retrieve_element(r, c) + value)

        return result

    def matrix_subtract(self, other):
        """
        Subtracts another matrix from this one.

        :param other: Another CompressedMatrix.
        :return: A new CompressedMatrix representing the result of the subtraction.
        """
        if self.total_rows != other.total_rows or self.total_cols != other.total_cols:
            raise ValueError(f"Matrices must have matching dimensions.")

        result = CompressedMatrix(self.total_rows, self.total_cols)

        # Subtract elements from the other matrix
        for index, value in other.data.items():
            r, c = map(int, index.split(','))
            result.insert_element(r, c, self.retrieve_element(r, c) - value)

        return result

    def matrix_multiply(self, other):
        """
        Multiplies two compressed matrices together.

        :param other: Another CompressedMatrix.
        :return: A new CompressedMatrix representing the product.
        """
        if self.total_cols != other.total_rows:
            raise ValueError(f"Matrix multiplication requires column count of the first to equal row count of the second.")

        result = CompressedMatrix(self.total_rows, other.total_cols)

        for index1, value1 in self.data.items():
            r1, c1 = map(int, index1.split(','))
            for index2, value2 in other.data.items():
                r2, c2 = map(int, index2.split(','))
                if c1 == r2:
                    result.insert_element(r1, c2, result.retrieve_element(r1, c2) + value1 * value2)

        return result

    def __str__(self):
        """
        Provides a string-based view of the compressed matrix.

        :return: A string showing matrix elements and dimensions.
        """
        result = [f"rows={self.total_rows}", f"cols={self.total_cols}"]
        for index, value in self.data.items():
            r, c = index.split(',')
            result.append(f"({r}, {c}, {value})")
        return '\n'.join(result)

    def write_to_file(self, filepath):
        """
        Saves the compressed matrix to a file.

        :param filepath: Destination file path for saving the matrix.
        """
        with open(filepath, 'w') as file:
            file.write(str(self))


def collect_user_input(prompt_text):
    """
    Collects user input from the console.

    :param prompt_text: The message to display to the user.
    :return: Input given by the user.
    """
    return input(prompt_text)


def run_matrix_operations():
    """
    Executes matrix operations based on user commands.
    """
    try:
        available_operations = {
            'A': ('Matrix Addition', 'matrix_add'),
            'B': ('Matrix Subtraction', 'matrix_subtract'),
            'C': ('Matrix Multiplication', 'matrix_multiply')
        }

        print("Available MATRIX Operations: ")
        print("(A) Add Matrices")
        print("(B) Subtract Matrices")
        print("(C) Multiply Matrices")

        operation_choice = collect_user_input("Choose operation (A, B, C): ")
        if operation_choice not in available_operations:
            raise ValueError("Invalid operation selection.")

        filepath1 = collect_user_input("Enter file path for the first matrix: ")
        filepath2 = collect_user_input("Enter file path for the second matrix: ")

        print(f"Loading first matrix from {filepath1}...")
        matrix1 = CompressedMatrix.build_from_file(filepath1)
        print(f"First matrix with size {matrix1.total_rows}x{matrix1.total_cols} loaded successfully.")

        print(f"Loading second matrix from {filepath2}...")
        matrix2 = CompressedMatrix.build_from_file(filepath2)
        print(f"Second matrix with size {matrix2.total_rows}x{matrix2.total_cols} loaded successfully.")

        operation_name, method_name = available_operations[operation_choice]
        print(f"Performing {operation_name}...")

        result_matrix = getattr(matrix1, method_name)(matrix2)
        output_filepath = f"{operation_name}_result.txt"
        result_matrix.write_to_file(output_filepath)

        print(f"Operation completed. Result saved to {output_filepath}.")
    except Exception as error:
        print(f"An error occurred: {str(error)}")


if __name__ == "__main__":
    run_matrix_operations()