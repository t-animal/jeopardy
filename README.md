# Installation

Dependencies: pyyaml, pygobject

# Running

```
python -m risiko-anwendung --logFile log.yml --config config.yml
```

If you get loads of GTK Warnings it helps using a standard-conforming default template:

```
GTK_THEME=Adwaita:light python -m risiko-anwendung --logFile log.yml --config config.yml
```

If you prefer a light theme for the application append `--theme light`

# Config file

The config should be a yaml file with a dictionary. The keys are the category names, the
entries should be lists of strings representing the answers. All categories must have an
equal number of answers.

Example:

```
Category A:
  - Some question.
  - |
    Some question with colons: or long text.

Category B:
  - !image path/to/image.jpg
  - !double*image path/to/imageDoubleJeopardy.jpg

Category C:
  - !double double jeopardy
  - another question
```
