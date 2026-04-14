# Side Quest App — TODO List

A living checklist of features and tasks for the Side Quest App.
Features are grouped by priority. Tick them off as they are completed.

---

## ✅ Done

- [x] Project scaffolding (HTML / CSS / JS)
- [x] Post a new side quest (title, description/prompt, optional reward)
- [x] View all available quests on the quest board
- [x] Accept a quest (moves it from *Available* → *Accepted*)
- [x] Complete a quest (moves it from *Accepted* → *Completed*)
- [x] Delete a quest with a confirmation prompt
- [x] Persist quests across page refreshes with `localStorage`
- [x] Responsive three-column board layout (collapses to single column on mobile)
- [x] Empty-state messages for each column

---

## 🔲 To Do — Core Features

- [ ] **User accounts** — let multiple adventurers log in and manage their own quest boards
- [ ] **Quest categories / tags** — e.g. *Combat*, *Exploration*, *Crafting*, *Social*
- [ ] **Difficulty rating** — Easy / Medium / Hard / Legendary selector when posting a quest
- [ ] **Due date / deadline** — optional date-picker so quests can expire
- [ ] **Quest assignment** — assign an accepted quest to a specific party member
- [ ] **Comments / notes** — add progress notes to an in-progress quest
- [ ] **Edit quest** — update title, description, or reward after posting
- [ ] **Search & filter** — filter quests by status, category, or keyword

---

## 🔲 To Do — Experience & Rewards

- [ ] **XP system** — award experience points when quests are completed
- [ ] **Level-up mechanic** — adventurer levels up after accumulating enough XP
- [ ] **Leaderboard** — rank adventurers by completed quests or XP earned
- [ ] **Achievement badges** — unlock badges for milestones (first quest, 10 completions, etc.)
- [ ] **Streak tracker** — reward consecutive days with at least one completion

---

## 🔲 To Do — Collaboration

- [ ] **Party system** — create or join a party to share a quest board
- [ ] **Quest gifting** — post a quest specifically for another adventurer to accept
- [ ] **Real-time sync** — use WebSockets or a backend API so party members see changes live
- [ ] **Notifications** — alert adventurers when a quest is posted, accepted, or completed

---

## 🔲 To Do — Technical / Infrastructure

- [ ] **Backend API** — Node.js / Express (or another framework) REST API to replace localStorage
- [ ] **Database** — persist quests in a database (e.g. PostgreSQL, MongoDB, SQLite)
- [ ] **Authentication** — JWT or OAuth2 login
- [ ] **Unit tests** — add test coverage for quest state transitions and form validation
- [ ] **End-to-end tests** — Playwright or Cypress tests for the full user flow
- [ ] **CI/CD pipeline** — GitHub Actions workflow for lint, test, and deploy on every push
- [ ] **PWA support** — add a `manifest.json` and service worker so the app can be installed offline
- [ ] **Accessibility audit** — ensure all interactive elements are keyboard-navigable and screen-reader friendly
- [ ] **Dark / light theme toggle**

---

## 🔲 To Do — Polish & UX

- [ ] **Drag-and-drop** — drag cards between columns instead of using buttons
- [ ] **Animations** — smooth slide/fade transitions when cards move columns
- [ ] **Confetti or celebration effect** on quest completion
- [ ] **Quest detail modal** — click a card to see full details without leaving the board
- [ ] **Undo delete** — brief toast with an undo action instead of a blocking confirm dialog
- [ ] **Custom avatars / party portraits** for each adventurer
