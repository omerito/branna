#!/usr/bin/env bash
# Publish a directory as the only commit of a branch of this repository (used by the Branna
# workflow for the website, its previews and failure logs). Each publish replaces the branch with a
# single fresh commit, so large build output never piles up in the repository's history.
#
# Usage: packaging/branna/publish.sh SOURCE_DIR BRANCH MESSAGE
# Needs GITHUB_TOKEN, GITHUB_REPOSITORY and GITHUB_SHA (set by GitHub Actions).
set -euo pipefail

SRC="${1:?usage: publish.sh SOURCE_DIR BRANCH MESSAGE}"
BRANCH="${2:?usage: publish.sh SOURCE_DIR BRANCH MESSAGE}"
MESSAGE="${3:?usage: publish.sh SOURCE_DIR BRANCH MESSAGE}"
: "${GITHUB_TOKEN:?}" "${GITHUB_REPOSITORY:?}" "${GITHUB_SHA:?}"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cp -R "$SRC/." "$WORK/"
# GitHub Pages: serve every file as is (no Jekyll processing).
touch "$WORK/.nojekyll"
cd "$WORK"
git init -q -b "$BRANCH"
git add -A
git -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
  commit -q -m "$MESSAGE" -m "Built from ${GITHUB_SHA}."
git push -q --force "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "HEAD:refs/heads/${BRANCH}"
echo "published $SRC to $BRANCH"
