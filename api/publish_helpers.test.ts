import assert from "node:assert/strict";
import test from "node:test";

import {
  authorizationMatchesBearer,
  photoUrlAllowed,
  siteHostFromRequestHeaders,
} from "./publish_helpers";

test("siteHostFromRequestHeaders prefers x-forwarded-host", () => {
  assert.equal(
    siteHostFromRequestHeaders({
      "x-forwarded-host": "EXAMPLE.com:443",
      host: "internal:3000",
    }),
    "example.com",
  );
});

test("siteHostFromRequestHeaders falls back to host", () => {
  assert.equal(
    siteHostFromRequestHeaders({
      host: "my.app:8080",
    }),
    "my.app",
  );
});

test("siteHostFromRequestHeaders returns empty when missing", () => {
  assert.equal(siteHostFromRequestHeaders({}), "");
});

test("photoUrlAllowed https same host", () => {
  assert.equal(
    photoUrlAllowed("https://my.app/images/x.png", "my.app"),
    true,
  );
});

test("photoUrlAllowed rejects other host", () => {
  assert.equal(
    photoUrlAllowed("https://evil.example/x.png", "my.app"),
    false,
  );
});

test("photoUrlAllowed rejects when allowed host empty", () => {
  assert.equal(photoUrlAllowed("https://my.app/x.png", ""), false);
});

test("photoUrlAllowed allows http localhost only", () => {
  assert.equal(
    photoUrlAllowed("http://localhost:3000/a.png", "localhost"),
    true,
  );
  assert.equal(
    photoUrlAllowed("http://127.0.0.1/a.png", "127.0.0.1"),
    true,
  );
  assert.equal(
    photoUrlAllowed("http://evil.com/a.png", "evil.com"),
    false,
  );
});

test("authorizationMatchesBearer", () => {
  assert.equal(
    authorizationMatchesBearer("Bearer secret-token", "secret-token"),
    true,
  );
  assert.equal(authorizationMatchesBearer("Bearer wrong", "secret-token"), false);
  assert.equal(authorizationMatchesBearer(undefined, "secret-token"), false);
  assert.equal(authorizationMatchesBearer("Bearer x", ""), false);
  assert.equal(authorizationMatchesBearer("Bearer spaced", " spaced "), true);
});
