# main.py
import platform
import pandas as pd

def main() -> None:
    print(f"Python version: {platform.python_version()}")
    print(f"Pandas version: {pd.__version__}")
    print("Docker environment is working correctly!")

if __name__ == "__main__":
    main()