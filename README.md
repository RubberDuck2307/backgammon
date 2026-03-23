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

Pygammon should no longer be needed, but there may be a forgotten import somewhere.


4. Install Ghostscript (optional, required by the renderer.py to export snapshots via Pillow/PostScript):


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

During your turn, the game prints all legal move sequences and asks you to enter the move index. 

## How to simulate games (`simulation.py`)

configure simulations at bottom of `simulation.py` and run the file
