#!/bin/bash
set -e

# Wait for PostgreSQL (ruby-pg lives in Fedibird's bundle).
until bundle exec ruby -e "require 'pg'; PG.connect(host: ENV['DB_HOST'], port: ENV.fetch('DB_PORT', 5432), user: ENV['DB_USER'], password: ENV['DB_PASS'], dbname: 'postgres')" 2>/dev/null; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Wait for Redis.
until bundle exec ruby -e "require 'redis'; Redis.new(host: ENV['REDIS_HOST'], port: ENV.fetch('REDIS_PORT', 6379)).ping" 2>/dev/null; do
  echo "Waiting for Redis..."
  sleep 1
done

# Initialize schema on first boot; no-op on subsequent boots.
echo "Setting up database..."
SAFETY_ASSURED=1 bundle exec rails db:setup || bundle exec rails db:migrate

# Create / reset bob by bypassing validations. Fedibird inherits Mastodon's
# EmailValidator which does DNS MX lookups. Then mint a long-lived Doorkeeper
# access token for bob: Fedibird disables OAuth ``grant_type=password`` so we
# cannot obtain a token over the wire, we have to create one in-DB and hand
# it to the test runner via ``docker exec ... cat /tmp/bob-token``.
echo "Ensuring bob + minting access token..."
bundle exec rails runner '
  account = Account.find_local("bob") || Account.new(username: "bob")
  if account.new_record?
    account.save!(validate: false)
  end
  user = account.user || User.new(account: account)
  user.email = "bob@web"
  user.password = "Password1234!"
  user.password_confirmation = "Password1234!"
  user.agreement = true
  user.confirmed_at ||= Time.now.utc
  user.locale = "en"
  user.save!(validate: false)
  user.update_columns(approved: true, confirmed_at: user.confirmed_at)

  app = Doorkeeper::Application.find_by(name: "misskey-cli-e2e")
  unless app
    app = Doorkeeper::Application.create!(
      name: "misskey-cli-e2e",
      redirect_uri: "urn:ietf:wg:oauth:2.0:oob",
      scopes: "read write follow",
    )
  end
  token = Doorkeeper::AccessToken.find_or_create_for(
    application: app,
    resource_owner: user.id,
    scopes: "read write follow",
    expires_in: nil,
    use_refresh_token: false,
  )
  File.write("/tmp/bob-token", token.token)
  puts "bob ready: user_id=#{user.id} account_id=#{account.id} approved=#{user.approved} confirmed=#{user.confirmed?}"
  puts "bob token written to /tmp/bob-token"
'

exec bundle exec puma -C config/puma.rb
