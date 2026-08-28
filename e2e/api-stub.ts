/**
 * A stub of the Voicebox Python sidecar (`backend/`, default 127.0.0.1:17493).
 *
 * The web build is a pure SPA: the dev server only ever returns an empty
 * `<div id="root">`, and every screen comes from `fetch()` against the sidecar.
 * Stubbing those routes in the browser lets E2E tests drive real UI state — a
 * voice list, an accepted generation, an outage toast — without loading a model.
 *
 * Payloads follow `app/src/lib/api/types.ts`. That matters: the app is not
 * defensive about unexpected shapes (a `{}` where a list is expected takes the
 * React tree down), so a sloppy stub shows up as a blank page rather than a
 * clear error. Anything not listed here answers 404, which every hook treats as
 * "no data yet".
 */
import type { Page } from '@playwright/test';

export const SIDECAR_ORIGIN = process.env.E2E_SIDECAR_ORIGIN ?? 'http://127.0.0.1:17493';

export interface RecordedRequest {
  method: string;
  path: string;
  url: string;
  postData: string | null;
}

export interface StubOptions {
  /** Overriding payloads keyed by pathname prefix (longest prefix wins). */
  overrides?: Record<string, unknown>;
  /** Pathnames that should fail, to exercise error states. */
  fail?: string[];
}

const EMPTY_MODEL_READINESS = {
  ready: false,
  model_name: 'none',
  display_name: 'Not downloaded',
  size: '0.6B',
};

const DEFAULT_ROUTES: [string, unknown][] = [
  [
    '/health',
    {
      status: 'healthy',
      model_loaded: true,
      model_downloaded: true,
      model_size: '0.6B',
      gpu_available: false,
      backend_type: 'cpu',
      backend_variant: 'cpu',
    },
  ],
  ['/profiles/presets', { engine: 'qwen3-tts', voices: [] }],
  ['/profiles', []],
  ['/history/failed', { deleted: 0 }],
  ['/history', { items: [], total: 0, limit: 50, offset: 0 }],
  ['/stories', []],
  ['/captures/readiness', { stt: EMPTY_MODEL_READINESS, llm: EMPTY_MODEL_READINESS }],
  ['/capture/readiness', { stt: EMPTY_MODEL_READINESS, llm: EMPTY_MODEL_READINESS }],
  ['/captures', { items: [], total: 0 }],
  ['/models/status', { models: [] }],
  ['/models/cache-dir', { cache_dir: '/tmp/voicebox-models' }],
  ['/effects/presets', []],
  ['/effects/available', { effects: [] }],
  [
    '/settings/generation',
    {
      max_chunk_chars: 600,
      crossfade_ms: 50,
      normalize_audio: true,
      autoplay_on_generate: false,
    },
  ],
  [
    '/settings/captures',
    {
      stt_model: 'base',
      language: 'en',
      auto_refine: false,
      llm_model: '0.6B',
      smart_cleanup: true,
      self_correction: false,
      preserve_technical: true,
      allow_auto_paste: false,
      default_playback_voice_id: null,
      hotkey_enabled: false,
    },
  ],
  ['/tasks/active', { downloads: [], generations: [] }],
  ['/mcp/bindings', { items: [] }],
  [
    '/cloud/status',
    {
      connected: false,
      device_name: null,
      account_user_id: null,
      key_prefix: null,
      connected_at: null,
      dashboard_url: '',
    },
  ],
  [
    '/backend/cuda-status',
    {
      available: false,
      active: false,
      binary_path: null,
      cuda_libs_version: null,
      download_supported: false,
      unsupported_reason: 'e2e stub',
      downloading: false,
    },
  ],
  [
    '/backend/rocm-status',
    {
      available: false,
      active: false,
      binary_path: '',
      rocm_libs_version: '',
      downloading: false,
    },
  ],
];

/** One synthetic voice profile, so the editor is usable without a real model. */
export const SAMPLE_PROFILE = {
  id: 'e2e-voice-1',
  name: 'E2E Test Voice',
  description: 'Created by the browser test harness',
  language: 'en',
  voice_type: 'preset',
  preset_engine: 'qwen3-tts',
  preset_voice_id: 'serena',
  generation_count: 0,
  sample_count: 0,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

/** A completed generation, matching `GenerationResponse`. */
export function fakeGeneration(text: string, profileId = SAMPLE_PROFILE.id) {
  return {
    id: 'e2e-generation-1',
    profile_id: profileId,
    text,
    language: 'en',
    audio_path: '/tmp/e2e.wav',
    duration: 1.5,
    seed: 42,
    engine: 'qwen3-tts',
    model_size: '0.6B',
    status: 'completed',
    created_at: '2026-01-01T00:00:00Z',
  };
}

function payloadFor(pathname: string, overrides: [string, unknown][]): unknown {
  const match =
    overrides.find(([prefix]) => pathname.startsWith(prefix)) ??
    DEFAULT_ROUTES.find(([prefix]) => pathname.startsWith(prefix));
  return match ? match[1] : undefined;
}

/**
 * Install the stub on a page and return the request log, so a test can assert on
 * the exact HTTP call the UI made — method, path and JSON body.
 */
export async function stubSidecar(
  page: Page,
  options: StubOptions = {},
): Promise<RecordedRequest[]> {
  const requests: RecordedRequest[] = [];
  const overrides = Object.entries(options.overrides ?? {}).sort(
    (a, b) => b[0].length - a[0].length,
  );
  const failures = options.fail ?? [];
  const origin = new URL(SIDECAR_ORIGIN);

  await page.route(
    (url) => url.origin === origin.origin,
    async (route) => {
      const request = route.request();
      const pathname = new URL(request.url()).pathname;
      requests.push({
        method: request.method(),
        path: pathname,
        url: request.url(),
        postData: request.postData(),
      });

      // EventSource streams: never fulfill with JSON, just close them.
      if (pathname.startsWith('/stream') || pathname.startsWith('/events')) return route.abort();
      if (failures.some((prefix) => pathname.startsWith(prefix))) {
        return route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'e2e: sidecar unavailable' }),
        });
      }

      const body = payloadFor(pathname, overrides);
      if (body === undefined) {
        return route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ detail: `e2e stub: ${pathname} is not stubbed` }),
        });
      }
      // A function override lets a test derive the response from the request.
      const resolved =
        typeof body === 'function' ? (body as (req: unknown) => unknown)(request) : body;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(resolved),
      });
    },
  );

  return requests;
}
