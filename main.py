from parser import parse_file
import validate

if __name__ == "__main__":
    data = parse_file("01_linear_path.txt")

    validate.validate_data(data)
    print(data)
