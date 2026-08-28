#!/usr/bin/env node
/**
 * One-time browser setup for the Playwright suite.
 *
 * 1. Try the normal path: `playwright install chromium` (downloads from
 *    cdn.playwright.dev / playwright's Azure mirror).
 * 2. If that host is unreachable — air-gapped runners, locked-down sandboxes,
 *    or an image with no `apt-get` access for the browser's system libraries —
 *    fall back to the Chromium build published *inside* the
 *    `@sparticuz/chromium` npm package, together with the shared libraries
 *    (libnss3/libnspr4/libexpat) it needs on slim images. npm is reachable
 *    wherever `bun install` works, and no package manager is required.
 *
 * Both paths yield a standard Chromium that speaks CDP, which is all Playwright
 * needs, so the tests themselves never change. Everything lands under
 * node_modules/.cache and is therefore cleaned up by a fresh install.
 */
import { execFileSync, spawnSync } from 'node:child_process';
import {
  chmodSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { brotliDecompressSync } from 'node:zlib';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, '..');
const CACHE_DIR = path.join(REPO_ROOT, 'node_modules/.cache/voicebox-e2e');
const MANIFEST = path.join(CACHE_DIR, 'browser.json');
const SPARTICUZ_BIN = path.join(REPO_ROOT, 'node_modules/@sparticuz/chromium/bin');
const MS_PLAYWRIGHT_DIR = path.join(process.env.HOME ?? '', '.cache/ms-playwright');

const log = (msg) => console.log(`[e2e:browser] ${msg}`);

function playwrightCli() {
  const local = path.join(REPO_ROOT, 'node_modules/.bin/playwright');
  return existsSync(local) ? local : 'npx';
}

function hasPlaywrightChromium() {
  if (!existsSync(MS_PLAYWRIGHT_DIR)) return false;
  return readdirSync(MS_PLAYWRIGHT_DIR).some(
    (entry) => entry.startsWith('chromium-') && !entry.includes('headless_shell'),
  );
}

function tryOfficialInstall() {
  const cli = playwrightCli();
  const args = cli.endsWith('npx')
    ? ['playwright', 'install', 'chromium']
    : ['install', 'chromium'];
  try {
    execFileSync(cli, args, { cwd: REPO_ROOT, stdio: 'inherit', timeout: 15 * 60 * 1000 });
    return true;
  } catch (error) {
    log(`official Chromium download failed: ${String(error).split('\n')[0]}`);
    return false;
  }
}

function writeBrotliFile(archivePath, targetPath) {
  writeFileSync(targetPath, brotliDecompressSync(readFileSync(archivePath)));
}

function extractTarBrotliArchive(archivePath, destDir) {
  mkdirSync(destDir, { recursive: true });
  const tarInput = brotliDecompressSync(readFileSync(archivePath));
  const result = spawnSync('tar', ['-x', '-f', '-', '-C', destDir], { input: tarInput });
  if (result.status !== 0) {
    throw new Error(`failed to extract ${path.basename(archivePath)}: ${result.stderr}`);
  }
}

async function installFallbackBrowser() {
  if (!existsSync(SPARTICUZ_BIN)) {
    throw new Error('missing node_modules/@sparticuz/chromium — run `bun install` first');
  }

  rmSync(CACHE_DIR, { recursive: true, force: true });
  mkdirSync(CACHE_DIR, { recursive: true });

  // The executable itself (brotli-compressed blob inside the npm package).
  const executable = path.join(CACHE_DIR, 'chromium');
  writeBrotliFile(path.join(SPARTICUZ_BIN, 'chromium.br'), executable);
  chmodSync(executable, 0o755);

  // Software GL, the NSS/NSPR stack Chromium links against, and fonts.
  extractTarBrotliArchive(path.join(SPARTICUZ_BIN, 'swiftshader.tar.br'), CACHE_DIR);
  extractTarBrotliArchive(path.join(SPARTICUZ_BIN, 'al2023.tar.br'), CACHE_DIR);
  const fontsArchive = path.join(SPARTICUZ_BIN, 'fonts.tar.br');
  if (existsSync(fontsArchive)) {
    extractTarBrotliArchive(fontsArchive, CACHE_DIR);
  }

  const version = spawnSync(executable, ['--version'], {
    encoding: 'utf8',
    env: { ...process.env, LD_LIBRARY_PATH: path.join(CACHE_DIR, 'lib') },
  }).stdout?.trim();

  writeFileSync(
    MANIFEST,
    `${JSON.stringify(
      {
        executablePath: executable,
        ldLibraryPath: existsSync(path.join(CACHE_DIR, 'lib'))
          ? path.join(CACHE_DIR, 'lib')
          : undefined,
        fontconfigPath: existsSync(path.join(CACHE_DIR, 'fonts'))
          ? path.join(CACHE_DIR, 'fonts')
          : undefined,
        chromiumVersion: version || 'unknown',
        source: '@sparticuz/chromium (npm-registry fallback, no CDN required)',
      },
      null,
      2,
    )}\n`,
  );
  log(`wrote ${path.relative(REPO_ROOT, MANIFEST)} (${version || 'unknown version'})`);
  log('note: this build is a chrome-headless-shell, so headed mode is unavailable');
}

async function main() {
  if (hasPlaywrightChromium()) {
    log('Playwright Chromium already installed — nothing to do');
    return;
  }
  if (tryOfficialInstall() && hasPlaywrightChromium()) {
    rmSync(CACHE_DIR, { recursive: true, force: true });
    log('installed Playwright Chromium from the CDN');
    return;
  }
  log('CDN unreachable — using the npm-registry Chromium build instead');
  await installFallbackBrowser();
}

await main();
