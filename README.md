Also check the pygammon documentation https://pygammon.readthedocs.io/en/latest/protocol.html#. This one page should be enough

# How to play the game 

## Install and run 

1. Clone the repository and move into the project folder:

```bash
git clone <your-repo-url>
cd backgammon
```

2. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies used by the project:

```bash
pip install pygammon pillow tqdm
```

4. Install Ghostscript (required by the renderer snapshot export via Pillow/PostScript):

```bash
brew install ghostscript
```

5. Run the game:

```bash
python main.py
```

## Play as a human (using `ai/human_input_ai.py`)

`main.py` currently creates `Game()` with default AI classes. To play manually, edit the bottom of `main.py` and pass `HumanInputAI` for the side you want to control.

Example (human as FIRST, and which ever AI you want to play against as SECOND):

```python
from ai.human_input_ai import HumanInputAI
from ai.random_ai import RandomAI

#or any other AI class


#Inside main.py change first_ai_cls to HumanInputAI, and second_ai_cls to the AI you want to play against.
#line 16-17
self.firstAi = first_ai_cls(Side.FIRST)
self.secondAi = second_ai_cls(Side.SECOND)
```
Then run:

```bash
python main.py
```
During your turn, the game prints all legal move sequences and asks you to enter the move index. 

## How to simulate games (`simulate_games.py`)

`simulate_games.py` runs repeated AI-vs-AI matches by repeatedly launching `main.py` and counting who wins.

#main.py needs to be reset to: 
self.firstAi = first_ai_cls(Side.FIRST)
self.secondAi = second_ai_cls(Side.SECOND)

```bash
python simulate_games.py
```

To change the matchup (which AIs play as FIRST/SECOND), edit the defaults at the bottom of `simulate_games.py` (the `run_match(...)` )

# main.py
Provides functions do_move_handler and current_game_state_handler for the pygammon engine. 

current_game_state_handler() updates the used Ai with the new game state, dice rolls etc... also renders the game using renderer

do_move_handler() asks Ai to move by calling move(), each move needs to be returned separately so if, player has 4 moves (rolled two same numbers)
the function move is called 4 times and each time it is required to return a single move. Check move() in ai_abstract.py / greedy_best_first_ai.py to see how it is handled

The two Ais playing the game are specified in the __init__ function of Game class and can be replaced by any other class
that extend the AiAbstract and implement method move()

# game_state_generator.py
now has two public functions restore_token() and move() they accept the current game state and an action and check if the action is possible.
If the action is possible they return the object of PossibleGameState(check what it contains). If the move is not possible they throw an exception.

# Ai
There is an abstract class ai_abstract.py that offers shared functionality, is used to get the game state updated. Each new Ai class
should as minimum extend the AiAbstract and implement method move.

The AbstractAi class has a method _get_all_possible_moves_one_die() that generates all of the possible game states that can result by playing given dice
in the current game state. There is little logic and it basically just asks the game_state_generator.py whether move is possible for every token.
If the generator throws error then it is ignored, if it returns object of PossibleGameState it is added to the rest of the possible moves.

method get_all_possible_moves() generates all the possible moves by using _get_all_possible_moves_one_die() in different order of dices.
((0,1),(1,0), (0,0,0,0) if same number of dice -> 4 moves)


# game_state_dict.py
A data structure for storing game states that ensures that there cannot be duplicates. Each duplicate is discarded.


# Tasks

My recommendations how I would try to do it, feel free to ignore all that I write below and try different ideas, stuff. 

## Finishing the framework for generation moves - Julius
Check the pygammon documentation, because you will need to interact with the engine, return correct format of move, handle game end 

Implement method borne_token in game_state_generator.py that returns a PossibleGameState. And use it in _get_all_possible_moves_one_die() in AiAbstract. 
Check the current functions in game_state_generator.py to get inspiration. Do not forget that tokens can be borne only after 
all of them are moved to the last quarter of the board.

Implement handling of OutputType.GameWon in main.py current_game_state_handler(). It can be anything, printing to console, updating ui ...

Fix the behavior when only one move or no move is possible in get_all_possible_moves() in AiAbstract.

Check that basicAi to be able to finish the game to test. You should not need to change much there.

## Evaluation function - Vita
Do not have much to advise here. Make a method/methods that accepts object of GameState (from pygammon import GameState) and return int value. You can experiment with creating new AIs
that uses it

You can try to collaborate with Asger because you can measure the value of the board as chance of reaching better board in next turns

## Stochastic generation - Asger
Make new method/methods in AiAbstract that utilize _get_all_possible_moves_one_die() in AiAbstract for each possible combinations of dices that can occur in next turn.
For each possible game state it should return the chance of reaching the state. You can experiment with different depths, etc... 

You can try to collaborate with Vita because she can measure the value of the board as chance of reaching next board

### Stochastic generation (simple notes) Asger

This is now implemented in `ai/ai_abstract.py`.

Think of it like this:

- We do not know the next dice roll yet.
- So we try all possible dice results.
- For each result, we generate all legal end-board states.
- Then we assign a probability ("chance") to each end-board state.

#### Main methods

- `get_all_possible_moves_for_side(game_state, dice, side)`
  - Same idea as `get_all_possible_moves`, but for any side (FIRST or SECOND).
  - Useful when simulating the opponent.

- `generate_next_turn_state_distribution(game_state, side, move_policy="uniform", state_evaluator=None)`
  - Returns a dictionary: `state_key -> probability`.
  - This is for one full turn (one player move turn).

- `generate_state_distribution_n_ply(game_state, side_to_move, depth, move_policy="uniform", state_evaluator=None)`
  - Same as above, but repeated for more turns (`depth` plies).
  - Alternates player side every ply.

#### Policies (important)

- `move_policy="uniform"`:
  - If there are many legal end states for one dice result, split that dice chance evenly between them.

- `move_policy="best"`:
  - Pick one best end state for that dice result (using `state_evaluator`).
  - Give all that dice chance to the chosen state.

#### Dice chances used

- doubles like `(3,3)`: `1/36`
- non-doubles like `(2,5)`: `2/36`

#### Quick example

```python
distribution = self.generate_next_turn_state_distribution(self.game_state, Side.SECOND)
print("reachable states:", len(distribution))
print("sum of chances:", sum(distribution.values()))  # should be close to 1.0
```

Best-policy example:

```python
distribution = self.generate_next_turn_state_distribution(
    self.game_state,
    Side.SECOND,
    move_policy="best",
    state_evaluator=lambda state, side: self.heuristic(state),
)
```

#### Team assumptions

- We track chance of final board states (not chance of exact move sequences).
- If two paths end in the same board state, their probabilities are added together.
- If a die cannot be played in a path, that path keeps the same state and continues with the next die.