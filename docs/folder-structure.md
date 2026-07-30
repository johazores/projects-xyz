# Folder Structure

```text
projects-xyz/
├── README.md
├── LICENSE
├── docs/
│   ├── architecture.md
│   ├── practical-toolkit-review.md
│   ├── practical-workflows.md
│   ├── development-guide.md
│   └── roadmap.md
├── media-process-api/
├── audio-process/
├── image-process/
└── video-process/
```

Each media project keeps the same shallow shape:

```text
<media>-process/
├── README.md
├── requirements*.txt
├── config.json.example
├── config.py
├── main.py
├── cli.py
├── providers/
├── utils/
├── examples/
├── outputs/
└── docs/
```

`image-process/presets.json` is a deliberate project-specific data file.

The API remains small:

```text
media-process-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   └── services/
├── examples/
├── outputs/
├── docs/
├── requirements.txt
└── README.md
```
