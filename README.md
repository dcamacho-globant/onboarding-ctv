# CTV Web — Connected: onboarding docs

A bilingual (Spanish / English) guide to how the NFL **Connected** CTV app works
(`packages/apps/Connected` in the `nfl/nfl-fe` monorepo), published as a password-protected
GitHub Pages site.

Every `file:line` reference in the guide links to that file on the `main` branch of
`nfl/nfl-fe`.

## What the guide covers

- Repo map: a boxes-and-arrows diagram, each box with its file and line
- The 5 key pieces and how the app works end to end
- The journey of a video URL, from a card to the player
- How MediaKind, Redfast, Sentry and Vizbee work
- How login works (activation code flow, tokens, sign-out)
- How analytics works (Adobe SDK on React Native, Adobe Launch / alloy on web)

## How the password protection works

The site is static, so the password cannot be checked on a server. Instead, **the documentation
is encrypted at build time** and the browser decrypts it with what the visitor types:

1. `build-source/build.sh` builds the full page, then encrypts it with
   AES-256-CBC. The key comes from the password through PBKDF2-SHA256 (600,000 rounds).
2. The ciphertext is embedded in `index.html`, the password page.
3. The visitor types the password. The browser (Web Crypto API) derives the key and tries to
   decrypt. If it works, the page is replaced with the documentation. If not, only an error
   message is shown and nothing else loads.

The password is read from the `ONBOARDING_PASSWORD` environment variable only. It is never
written to a file or passed on the command line.

## Repository layout

```
index.html                 Password page (bilingual). Contains a __PAYLOAD__ placeholder.
build-source/
  build.sh                 Encrypts the docs and writes dist/index.html
  build.py                 Expands the page parts into one HTML document
  part*.html               The documentation, one file per section (ES + EN)
.github/workflows/pages.yml  Builds and deploys to GitHub Pages
dist/                      Build output (git-ignored). This is what gets published.
.nojekyll                  Tells GitHub Pages to serve files as they are
```

## Setup

1. Make the repository **private**. `build-source/` holds the documentation in plain text, so a
   public repository exposes it regardless of the password.
2. Add a repository secret named `ONBOARDING_PASSWORD`
   (Settings → Secrets and variables → Actions). Use a long password: the ciphertext is
   public, so a weak one can be guessed offline.
3. In Settings → Pages, set the source to **GitHub Actions**.
4. Push to `main`. The workflow builds and deploys the site.

GitHub Pages for private repositories depends on your organization's GitHub plan.

## Build locally

Requires `bash`, `openssl` and `python3`.

```sh
ONBOARDING_PASSWORD='your-password' bash build-source/build.sh
open dist/index.html
```

To also check that every referenced file and line exists, point `REPO` at a local checkout of
`nfl-fe`:

```sh
REPO=/path/to/nfl-fe ONBOARDING_PASSWORD='your-password' bash build-source/build.sh
```

The build fails if a referenced file is missing or the line is empty.

## Updating the content

- Edit the matching `build-source/part*.html`. Each section has a Spanish block (`class="es"`)
  and an English block (`class="en"`). Keep both in sync.
- Write references as `{{C:path:line}}` for files under `packages/apps/Connected/`, or
  `{{P:path:line}}` for files under `packages/`. Add `|text` to change the label shown.
  The build turns them into links to `main`.
- Line numbers drift as `nfl-fe` changes. Re-run the build with `REPO` set to find references
  that no longer point to a real line, then update them.

## Caveats

- Decryption needs the Web Crypto API, which browsers only provide on `https` pages (and
  `localhost` / `file://` in Chrome). Very old TV browsers may not support it.
- The guide describes the code at the time it was written. It was produced by reading the
  source, not by running the app.
