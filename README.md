# Trails Through Daybreak LGC Alignment Choices [![Test](https://github.com/ExcaliburZero/trails_through_daybreak_lgc_alignment_choices/actions/workflows/test.yml/badge.svg)](https://github.com/ExcaliburZero/trails_through_daybreak_lgc_alignment_choices/actions/workflows/test.yml)
Analysis of LGC alignment choices in Trails through Daybreak.

## Alignment impact types
During various parts of the game, there are side quests (4SPG) and main story events that increase your alignment score for one or more alignments. This involves both alignment increases for completing a side quest and alignment increases for making specific choices during a side quest or during the main story.

For example, the side quest "Investigate a Friend Who Stole" rewards 1 Law and 1 Grey alignment point upon completition. Additionally, during the side quest there is a choice where you have two options to choose between, one of which grants 5 Law points and the other grants 5 Grey points.

## Credits
LGC alignment impact and choice information is from [ZekeBel's "LGC Alignment Guide"](https://steamcommunity.com/sharedfiles/filedetails/?id=3033273093) on Steam.

https://steamcommunity.com/sharedfiles/filedetails/?id=3033273093

## Installation
### General
```bash
pip install .
```

### Development
```bash
# Setup and activate conda environment (installs the correct Python version)
conda env create -f trails_through_daybreak_lgc_alignment_choices.yml
conda activate trails_through_daybreak_lgc_alignment_choices

# Install library and dev dependencies (ex. linting tools)
pip install -e '.[dev]'
```

## MILP model
WIP: Writing in progress

### Variables

```math
R_{x} = \text{1 if route ``x'' was chosen in Chapter 5, else 0}
```

```math
A_{a_b} = \text{Score of alignment ``a'' at the end of Chapter ``b''}
```

```math
O_{c} = \text{1 if choice ``c'' was chosen, else 0}
```

```math
H_{e} = \text{1 if the correct route was chosen for event ``e'', else 0}
```

### Constraints
Choose exactly one of the routes in Chapter 5.

```math
R_{law} + R_{grey} + R_{chaos} + R_{fourth} = 1
```

Choose exactly one of the choices for each dialog prompt.

```math
\forall_{e \in events} \left(\sum_{c \in e.choices} O_{c}\right) = 1
```

Model the alignment scores at the end of each chapter.

```math
\forall_{a \in \{law, grey, chaos\}} \forall_{c \in \{1, 2, 3, 4, 5, 6, 7\}} A_{ac} = \sum_{e \in \{d \in events \mid d.chapter <= c\}} \left(H_{e} * e.completion.a + H_{e} * \left(\sum_{h \in e.choices} O_c * h.a\right)\right)
```
