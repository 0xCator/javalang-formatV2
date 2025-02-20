import re

def to_pascal_case(text):
    """Converts to PascalCase. Handles mixed case and delimiters correctly."""

    if not re.search(r"[ _-]", text):  
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text) 
    text = re.sub(r"[ _-]+", " ", text).strip() 
    return "".join(word.capitalize() for word in text.split())

def to_camel_case(text):
    """Converts a string to camelCase."""
    pascal_case = to_pascal_case(text)
    return pascal_case[0].lower() + pascal_case[1:] if pascal_case else ""


if __name__ == "__main__":
    test_cases = [
        "  bad  naming  ",
        "bad-naming",
        "bad_naming",
        "bad__naming",
        "bad--naming",
        "bad - naming",
        "BadNaming", 
        "badNaming", 
        "  Mixed_Case-Naming  ",
        "123InvalidStart", 
        "",  
        "   ",
        "special!characters#", 
        "Bad     Name With    Multiple      Spaces",
        "testthatmethod",  # The crucial test case!
        "TestThatMethod", # Already PascalCase
        "testThatMethod", # Already camelCase
        "anotherTestExample" # Another mixed case example
    ]

    for test_case in test_cases:
        pascal = to_pascal_case(test_case)
        camel = to_camel_case(test_case)
        print(f"Input: '{test_case}'")
        print(f"PascalCase: '{pascal}'")
        print(f"camelCase: '{camel}'")
        print("-" * 20)

    # Example usage (you can customize this)
    input_string = "  my_bad-naming  "
    pascal_case_result = to_pascal_case(input_string)
    camel_case_result = to_camel_case(input_string)

    print(f"\nExample:")
    print(f"Input: '{input_string}'")
    print(f"PascalCase: '{pascal_case_result}'")
    print(f"camelCase: '{camel_case_result}'")