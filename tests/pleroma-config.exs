import Config

# Plain-HTTP config for the misskey-cli E2E tests. No TLS, no federation, no
# media proxy — just enough to exercise the Pleroma-family code path.

config :pleroma, Pleroma.Web.Endpoint,
  url: [host: "pleroma", scheme: "http", port: 4000],
  http: [ip: {0, 0, 0, 0}, port: 4000],
  secret_key_base: "test-secret-key-base-not-for-production-use-misskey-cli-e2e-000000000000000",
  signing_salt: "test-signing-salt-00000000"

config :pleroma, Pleroma.Repo,
  adapter: Ecto.Adapters.Postgres,
  username: "pleroma",
  password: "testpass",
  database: "pleroma",
  hostname: "postgres-pl",
  pool_size: 10

config :pleroma, :instance,
  name: "Pleroma Test",
  email: "admin@pleroma",
  registrations_open: true,
  account_activation_required: false,
  federation_incoming_replies_max_depth: 100,
  allow_relay: false

config :pleroma, Pleroma.Captcha,
  enabled: false

config :pleroma, :media_proxy,
  enabled: false

config :pleroma, Pleroma.Upload,
  uploader: Pleroma.Uploaders.Local

config :pleroma, :http_security,
  enabled: false

config :web_push_encryption, :vapid_details,
  subject: "mailto:admin@pleroma",
  public_key: "BLFZ5XFJ8tPpOlUh4j5FZY-6IqbKqYFBwjdYq5yeAx9o1vLpf8wQz3aCjTcW8-6E4gQoq8P3D0zqY1dxg9p3y7o",
  private_key: "ZczHLL4CH6ekVB5a4Av3-1EJ3LVFz0bqV8tX0DKQbw0"
