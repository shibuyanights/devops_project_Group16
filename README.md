# Students Repository for HSLU Module "DevOps"

The following commands are all ment to be executed in the root directory of the project.

## Mac/Linux
### Run your Script
````
source ../.venv/bin/activate
export PYTHONPATH=$(pwd)
python server/py/hangman.py
python server/py/battleship.py
python server/py/uno.py
python server/py/dog.py
````

### Run the Benchmark
````
source ../.venv/bin/activate
export PYTHONPATH=$(pwd)
python benchmark/benchmark_hangman.py python hangman.Hangman
python benchmark/benchmark_battleship.py python battleship.Battleship
python benchmark/benchmark_uno.py python uno.Uno
python benchmark/benchmark_dog.py python dog.Dog
````

### Start the Server
````
source ../.venv/bin/activate
uvicorn server.py.main:app --reload
````
Open up your browser and go to http://localhost:8000


## Windows
### Run your Script
````
"../.venv\Scripts\activate"
set PYTHONPATH=%cd%                    # in Command Prompt
$env:PYTHONPATH = (Get-Location).Path  # in PowerShell
python server/py/hangman.py
python server/py/battleship.py
python server/py/uno.py
python server/py/dog.py
````

### Run the Benchmark
````
"../.venv\Scripts\activate"
set PYTHONPATH=%cd%                    # in Command Prompt
$env:PYTHONPATH = (Get-Location).Path  # in PowerShell
python benchmark/benchmark_hangman.py python hangman.Hangman
python benchmark/benchmark_battleship.py python battleship.Battleship
python benchmark/benchmark_uno.py python uno.Uno
python benchmark/benchmark_dog.py python dog.Dog
````

### Start the Server
````
"../.venv\Scripts\activate"
uvicorn server.py.main:app --reload
start chrome http://localhost:8000
````