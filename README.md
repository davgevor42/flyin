*This project has been created as part of the 42 curriculum by davgevor.*

# Fly-in

## Description

Fly-in routes a fleet of drones from a start zone to an end zone through a
network of connected zones, in as few simulation turns as possible.

The network is read from a text file. Zones have a type (`normal`,
`priority`, `restricted`, `blocked`), an optional color and a capacity
(`max_drones`). Connections are bidirectional and have a capacity
(`max_link_capacity`). The program computes the paths, plays the simulation
turn by turn, prints one line per turn, and shows the result in a window.

Rules respected by the simulation:

- a normal or priority zone costs 1 turn, a restricted zone costs 2 turns,
  a blocked zone cannot be entered;
- a zone holds at most `max_drones` drones (start and end are unlimited);
- a connection carries at most `max_link_capacity` drones per turn;
- a drone that leaves for a restricted zone must arrive on the next turn;
- all moves of a turn are decided from the state at the start of the turn,
  and a space freed this turn can be used by another drone this turn.

## Instructions

Requirements: Python 3.10 or later (tkinter is needed for the window).

```bash
make install                      # installs flake8 and mypy
make run MAP=maps/easy/01_linear_path.txt
make debug MAP=maps/easy/01_linear_path.txt   # runs under pdb
make lint                         # flake8 + mypy
make clean
```

or directly:

```bash
python3 main.py <map_file>
```

The program prints `Error: ...` and exits with code 1 for an unreadable
file, an invalid map (with the line number and the cause) or a map with no
path between start and end.

### Example

Input (`example.txt`):

```
nb_drones: 2
start_hub: s 0 0
end_hub: g 1 0
connection: s-g [max_link_capacity=2]
```

Output (one line per turn):

```
D1-g D2-g
```

A drone going to a restricted zone `r` from `a` is written `D1-a-r` on the
turn it leaves and `D1-r` on the turn it arrives.

## Algorithm

The work is done once, when the `Simulation` is created.

1. **Finding candidate paths.** Dijkstra's algorithm is run several times
   (between 10 and 200 times depending on the number of drones). The cost of
   entering a zone is its movement cost. On equal distance the path with more
   priority zones wins. After every run, the inner zones of the path found
   get a penalty, so the next run looks for a different route. Duplicate
   paths are dropped. Enumerating all paths is avoided because their number
   grows exponentially.
2. **Path properties.** Each path stores its cost, its number of priority
   zones and its capacity, which is the smallest `max_link_capacity` or
   `max_drones` along it (the narrowest point).
3. **Distributing the drones.** For each `k`, the drones are assigned one by
   one to the `k` best paths. Each drone takes the path where it is expected
   to arrive first: `cost + assigned_drones // capacity`.
4. **Choosing `k`.** Every `k` is simulated silently (`dry_run`) and the
   fastest is kept.
5. **Hill climbing.** One drone at a time is moved from a path to another;
   the change is kept only if the simulation becomes strictly faster.
   Drones with the longest paths leave first.
6. **Turn simulation.** Each turn: drones in flight land; the others propose
   the next zone of their path; proposals are accepted in a loop, repeated
   while something changes, so a whole column of drones can advance in one
   turn; zone and connection capacities are checked on accepted moves only.
7. **Optimistic and strict mode.** In optimistic mode a drone may leave for
   a restricted zone without checking room there, because room is checked on
   arrival; plans that fail are rejected by the silent run. If no plan
   works, the strict mode checks room immediately.
8. **Deadlocks.** A turn where nobody moves but drones remain stops the
   simulation with an error instead of looping forever.

### Complexity

Dijkstra uses a linear search for the next zone and a linear search for
the neighbours, so one run is about O(V² + V·E). It runs at most 200
times. Paths are computed once and cached in `path_infos`; they are not
recalculated during the simulation. Memory is O(V + E) for the map plus
the stored paths and one path copy per drone.

### Results on the provided maps

All maps run in well under a second and pass an independent rule checker.
Every map reaches the reference optimum, including the challenger map
(43 turns), except `easy/02_simple_fork`, which takes 5 turns instead of 4
(within 25%).

## Visual representation

A tkinter window draws the network:

- zones are circles filled with the color from the map (unknown or missing
  colors are drawn white, `rainbow` is drawn as nested circles);
- connections are lines between zones;
- drones are numbered triangles; a drone crossing a restricted connection
  is drawn halfway between the two zones;
- the **Next Step** button plays one turn and a label shows the turn number;
- the map is scaled and centered to fit the window, and is redrawn when the
  window is resized.

Seeing where drones queue and which paths they choose makes it easy to
understand why a map needs a given number of turns. The turn lines are also
printed in the terminal.

## Resources

- Dijkstra's algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Python tkinter documentation: https://docs.python.org/3/library/tkinter.html
- PEP 257 (docstrings): https://peps.python.org/pep-0257/
- mypy documentation: https://mypy.readthedocs.io/
- flake8 documentation: https://flake8.pycqa.org/

**Use of AI.** I used an AI assistant (Claude) as a guide while building and
understanding this project. It helped me to:

- understand the subject and break the problem into steps (parsing,
  validation, pathfinding, turn simulation, visualization);
- understand and compare algorithm options, such as penalized Dijkstra runs
  instead of listing all paths, and how the simulation checks capacities;
- review my code, find bugs and fix typing errors reported by mypy and
  flake8;
- improve the visualizer, the docstrings and the draft of this
  README;
- build a separate rule checker and test maps, used only for my own testing
  and not part of the submission.