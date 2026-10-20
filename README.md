# Eventually Consistent

**One systems concept a day, as a three-minute podcast.**

Eventually Consistent is a daily audio explainer of one backend and distributed-systems concept: indexing, replication, quorums, consensus, CAP, MVCC, LSM trees, and so on, 77 in all. Each episode covers what the concept is, why it exists, a real example and the trade-off, in about three minutes.

- **Feed:** https://tech-bites-podcast.vercel.app/feed.xml
- **Site:** https://tech-bites-podcast.vercel.app/

To subscribe in **Pocket Casts**, paste the feed URL into the search box. Any podcast app that takes an RSS URL works the same way.

## Why

I already get a short written explainer of one systems concept every morning. Reading it is easy to skip. Listening isn't: turning each explainer into an episode on an RSS feed means it shows up in my podcast app every day next to everything else I listen to, and I can catch it on a walk or a commute.

## Pipeline

```
concept list (daily-concepts/state.json)
  → daily written explainer (what / why / real example / trade-off)
  → spoken script, 450–600 words (scripts/YYYY-MM-DD-slug.txt)
  → Chatterbox TTS, cloned voice, CPU  (cb_render.py)
  → ffmpeg: loudnorm -16 LUFS, 64 kbps mono MP3
  → episodes.json → site/feed.xml + site/index.html  (add_episode.py)
  → static Vercel deploy  (deploy_prep.py + Vercel API)
```

