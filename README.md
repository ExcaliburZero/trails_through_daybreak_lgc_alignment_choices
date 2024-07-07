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