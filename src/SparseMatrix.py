class CompressedMatrix:
    def __init__(self, rows_count, cols_count):
        """
        Initializes a CompressedMatrix object.

        :param rows_count: Number of rows in the matrix
        :param cols_count: Number of columns in the matrix
        """
        self.matrix_data = {}
        self.total_rows = rows_count
        self.total_cols = cols_count

    @staticmethod
    def _load_matrix_from_file(filepath):
        """
        Reads a matrix file manually without using built-in libraries for path handling.

        :param filepath: Path to the matrix file
        :return: List of lines from the matrix file
        """
        try:
            with open(filepath.replace("\\", "/"), "r") as file:
                data_lines = file.readlines()
                return [line.strip() for line in data_lines if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")

    @staticmethod
    def import_from_file(file_path):
        """
        Loads a compressed matrix from the specified file.

        :param file_path: The path of the file containing matrix data
        :return: CompressedMatrix instance
        """
        data_lines = CompressedMatrix._load_matrix_from_file(file_path)
        
        if len(data_lines) < 2:
            raise ValueError(f"File {file_path} must contain at least two lines for matrix dimensions.")
        
        # Read the matrix dimensions
        try:
            rows_count = int(data_lines[0].split('=')[1])
            cols_count = int(data_lines[1].split('=')[1])
        except (IndexError, ValueError):
            raise ValueError(f"Invalid matrix dimensions in {file_path}.")
        
        matrix_instance = CompressedMatrix(rows_count, cols_count)

        # Parse matrix elements
        for element_line in data_lines[2:]:
            if not element_line.startswith("(") or not element_line.endswith(")"):
                raise ValueError(f"Invalid format for matrix element: {element_line}")

            parts = element_line[1:-1].split(',')
            try:
                row_index = int(parts[0].strip())
                col_index = int(parts[1].strip())
                value = int(parts[2].strip())
            except (IndexError, ValueError):
                raise ValueError(f"Invalid matrix element format in file: {element_line}")
            
            matrix_instance.update_value(row_index, col_index, value)
        
        return matrix_instance

    def update_value(self, row, col, val):
        """
        Updates a value at a specific row and column in the compressed matrix.

        :param row: Row index
        :param col: Column index
        :param val: Value to update
        """
        if row >= self.total_rows:
            self.total_rows = row + 1
        if col >= self.total_cols:
            self.total_cols = col + 1
        
        key = f"{row},{col}"
        self.matrix_data[key] = val

    def retrieve_value(self, row, col):
        """
        Retrieves a value from a specific row and column in the compressed matrix.

        :param row: Row index
        :param col: Column index
        :return: Value at the given row and column, or 0 if no element is present
        """
        key = f"{row},{col}"
        return self.matrix_data.get(key, 0)

    def matrix_add(self, other_matrix):
        """
        Adds two compressed matrices and returns the result.

        :param other_matrix: CompressedMatrix to add
        :return: A new CompressedMatrix instance representing the result of the addition
        """
        if self.total_rows != other_matrix.total_rows or self.total_cols != other_matrix.total_cols:
            raise ValueError(f"Cannot add matrices with different dimensions.")
        
        combined_matrix = CompressedMatrix(self.total_rows, self.total_cols)
        
        # Combine elements from both matrices
        for key, val in self.matrix_data.items():
            row, col = map(int, key.split(','))
            combined_matrix.update_value(row, col, val)

        for key, val in other_matrix.matrix_data.items():
            row, col = map(int, key.split(','))
            combined_matrix.update_value(row, col, combined_matrix.retrieve_value(row, col) + val)
        
        return combined_matrix

    def matrix_subtract(self, subtract_matrix):
        """
        Subtracts one compressed matrix from another.

        :param subtract_matrix: CompressedMatrix to subtract
        :return: A new CompressedMatrix instance representing the result of the subtraction
        """
        if self.total_rows != subtract_matrix.total_rows or self.total_cols != subtract_matrix.total_cols:
            raise ValueError(f"Cannot subtract matrices with different dimensions.")
        
        diff_matrix = CompressedMatrix(self.total_rows, self.total_cols)
        
        # Subtract elements of the second matrix from the first
        for key, val in subtract_matrix.matrix_data.items():
            row, col = map(int, key.split(','))
            diff_matrix.update_value(row, col, self.retrieve_value(row, col) - val)
        
        return diff_matrix

    def matrix_multiply(self, other_matrix):
        """
        Multiplies two compressed matrices.

        :param other_matrix: CompressedMatrix to multiply
        :return: A new CompressedMatrix instance representing the result of the multiplication
        """
        if self.total_cols != other_matrix.total_rows:
            raise ValueError(f"Cannot multiply: the number of columns in the first matrix must equal the number of rows in the second.")
        
        product_matrix = CompressedMatrix(self.total_rows, other_matrix.total_cols)

        for first_key, first_val in self.matrix_data.items():
            row1, col1 = map(int, first_key.split(','))
            for second_key, second_val in other_matrix.matrix_data.items():
                row2, col2 = map(int, second_key.split(','))
                if col1 == row2:
                    product_matrix.update_value(row1, col2, product_matrix.retrieve_value(row1, col2) + first_val * second_val)
        
        return product_matrix

    def __str__(self):
        """
        Returns a string representation of the compressed matrix.

        :return: String representation of the matrix
        """
        result = [f"rows={self.total_rows}", f"cols={self.total_cols}"]
        for key, val in self.matrix_data.items():
            row, col = key.split(',')
            result.append(f"({row}, {col}, {val})")
        return '\n'.join(result)

    def save_matrix(self, output_path):
        """
        Saves the compressed matrix to a file.

        :param output_path: Path to save the matrix
        """
        with open(output_path, 'w') as file:
            file.write(str(self))


def prompt_user(message):
    """
    Gets user input from the console.

    :param message: The prompt to display
    :return: User input as a string
    """
    return input(message)


def perform_matrix_operations():
    """
    Performs matrix operations based on user input.
    """
    try:
        available_operations = {
            '1': ('addition', 'matrix_add'),
            '2': ('subtraction', 'matrix_subtract'),
            '3': ('multiplication', 'matrix_multiply')
        }

        print("Available MATRIX Operations: ")
        print("(1) Addition")
        print("(2) Subtraction")
        print("(3) Multiplication")

        selected_op = prompt_user("Select operation (1,2,3): ")
        if selected_op not in available_operations:
            raise ValueError("Invalid selection.")

        matrix_file1 = prompt_user("Enter path for the first matrix file: ")
        matrix_file2 = prompt_user("Enter path for the second matrix file: ")

        print(f"Loading first matrix from {matrix_file1}...")
        first_matrix = CompressedMatrix.import_from_file(matrix_file1)
        print(f"Loaded matrix size {first_matrix.total_rows}x{first_matrix.total_cols}")

        print(f"Loading second matrix from {matrix_file2}...")
        second_matrix = CompressedMatrix.import_from_file(matrix_file2)
        print(f"Loaded matrix size {second_matrix.total_rows}x{second_matrix.total_cols}")

        operation_name, operation_method = available_operations[selected_op]
        print(f"Performing {operation_name}...")

        operation_result = getattr(first_matrix, operation_method)(second_matrix)
        result_file = f"{operation_name}_output.txt"
        operation_result.save_matrix(result_file)

        print(f"{operation_name.capitalize()} completed successfully. Output saved to {result_file}.")
    except Exception as error:
        print(f"Error: {str(error)}")


if __name__ == "__main__":
    perform_matrix_operations()
