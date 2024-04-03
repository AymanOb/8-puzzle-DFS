import tkinter as tk
from tkinter import messagebox
import time
import random

GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Define the PuzzleNode class to represent states in the puzzle
class PuzzleNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(tuple(self.state))

    def __str__(self):
        return str(self.state)

    def is_goal(self):
        return self.state == GOAL_STATE

# Define the PuzzleGUI class for the graphical user interface
class PuzzleGUI:
    def __init__(self, master):
        # Initialize the GUI
        self.master = master
        self.master.title("8-Puzzle Game")

        # Generate a solvable initial state for the puzzle
        self.initial_state = self.generate_solvable_state()
        self.current_state = PuzzleNode(self.initial_state)
        self.game_over = False

        # Create GUI elements
        self.create_widgets()

        # Draw the initial puzzle state
        self.draw_puzzle()

        # Record the start time for the timer
        self.start_time = time.time()

        # Update the timer display
        self.update_timer()

        # Solve the puzzle using IDDFS
        self.solve_with_iddfs()

    def create_widgets(self):
        # Create a canvas to draw the puzzle
        self.canvas = tk.Canvas(self.master, width=300, height=300, bg="#EADDCA")
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Create a label to display the timer
        self.timer_label = tk.Label(self.master, text="", font=("Helvetica", 12), fg="red")
        self.timer_label.grid(row=1, column=0, columnspan=3)

    def generate_solvable_state(self):
        # Generate a random solvable state for the puzzle
        numbers = list(range(9))
        random.shuffle(numbers)

        # Ensure the generated state is solvable
        while not self.is_solvable(numbers):
            random.shuffle(numbers)

        return tuple(numbers)

    def is_solvable(self, state):
        # Check if the generated state is solvable
        inversion_count = 0
        for i in range(8):
            for j in range(i + 1, 9):
                if state[i] > state[j] and state[i] != 0 and state[j] != 0:
                    inversion_count += 1

        # If the inversion count is even, the puzzle is solvable
        return inversion_count % 2 == 0

    def draw_puzzle(self):
        # Draw the current puzzle state on the canvas
        self.canvas.delete("all")
        cell_size = 100

        for i in range(3):
            for j in range(3):
                index = i * 3 + j
                number = self.current_state.state[index]
                x, y = j * cell_size, i * cell_size
                background_color = "#FFAC1C" if number != 0 else "#6E260E"

                # Draw puzzle cell
                self.canvas.create_rectangle(
                    x, y, x + cell_size, y + cell_size,
                    fill=background_color, outline="#6E260E", width=3
                )

                if number != 0:
                    # Draw number in the cell
                    self.canvas.create_text(
                        x + cell_size // 2, y + cell_size // 2,
                        text=str(number), font=("Helvetica", 24), fill="black"
                    )

    def perform_move(self, state, action):
        # Perform a move in the puzzle
        blank_index = state.index(0)
        state_list = list(state)
        state_list[blank_index], state_list[action] = state_list[action], state_list[blank_index]
        return tuple(state_list)

    def solve_with_iddfs(self):
        # Solve the puzzle using Iterative Deepening Depth-First Search (IDDFS)
        depth = 1
        while True:
            result = self.dfs_with_depth(self.current_state, depth, set())
            if result is not None:
                # If the goal state is found, update GUI for solution
                self.update_gui_for_solution(result)
                break
            depth += 1

    def dfs_with_depth(self, node, depth, visited):
        # Depth-limited DFS with a maximum depth
        if node.is_goal():
            return node
        if depth == 0:
            return None
        visited.add(node.state)

        blank_index = node.state.index(0)
        possible_actions = self.get_possible_actions(blank_index)

        for action in possible_actions:
            new_state = self.perform_move(node.state, action)
            child_node = PuzzleNode(new_state, parent=node, action=action)

            if child_node.state not in visited:
                result = self.dfs_with_depth(child_node, depth - 1, visited)
                if result is not None:
                    return result

        return None

    def get_possible_actions(self, blank_index):
        # Get possible actions (moves) for the blank space in the puzzle
        row, col = divmod(blank_index, 3)
        actions = [blank_index - 3, blank_index + 3, blank_index - 1, blank_index + 1]
        return [action for action in actions if 0 <= action < 9 and (action // 3 == row or action % 3 == col)]

    def update_gui_for_solution(self, solution_node):
        # Update the GUI to show the solution path
        moves = []

        while solution_node.parent is not None:
            moves.append(solution_node.action)
            solution_node = solution_node.parent

        moves.reverse()

        # Perform moves to show the solution path
        for move in moves:
            self.current_state = PuzzleNode(self.perform_move(self.current_state.state, move))
            self.draw_puzzle()
            self.master.update()
            self.master.after(500)

        # Display a congratulatory message and destroy the GUI window
        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        messagebox.showinfo("Congratulations", f"You won!\nTime taken: {seconds} seconds.")
        self.master.destroy()

    def update_gui(self):
        # Update the GUI
        self.master.update_idletasks()
        self.master.update()

    def update_timer(self):
        # Update the timer display
        if not self.game_over:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, 60 - elapsed_time)
            minutes, seconds = divmod(int(remaining_time), 60)
            self.timer_label.config(text=f"Time left: {minutes:02d}:{seconds:02d}")

            # Check for game over due to time expiration
            if not self.current_state.is_goal() and remaining_time == 0:
                messagebox.showinfo("Time's Up", "GAME OVER Puzzle Unsolved")
                self.master.destroy()
            else:
                # Schedule the timer to update every 1000 milliseconds (1 second)
                self.master.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    puzzle_gui = PuzzleGUI(root)
    root.mainloop()
