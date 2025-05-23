# InfoViz-league
Repository for the assignment of the Information Visualization course.
The assignments aims to do a visualization of a chosen dataset. Our dataset is: https://www.kaggle.com/datasets/chuckephron/leagueoflegends/data
## Considerations
We are in no way affiliated with Riot Games or in any way endorsed by them. This is a university project done in the context of a Information Visualization course. The dataset we used is publicly available on [kaggle](https://www.kaggle.com/datasets/chuckephron/leagueoflegends/data).

Some of the game assets available on the community backed cdn were used (and slightly modified) in the making of some visualizations.

The minimap image used is from [this post](https://www.reddit.com/r/leagueoflegends/comments/pl92ho/vector_map_of_summoners_rift_wip/).

## Assignment related formailities
Some commits have been made between the presentation and the current state of the repository. Rest assured that these are not groundbreaking changes and you won't see a difference because of those compared to the presentation held on Thursday (22.05.2025), except for the "winrate" visual, which was fixed right after the presentation!

The rest of the changes are formalities relating to the creation of the packaged version of the executable (library additions to the toml, changing path names and adding the possible reduction to the preprocessing plus addition of the dist folder and user manual) and updating of this readme file.

**If you want to get the absolutely exact state of things from Thursday you can use the "Thursday" branch!** But as mentioned earlier, it won't make much of a difference.
# Running the applications
There are 2 ways of running the application. One using a prebuilt and packaged executable, one running it using a Python installation.
## Executable
There is an executable in the `dist` folder along with an user manual (given to the evaluation participants). running the exe will run the application with the reduced dataset (see "Datasets" hereunder)
## Developers
This method is only recommended if you know what you're doing and planning on using an extended or own dataset.
### Requirements
- We use [uv](https://docs.astral.sh/uv/) for package management.
  - `pip install uv`
  - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- python >=  3.12
### Getting started
To install all the dependencies simply run `uv sync` in the repository directory. This will create a .venv file in your repository root, can activate it by using:
- Windows: `.\.venv\Scripts\activate` 
- Linux/MacOS: `source venv/bin/activate`

Once the the environment is ready you need to get the dataset. The application was built with the aforementioned dataset from kaggle in mind. Make sure you download it and put the csv files in a `data` folder in the repository root.

Before running the app you should run our data preprocessing script. To do so so run `src/data_prep.py` from the repository root. 
> If you're having issues activating the venv. You can also explicitly run python through uv, simply use `uv run python src/data_prep.py` from the root.

Once the preprocessing is done you can run `src/app.py`.
#### Datasets
`data_prep` offers two preprocessing options, you can chose which to use, by changing the global variable `REDUCE` in the Python file.
- `REDUCE = False`: Is the default, it will do the simple data preprocessing. This will create new versions of the csv files appended by a `_mod` in the name, used by our application. 
- `REDUCE = True`: Can be activated to apply a reduction on the datasets on top of the usual preprocessing. Specifically it filters out the data from before 2017. The created files have the original names appended by an `_r`. **If you want to use the reduced dataset, rename these files to have a `_mod` at the end instead of `_r`!**

In conclusion: The app will nee the following csv files in `data/`:
- `matchinfo_mod.csv`
- `kills_mod.csv`
- `structures_mod.csv`
- `monsters_mod.csv`
- `gold_mod.csv`
- `champ_ids_mod.csv`
#### Internet
Some visualization get images from an online cdn and might not work if you are not connected to the internet. This is the case for any visualizations using champion images.


