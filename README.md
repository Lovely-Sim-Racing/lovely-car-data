<p align="center">
<img width="150" height="150" alt="Lovely Sim Racing" src="docs/images/lr-team-icon.png">
</p>

<h1 align="center">Lovely Car Data</h1>

<p align="center">
A comprehensive list of Car Data for Sim Racing games.<br>
<strong>File Format v1.0.0</strong>
</p>

---

## How to
Fetch the data by retrieving the url:
`/data/{simId}/{carId}.json`

* `{simId}` is the lowercase Simhub game id `DataCorePlugin.CurrentGame`
* `{carId}` is the lowercase Simhub car id `DataCorePlugin.CarId`

## Changelog
Read the [changelog](changelog.md) to keep track of the format updates.

## File Format
Every file is formatted as follows:

``` 
# name                (String) - The full human readable car name
# class               (String) - The car's 3-5 letter class shorthand
# ledNumber           (Int)    - The car's in game number of telemetry LED's
# ledColor                       An array of the led color
  # redline(:Value)   (String) - A color name or HEX value for the red line
  # led1color(:Value) (String) - A color name or HEX value for LED 1
  # led2color(:Value) (String) - A color name or HEX value for LED 2
  # led3color(:Value) (String) - A color name or HEX value for LED 3
  # ledNcolor(:Value) (String) - A color name or HEX value for LED N
# ledRpm                         An array of all the RPM data per gear
  # gear(:Key)        (String) - The gear number
    # redline(:Value) (Int)    - The RPM red line value per gear
    # led1rpm(:Value) (Int)    - The RPM value for LED 1
    # led2rpm(:Value) (Int)    - The RPM value for LED 2
    # led3rpm(:Value) (Int)    - The RPM value for LED 3
    # ledNrpm(:Value) {Int)    - The RPM value for LED N
```

## Color Names
To preserve consistency among LED profiles, you can use any of the offical **HTML Color Names** as listed in the [W3 Schools HTML Color Names](https://www.w3schools.com/tags/ref_colornames.asp) list or add you custom **HEX RGB** color code.

## Contributing
To maintain properly formatted files, I've implemented - and require - a `pre-commit` script, that will prettify the JSON files and thus properly track changes to them.

### 1. Install Pre-Commit Hook
Before you can run hooks, you need to have the pre-commit package manager installed. You can do so by following the instructions on the [official pre-commit website](https://pre-commit.com/#installation), or just install it using the following command:

```
brew install pre-commit
```

Homebrew not your thing? Read more on the [official pre-commit website](https://pre-commit.com/#installation).


### 2. Install Git Hook Scripts

Once installed, run `pre-commit install` to set up the git hook scripts

```
pre-commit install
```

### 3. Test & Finish
You're all set as far as tooling is concerned. Every time you make a commit, the `pre-commit` script will make sure the files are properly formatted and are prettified. 

It's usually a good idea to run the hooks against all of the files when adding new hooks (usually pre-commit will only run on the changed files during git hooks). Running `pre-commit run --all-files` will have a pass at everythig, and if all is well, you should see somthing like the below. 

```
$ pre-commit run --all-files
check json...............................................................Passed
pretty format json.......................................................Passed
```
