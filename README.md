# iacosta3994.github.io

Personal site for Blizen. Published at <https://iacosta3994.github.io/>.

Static HTML and CSS. Edit `index.html` and `style.css` on `main`.

Most played Steam games are listed in `games.json`. The page uses that file when it has games, and keeps the handwritten pills otherwise.

`.github/workflows/steam-games.yml` tries to refresh the file once a day. Steam's games page still answers anonymous requests with a sign-in screen, even when game details are public, so the refresh only writes new hours when the `STEAM_API_KEY` repository secret is set. Create the key at <https://steamcommunity.com/dev/apikey> and add it with `gh secret set STEAM_API_KEY` in this repo. Do not commit the key.
