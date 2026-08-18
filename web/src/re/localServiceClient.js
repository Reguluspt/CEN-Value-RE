const LAUNCH_ID_HEADER = 'X-CenValue-RE-Launch-ID';

let bootstrapEnvelope = null;

function normalizeBootstrap(envelope) {
  if (!envelope || typeof envelope !== 'object') {
    throw new TypeError('CenValue RE bootstrap envelope is required');
  }
  const { base_url: baseUrl, launch_id: launchId, bearer_token: bearerToken } = envelope;
  if (![baseUrl, launchId, bearerToken].every((value) => typeof value === 'string' && value.trim())) {
    throw new TypeError('CenValue RE bootstrap envelope is incomplete');
  }

  const url = new URL(baseUrl);
  const hostname = url.hostname.replace(/^\[|\]$/g, '');
  const ipv4Loopback = /^127(?:\.\d{1,3}){3}$/.test(hostname);
  const ipv6Loopback = hostname === '::1';
  if (url.protocol !== 'http:' || (!ipv4Loopback && !ipv6Loopback)) {
    throw new TypeError('CenValue RE local service must use an HTTP loopback URL');
  }
  return Object.freeze({
    baseUrl: url.origin,
    launchId: launchId.trim(),
    bearerToken: bearerToken.trim(),
  });
}

export class ReLocalServiceError extends Error {
  constructor(code, message, status) {
    super(message);
    this.name = 'ReLocalServiceError';
    this.code = code;
    this.status = status;
  }
}

export function installReBootstrap(envelope) {
  bootstrapEnvelope = normalizeBootstrap(envelope);
}

export function clearReBootstrap() {
  bootstrapEnvelope = null;
}

export function hasReBootstrap() {
  return bootstrapEnvelope !== null;
}

export async function reRequest(path, { method = 'GET', body } = {}) {
  if (!bootstrapEnvelope) {
    throw new ReLocalServiceError(
      'RE_BOOTSTRAP_REQUIRED',
      'CenValue RE local-service session is not available for this desktop launch.',
      0,
    );
  }
  if (typeof path !== 'string' || !path.startsWith('/api/re/')) {
    throw new TypeError('CenValue RE request path must stay inside /api/re/');
  }

  const headers = {
    [LAUNCH_ID_HEADER]: bootstrapEnvelope.launchId,
    Authorization: `Bearer ${bootstrapEnvelope.bearerToken}`,
  };
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${bootstrapEnvelope.baseUrl}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const error = payload?.error;
    throw new ReLocalServiceError(
      typeof error?.code === 'string' ? error.code : 'RE_LOCAL_SERVICE_ERROR',
      typeof error?.message === 'string'
        ? error.message
        : 'CenValue RE local service could not complete the request.',
      response.status,
    );
  }
  return payload;
}
