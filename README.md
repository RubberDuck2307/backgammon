Also check the pygammon documentation https://pygammon.readthedocs.io/en/latest/protocol.html#. This one page should be enough


# main.py
Provides functions do_move_handler and current_game_state_handler for the pygammon engine. 

current_game_state_handler() updates the used Ai with the new game state, dice rolls etc... also renders the game using renderer

do_move_handler() asks Ai to move by calling move(), each move needs to be returned separately so if, player has 4 moves (rolled two same numbers)
the function move is called 4 times and each time it is required to return a single move. Check move() in basic_ai.py to see how it is handled

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
