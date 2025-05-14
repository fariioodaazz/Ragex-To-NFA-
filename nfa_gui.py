# --- Imports ---
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import graphviz
from graphviz import Source
from io import BytesIO

# --- NFA Logic ---
class NFA:
    """Represents a Non-deterministic Finite Automaton (NFA)."""
    def __init__(self, start_state, accept_state, transitions=None):
        self.start_state = start_state
        self.accept_state = accept_state
        self.transitions = transitions if transitions is not None else {}

    def add_transition(self, from_state, symbol, to_state):
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = set()
        self.transitions[from_state][symbol].add(to_state)

    def to_graphviz(self):
        dot = "digraph NFA {\n"
        dot += "  rankdir=LR;\n"
        dot += "  node [shape=circle, fontname=\"Arial\"];\n"
        dot += f"  dummy [label=\"\", shape=none];\n"
        dot += f"  dummy -> {self.start_state};\n"

        all_states = set(self.transitions.keys())
        for transitions in self.transitions.values():
            for dests in transitions.values():
                all_states.update(dests)
        all_states.add(self.accept_state)

        for state in sorted(all_states):
            shape = 'doublecircle' if state == self.accept_state else 'circle'
            dot += f"  {state} [shape={shape}];\n"

        edges = {}
        for from_state, symbols in self.transitions.items():
            for symbol, to_states in symbols.items():
                for to_state in to_states:
                    key = (from_state, to_state)
                    if key not in edges:
                        edges[key] = []
                    edges[key].append('ε' if symbol == 'ε' else symbol)

        for (from_state, to_state), labels in edges.items():
            label_text = ",".join(labels)
            dot += f"  {from_state} -> {to_state} [label=\"{label_text}\"];\n"

        dot += "}\n"
        return dot



# --- Helper Functions for Conversion ---
def expand_character_classes(regex):
    """Expand character classes like [a-z] or [0-9] into (a|b|c|...|z)."""
    i = 0
    expanded = ''
    while i < len(regex):
        if regex[i] == '[':
            j = i + 1
            while j < len(regex) and regex[j] != ']':
                j += 1
            if j == len(regex):
                raise ValueError("Unmatched [ in regex")
            content = regex[i+1:j]
            if '-' in content and len(content) == 3:  
                start, dash, end = content
                if dash != '-':
                    raise ValueError("Invalid character class")
                chars = [chr(c) for c in range(ord(start), ord(end)+1)]
                expanded += '(' + '|'.join(chars) + ')'
            else:
                raise ValueError("Only simple ranges like [a-z] supported")
            i = j + 1
        else:
            expanded += regex[i]
            i += 1
    return expanded

def infix_to_postfix(regex):
    """Convert infix regular expression to postfix with explicit concatenation."""
    explicit = []
    length = len(regex)
    for i in range(length):
        c = regex[i]
        explicit.append(c)
        if i < length - 1:
            nxt = regex[i + 1]
            if (c not in ['(', '|']) and (nxt not in [')', '|', '*', '+', '?']):
                explicit.append('.')
    regex = "".join(explicit)

    output = []
    stack = []
    precedence = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1, '(': 0}

    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif char in precedence:
            while stack and precedence[stack[-1]] >= precedence[char]:
                output.append(stack.pop())
            stack.append(char)
        else:
            output.append(char)

    while stack:
        output.append(stack.pop())
    
    return "".join(output)

