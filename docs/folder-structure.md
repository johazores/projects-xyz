# Folder Structure

```text
projects-xyz/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── coding-standards.md
│   ├── contributing.md
│   ├── design-decisions.md
│   ├── development-guide.md
│   ├── faq.md
│   ├── folder-structure.md
│   ├── review-report.md
│   └── roadmap.md
├── audio-process/
├── image-process/
└── video-process/
```

Every media project follows this shape:

```text
<media>-process/
├── README.md
├── requirements.txt
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

The folders are intentionally shallow. Add deeper folders only when a project becomes difficult to navigate without them.
