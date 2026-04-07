# ⚔️ Side Quest App

A lightweight, browser-based quest board where adventurers can **post**, **accept**, and **complete** side quests — each with its own description prompt and optional reward.

---

## Features

| Feature | Description |
|---|---|
| **Post a Quest** | Fill in a title, description/prompt, and optional reward, then hit *Post Quest* |
| **Accept a Quest** | Move any available quest to your *Accepted* column with one click |
| **Complete a Quest** | Mark an accepted quest as finished and send it to the *Completed* column |
| **Delete a Quest** | Remove a quest from any column (with a confirmation prompt) |
| **Persistent Storage** | All quests are saved in `localStorage` so they survive page refreshes |
| **Responsive Layout** | Three-column board that collapses to a single column on mobile |

---

## Getting Started

No build step required — just open `index.html` in your browser:

```bash
# Clone the repo
git clone https://github.com/Fade32/side-quest-app.git
cd side-quest-app

# Open in your default browser (macOS)
open index.html

# …or on Linux
xdg-open index.html
```

---

## Project Structure

```
side-quest-app/
├── index.html   — App markup and quest card template
├── style.css    — Dark-fantasy themed styles
├── app.js       — Quest logic (add / accept / complete / delete / persist)
├── TODO.md      — Feature roadmap and task checklist
└── README.md    — This file
```

---

## Roadmap

See [TODO.md](TODO.md) for the full list of planned features including user accounts, XP systems, party collaboration, a backend API, and more.

---

## License

[MIT](LICENSE)
