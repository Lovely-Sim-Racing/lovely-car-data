<p align="center">
<img width="150" height="150" alt="Lovely Sim Racing" src="docs/images/lr-team-icon.png">
</p>

<h1 align="center">Lovely Car Data</h1>

<p align="center">
A comprehensive list of Car Data for Sim Racing games.<br>
<strong>File Format v2.0.0</strong>
</p>

---

<p align="center">
<strong>A joint project between <a href="https://lsr.gg" target="_blank">Lovely Sim Racing</a>, <a href="https://lsr.gg/atsr" target="_blank">ATSR</a> & <a href="https://lsr.gg/gsi" target="_blank">Gomez Sim Industries</a>,</strong><br/>
with the goal, to bring open and unified sim racing car data to everyone.
</p>

---

## How to
Fetch the data by retrieving the url:
`{version}/data/{simId}/{carId}.json`

* `{version}` is the specific branch of car data. `main` will always have the latest version.
* `{simId}` is the Simhub game id `DataCorePlugin.CurrentGame`
* `{carId}` is the Simhub car id `DataCorePlugin.CarId`

### Manifest
A single root manifest at `data/manifest.json` lists all cars, grouped by game.

Structure:
```
{
  "cars": {
    "{simId}": [
      { "carName": "...", "carId": "...", "path": "{simId}/...json" }
    ]
  }
}
```

- Filter by game using the `{simId}` key in `cars`.
- `path` is relative to `data/` and includes the game folder.

See [scripts/MANIFEST_GENERATOR.md](scripts/MANIFEST_GENERATOR.md) for details on regenerating manifests.

### Name Format

Both `{SimId}` and `{carId}` must adhere to the following naming format:

1. Lowercase
2. Replace accented chars with standard equivalent
3. Replace spaces with hyphen
4. Replace special characters with hyphen
5. Remove double Hyphens
6. Remove leading and trailing hyphens

### Example name formatting

* `F12024 / AIX Racing 24` -> `f12024/aix-racing-24.json`
* `F12024 / Dams ‘23` -> `f1/dams-23.json`
* `AssettoCorsa / alpine_a110_gt4` -> `assettocorsa/alpine-a110-gt4.json`
* `LMU / Algarve Pro Racing 2024` -> `lmu/algarve-pro-racing-2024.json`

### Example code

```
function nameCleaner($cleanName)
{
    // Convert to lowercase
    $cleanName = mb_strtolower($cleanName, 'UTF-8');

    // Replace accented character with standard
    $cleanName = iconv('UTF-8', 'ASCII//TRANSLIT', $cleanName);
    
    // Replace spaces with hyphen
    $cleanName = preg_replace('/\s+/', '-', $cleanName);
    
    // Replace special characters with hyphen
    $cleanName = preg_replace('/[^a-z0-9]/i', '-', $cleanName);
    
    // Replace multiple hyphens with single
    $cleanName = preg_replace('/-+/', '-', $cleanName);
    
    // Clean leading and trailign hyphens
    $cleanName = trim($cleanName, '-');
    
    return $cleanName;
}   
```

### Manifest
A single root manifest at `data/manifest.json` lists all cars, grouped by game.

Structure:
```
{
  "cars": {
    "{simId}": [
      { "carName": "...", "carId": "...", "path": "{simId}/...json" }
    ]
  }
}
```

- Filter by game using the `{simId}` key in `cars`.
- `path` is relative to `data/` and includes the game folder.

See [scripts/MANIFEST_GENERATOR.md](scripts/MANIFEST_GENERATOR.md) for details on regenerating manifests.

## Changelog
Read the [changelog](changelog.md) to keep track of the format updates.

## File Format
Every file is formatted as follows:

``` 
# carName               (String) - The full human readable car name
# carId                 (String) - The carId property as it appears in SimHub
# carClass              (String) - The car's 3-5 letter class shorthand
# ledNumber             (Int)    - The car's in game number of telemetry LED's
# redlineBlinkInterval  (Int)    - The Speed at which the redline blinks in ms
# ledColor                         An array of the led color
  # redline(:Value)     (String) - A color name or HEX value for the red line
  # led1color(:Value)   (String) - A color name or HEX value for LED 1
  # led2color(:Value)   (String) - A color name or HEX value for LED 2
  # led3color(:Value)   (String) - A color name or HEX value for LED 3
  # ledNcolor(:Value)   (String) - A color name or HEX value for LED N
# ledRpm                           An array of all the RPM data per gear
  # gear(:Key)          (String) - The gear number
    # redline(:Value)   (Int)    - The RPM red line value per gear
    # led1rpm(:Value)   (Int)    - The RPM value for LED 1
    # led2rpm(:Value)   (Int)    - The RPM value for LED 2
    # led3rpm(:Value)   (Int)    - The RPM value for LED 3
    # ledNrpm(:Value)   (Int)    - The RPM value for LED N
# carSettings                      (Optional) An array of all the available Car Settings
  # property(:Simhub)   (String) - The SimHub Property Name
    # min               (Int)    - Lowest possible setting
    # max               (Int)    - Highest possible setting

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

---

© 2025 by [Lovely Sim Racing](https://lsr.gg) is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

