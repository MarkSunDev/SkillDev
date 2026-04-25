#!/usr/bin/env node
/**
 * store_fetcher.js — Fetch Google Play Store metadata via google-play-scraper.
 *
 * Usage:
 *   node store_fetcher.js <package_name> [lang] [country]
 *
 * Outputs a single JSON object to stdout with fields:
 *   app_name, developer, developer_id, developer_email, developer_website,
 *   icon, rating, rating_count, rating_histogram, installs, min_installs,
 *   price, free, offers_iap, android_version, content_rating,
 *   genre, genre_id, last_update, version, recent_changes,
 *   privacy_policy, google_play_url,
 *   permissions[]  — from permissions() call
 *   data_safety[]  — from datasafety() call
 *
 * Exit codes:
 *   0  success
 *   1  fetch error (message on stderr)
 */

'use strict';

const path = require('path');
const { execFileSync } = require('child_process');

// node_modules lives next to this script — resolve from __dirname so the
// script works regardless of the working directory Claude invokes it from.
const NODE_MODULES = path.join(__dirname, 'node_modules');
process.env.NODE_PATH = NODE_MODULES +
  (process.env.NODE_PATH ? path.delimiter + process.env.NODE_PATH : '');
require('module').Module._initPaths();

// Auto-install google-play-scraper on first run (mirrors dependency_bootstrap.py
// pattern used for Python deps — no pre-committed node_modules needed).
function ensureGooglePlayScraper() {
  try {
    require('google-play-scraper');
    return; // already installed
  } catch (_) {}

  process.stderr.write('[store] google-play-scraper not found — installing...\n');
  try {
    execFileSync('npm', ['install', '--prefix', __dirname, 'google-play-scraper', '--save'], {
      stdio: ['ignore', 'ignore', 'pipe'],
    });
    // Re-initialise Node module paths so the freshly installed package is found.
    require('module').Module._initPaths();
    process.stderr.write('[store] google-play-scraper installed.\n');
  } catch (e) {
    process.stderr.write(
      '[store] Auto-install failed. Run manually:\n' +
      `  npm install --prefix ${__dirname} google-play-scraper\n`
    );
    process.exit(1);
  }
}

ensureGooglePlayScraper();

const packageName = process.argv[2];
const lang = process.argv[3] || 'zh-CN';
const country = process.argv[4] || 'cn';

if (!packageName) {
  process.stderr.write('Usage: node store_fetcher.js <package_name> [lang] [country]\n');
  process.exit(1);
}

let gplay;
try {
  const _mod = require('google-play-scraper');
  // Support both legacy (direct export) and new ESM-compat (default export) builds.
  gplay = (_mod && typeof _mod.app === 'function') ? _mod : (_mod && _mod.default);
  if (!gplay || typeof gplay.app !== 'function') throw new Error('unexpected module shape');
} catch (e) {
  process.stderr.write(`[store] Failed to load google-play-scraper: ${e.message}\n`);
  process.exit(1);
}

async function fetchAll(pkgId) {
  const opts = { appId: pkgId, lang, country, throttle: 10 };

  const [appData, perms, safety] = await Promise.allSettled([
    gplay.app(opts),
    gplay.permissions({ appId: pkgId, lang, country }),
    gplay.datasafety({ appId: pkgId, lang, country }),
  ]);

  if (appData.status === 'rejected') {
    throw new Error(`app() failed: ${appData.reason && appData.reason.message || appData.reason}`);
  }

  const a = appData.value;

  // Normalize last_update to YYYY-MM-DD
  let lastUpdate = '';
  if (a.updated) {
    try {
      const d = new Date(a.updated);
      lastUpdate = d.toISOString().slice(0, 10);
    } catch (_) {
      lastUpdate = String(a.updated);
    }
  }

  // Flatten rating histogram: {1: n, 2: n, 3: n, 4: n, 5: n}
  let histogram = {};
  if (a.histogram && Array.isArray(a.histogram)) {
    // google-play-scraper returns [1star_count, 2star_count, ...]
    a.histogram.forEach((count, idx) => {
      histogram[idx + 1] = count;
    });
  }

  return {
    app_name: a.title || '',
    developer: a.developer || '',
    developer_id: a.developerId || '',
    developer_email: a.developerEmail || '',
    developer_website: a.developerWebsite || '',
    icon: a.icon || '',
    rating: typeof a.score === 'number' ? a.score.toFixed(2) : '',
    rating_count: a.ratings || 0,
    rating_histogram: histogram,
    installs: a.installs || '',
    min_installs: a.minInstalls || 0,
    price: a.priceText || '免费',
    free: a.free !== false,
    offers_iap: a.offersIAP || false,
    android_version: a.androidVersion || '',
    content_rating: a.contentRating || '',
    genre: a.genre || '',
    genre_id: a.genreId || '',
    last_update: lastUpdate,
    version: a.version || '',
    recent_changes: a.recentChanges || '',
    privacy_policy: a.privacyPolicy || '',
    google_play_url: a.url || `https://play.google.com/store/apps/details?id=${pkgId}`,
    permissions: perms.status === 'fulfilled' ? (perms.value || []) : [],
    data_safety: safety.status === 'fulfilled' ? (safety.value || []) : [],
  };
}

fetchAll(packageName)
  .then(result => {
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    process.exit(0);
  })
  .catch(err => {
    process.stderr.write(`Error fetching store data for ${packageName}: ${err.message || err}\n`);
    process.exit(1);
  });