def postfix_to_nfa(postfix):
    """Builds NFA from postfix regular expression."""
    next_state_id = [0]

    def new_state():
        s = next_state_id[0]
        next_state_id[0] += 1
        return s

    stack = []

    for char in postfix:
        if char not in ['*', '+', '?', '.', '|']:
            start = new_state()
            accept = new_state()
            nfa = NFA(start, accept)
            nfa.add_transition(start, char, accept)
            stack.append(nfa)
        elif char == '*':
            nfa1 = stack.pop()
            start, accept = new_state(), new_state()
            nfa = NFA(start, accept, dict(nfa1.transitions))
            nfa.add_transition(start, 'ε', nfa1.start_state) #ε-transition to start state
            nfa.add_transition(nfa1.accept_state, 'ε', nfa1.start_state) #repetition
            nfa.add_transition(start, 'ε', accept) #ε-transition to accept state (skip)
            nfa.add_transition(nfa1.accept_state, 'ε', accept) #ε-transition to accept state 
            stack.append(nfa)
        elif char == '+':
            nfa1 = stack.pop()
            start, accept = new_state(), new_state()
            nfa = NFA(start, accept, dict(nfa1.transitions))
            nfa.add_transition(start, 'ε', nfa1.start_state)
            nfa.add_transition(nfa1.accept_state, 'ε', nfa1.start_state)
            nfa.add_transition(nfa1.accept_state, 'ε', accept)
            stack.append(nfa)
        elif char == '?':
            nfa1 = stack.pop()
            start, accept = new_state(), new_state()
            nfa = NFA(start, accept, dict(nfa1.transitions))
            nfa.add_transition(start, 'ε', nfa1.start_state)
            nfa.add_transition(nfa1.accept_state, 'ε', accept)
            nfa.add_transition(start, 'ε', accept)
            stack.append(nfa)
        elif char == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa = NFA(nfa1.start_state, nfa2.accept_state, dict(nfa1.transitions))
            for state, transitions in nfa2.transitions.items():
                if state not in nfa.transitions:
                    nfa.transitions[state] = {}
                for symbol, destinations in transitions.items():
                    nfa.transitions[state][symbol] = destinations.copy()
            nfa.add_transition(nfa1.accept_state, 'ε', nfa2.start_state)
            stack.append(nfa)
        elif char == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start, accept = new_state(), new_state()
            nfa = NFA(start, accept, dict(nfa1.transitions))
            for state, transitions in nfa2.transitions.items():
                if state not in nfa.transitions:
                    nfa.transitions[state] = {}
                for symbol, destinations in transitions.items():
                    nfa.transitions[state][symbol] = destinations.copy()
            nfa.add_transition(start, 'ε', nfa1.start_state)
            nfa.add_transition(start, 'ε', nfa2.start_state)
            nfa.add_transition(nfa1.accept_state, 'ε', accept)
            nfa.add_transition(nfa2.accept_state, 'ε', accept)
            stack.append(nfa)
    return stack.pop()

def regex_to_nfa(regex):
    """Full conversion from infix regex to NFA object."""
    regex = expand_character_classes(regex)
    postfix = infix_to_postfix(regex)
    return postfix_to_nfa(postfix)

# --- GUI Functions ---
def generate_nfa_gui():
    expr = entry.get().strip()
    if not expr:
        messagebox.showerror("Error", "Please enter a regular expression")
        return
    try:
        nfa_obj = regex_to_nfa(expr)
        dot = nfa_obj.to_graphviz()
        graph = Source(dot)
        graph.render('nfa_graph', format='png', cleanup=True)

        img = Image.open("nfa_graph.png")


        max_width, max_height = 1000, 1000
        img.thumbnail((max_width, max_height), Image.LANCZOS)

        img_tk = ImageTk.PhotoImage(img)

        panel.config(image=img_tk)
        panel.image = img_tk


        transitions_info = []
        for from_state, symbols in sorted(nfa_obj.transitions.items()):
            for symbol, to_states in sorted(symbols.items()):
                for to_state in sorted(to_states):
                    transitions_info.append(f"{from_state} --{symbol}--> {to_state}")
                    
        output_text.set(
            f"Start: {nfa_obj.start_state}\nAccept: {nfa_obj.accept_state}\nTransitions:\n" + "\n".join(transitions_info)
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))


def clear_gui():
    entry.delete(0, tk.END)
    output_text.set("")
    panel.config(image='')

def exit_app():
    root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("Regex to NFA Converter")

tk.Label(root, text="Enter Regular Expression:").pack()
entry = tk.Entry(root, width=40)
entry.pack()

tk.Button(root, text="Generate NFA", command=generate_nfa_gui).pack()
output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text, justify="left")
output_label.pack()

panel = tk.Label(root)
panel.pack()

tk.Button(root, text="Clear", command=clear_gui).pack()
tk.Button(root, text="Exit", command=exit_app).pack()

root.mainloop()
