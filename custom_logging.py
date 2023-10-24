# ANSI color codes
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'

def color_text(text, color):
    """Color the text using ANSI escape codes."""
    return f"{color}{text}{RESET}"

def print_message(message, color, message_type):
    """Print a colored message with a message type prefix."""
    colored_message = color_text(message, color)
    print(f"[{message_type}] {colored_message}")

def print_error(message):
    """Print an error message in red."""
    print_message(message, RED, "ERROR")

def print_warning(message):
    """Print a warning message in yellow."""
    print_message(message, YELLOW, "WARNING")

def print_success(message):
    """Print a success message in green."""
    print_message(message, GREEN, "SUCCESS")

# Example usage
# print_error("This is an error message")
# print_warning("This is a warning message")
# print_success("This is a success message")

# Output (everything after the ] is colored):
# [ERROR] This is an error message
# [WARNING] This is a warning message
# [SUCCESS] This is a success message