1. **Explainer.** Each day picks the next concept from `daily-concepts/state.json` and writes a short markdown explainer (example: `daily-concepts/explainers/day05-read-replicas.md`). History is appended to the state file so concepts don't repeat within a round.
2. **Spoken script.** The explainer is rewritten for the ear: 450–600 words, no markdown, symbols and acronyms spelled out. It opens *"Hey, welcome to Eventually Consistent. This is day N of 77, and today we're talking about X."* and closes *"That's it for today. See you tomorrow, eventually."*
3. **Voice.** [Chatterbox](https://github.com/resemble-ai/chatterbox) runs locally on CPU (8 cores, no GPU) and clones a warm female reference voice (`voices/ref_af_heart.wav`) with emotion/exaggeration **0.7** and cfg weight 0.4.
   - The script is split into chunks of **3 sentences or fewer** (or ~40 words), with **0.45 s** of silence between chunks.
   - **Dropped-word check:** any chunk that renders faster than 0.24 s per word (or slower than 0.9 s/word) is regenerated, up to 3 tries, keeping the longest take. The final JSON line reports `"suspect": []` when every chunk passed.
   - A three-minute episode takes about six minutes to render.
   - **Fallback:** `TB_ENGINE=piper` uses Piper (`en_US-ryan-high`) instead. It's much faster but flatter.
4. **Mastering.** ffmpeg loudness-normalises to **-16 LUFS** (true peak -1.5 dB) and encodes **64 kbps mono** MP3 at 44.1 kHz.
5. **Feed and site.** `add_episode.py` updates `episodes.json` and regenerates `site/feed.xml` (RSS 2.0 + iTunes tags), `site/index.html` and `site/vercel.json` (correct content types for the feed and MP3s).
6. **Deploy.** `deploy_prep.py` writes a SHA-1 manifest of everything in `site/`. Files are uploaded to Vercel and a production deployment of the static project `tech-bites-podcast` is created. Every deploy includes all episodes, because a deploy replaces the whole site.

**Audio is not in this repo.** The MP3s are hosted on Vercel at `https://tech-bites-podcast.vercel.app/episodes/<file>.mp3`; `*.mp3`, `*.wav`, `site/episodes/` and the `deploy/` payload folder are git-ignored.

## Repo layout

| Path | What |
|---|---|
| `publish_today.py` | One-command daily step: save script, render, rebuild feed, prep deploy |
| `add_episode.py` | Render one script to MP3, update `episodes.json`, regenerate feed/site |
| `cb_render.py` | Chatterbox chunked renderer with the dropped-word check |
| `deploy_prep.py` | Builds the Vercel file manifest (`deploy/files.json`) |
| `make_cover.py` | Draws the 3000×3000 cover art (`site/cover.jpg`) |
| `episodes.json` | Episode metadata (source of truth for the feed) |
| `scripts/` | The spoken script for every episode |
| `site/` | `feed.xml`, `index.html`, `vercel.json`, `cover.jpg` |
| `daily-concepts/` | The 77-concept list + progress (`state.json`) and sample explainer |
| `samples/` | Voice-audition scripts (Kokoro and Chatterbox) and the test passage |
| `voices/make_ref.py` | Regenerates the voice reference clip |

## Setup

Needs Linux or macOS, `ffmpeg`/`ffprobe`, Python 3.13 (main) and Python 3.11 (TTS). Three virtualenvs keep the heavy TTS stacks apart:

```bash
# main: feed, cover, Piper fallback
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Chatterbox (CPU torch)
python3.11 -m venv .venv-cb
.venv-cb/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 torchaudio==2.6.0
.venv-cb/bin/pip install -r requirements-chatterbox.txt

# Kokoro (only to regenerate the reference voice)
python3.11 -m venv .venv-kokoro && .venv-kokoro/bin/pip install -r requirements-kokoro.txt
```

Model weights download from Hugging Face on first run (`ResembleAI/chatterbox`, `hexgrad/Kokoro-82M`) and are not stored here.

**Reference voice.** `voices/ref_af_heart.wav` is not committed. It's ~25 s of the Kokoro-82M **af_heart** voice (Apache-2.0) reading `samples/opening.txt`. Regenerate it with:

```bash
.venv-kokoro/bin/python voices/make_ref.py
```

**Piper fallback voice** (optional): download `en_US-ryan-high.onnx` and `.onnx.json` from [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ryan/high) into `voices/`.

**Cover art:** `.venv/bin/python make_cover.py` (uses DejaVu fonts).

## Daily run

```bash
# 1. write today's spoken script to /tmp/tb_script.txt
# 2. render + rebuild feed + prep deploy (title/day default from the concept state file)
TB_STATE=daily-concepts/state.json \
  python3 publish_today.py --script /tmp/tb_script.txt --summary "One-line episode summary"
# check the cb_render output ends with "suspect": []
# 3. upload deploy/files.json entries to Vercel and create a production deployment
# 4. verify
curl -sI https://tech-bites-podcast.vercel.app/feed.xml   # 200 application/rss+xml
```

Options: `--title`, `--day`, `--date` override the state-file defaults; `--explainer file.md` does a rough markdown-to-speech conversion instead of a hand-written script; `TB_ENGINE=piper` switches engines; `TB_BASE_URL` changes the URL written into the feed.

Deploying uses the Vercel REST API: `POST /v2/files` for each binary in `deploy/files.json` (header `x-vercel-digest: <sha>`), then `POST /v13/deployments` with `target: production`, `projectSettings.framework: null` and the full file list. Credentials come from your own Vercel login and never live in this repo.

## Episodes

| Day | Date | Concept | Length | Links |
|---|---|---|---|---|
| 4 | 2026-10-13 | Normalization | 2:56 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-13-normalization.mp3) · [script](scripts/2026-10-13-normalization.txt) |
| 5 | 2026-10-14 | Read replicas | 2:48 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-14-read-replicas.mp3) · [script](scripts/2026-10-14-read-replicas.txt) |
| 6 | 2026-10-15 | Leader–Follower replication | 2:51 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-15-leader-follower-replication.mp3) · [script](scripts/2026-10-15-leader-follower-replication.txt) |
| 7 | 2026-10-16 | Multi-leader replication | 3:13 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-16-multi-leader-replication.mp3) · [script](scripts/2026-10-16-multi-leader-replication.txt) |
| 8 | 2026-10-17 | Quorum | 3:10 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-17-quorum.mp3) · [script](scripts/2026-10-17-quorum.txt) |
| 9 | 2026-10-18 | Consensus | 2:56 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-18-consensus.mp3) · [script](scripts/2026-10-18-consensus.txt) |
| 10 | 2026-10-19 | CAP theorem | 3:18 | [mp3](https://tech-bites-podcast.vercel.app/episodes/2026-10-19-cap-theorem.mp3) · [script](scripts/2026-10-19-cap-theorem.txt) |

Days 1–3 (Indexing, Clustering, Denormalization) were written explainers only, before the podcast started. New episodes are added daily; `episodes.json` and the feed are the up-to-date list.

## Licence

Code and scripts: [MIT](LICENSE). The reference voice is derived from Kokoro-82M (Apache-2.0); Chatterbox is MIT; Piper voices carry their own licences.
