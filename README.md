# Regex to NFA Converter (GUI)

This project is a Python-based tool that allows users to input a **regular expression** and visualize its corresponding **Non-deterministic Finite Automaton (NFA)**. The application features a graphical user interface (GUI) built using Tkinter and visualizes the NFA using the Graphviz library.

## Features

- Accepts regular expressions with support for:
  - Concatenation (implicit)
  - Alternation (`|`)
  - Kleene star (`*`)
  - Plus (`+`)
  - Optional (`?`)
  - Character classes (e.g., `[a-z]`)
- Converts infix regular expressions to postfix notation.
- Constructs NFAs using Thompson's construction algorithm.
- Visualizes the NFA graph using Graphviz and displays it directly in the GUI.
- Displays detailed NFA transitions (states and transitions).
- Simple, interactive GUI for ease of use.

## GUI Overview

- Input field for the regular expression
- "Generate NFA" button to process and display the result
- Graphical display of the NFA
- Textual display of the start state, accept state, and all transitions
- "Clear" and "Exit" buttons for managing input and exiting the program

## Example

For the input regular expression:

```
(a|b)*abb
```

The program generates and displays an NFA accepting the language that matches this regex.

## Requirements

- Python 3.x
- Required Python packages:
  - `tkinter` (usually included with Python)
  - `Pillow` (for image handling)
  - `graphviz` (Python bindings)
- **Graphviz** system installation is also required for rendering:
  - Download from: https://graphviz.org/download/

Install the required Python packages:

```bash
pip install pillow graphviz
```

Ensure that the Graphviz binaries are accessible via system PATH (especially on Windows).

## How to Run

1. Clone or download this repository.
2. Ensure all dependencies are installed.
3. Run the Python file:

```bash
python your_filename.py
```

## How it Works

1. **Regex Parsing**: Supports simple character classes like `[a-z]` and converts infix to postfix notation.
2. **NFA Construction**: Uses Thompson's construction to build an NFA from the postfix regex.
3. **Graph Visualization**: Converts the NFA into a Graphviz DOT format, renders it as an image, and displays it in the GUI.

## Limitations

- Character classes only support simple ranges like `[a-z]`.
- Doesn't currently support escaped characters (like `\*` or `\.`).
- No support for full regex features like lookaheads or backreferences.

## License

This project is open-source and free to use. You can modify or adapt it for personal or educational purposes.

