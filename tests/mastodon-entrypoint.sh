#!/bin/bash
set -e

# Wait for PostgreSQL (ruby-pg lives in Mastodon's bundle).
until bundle exec ruby -e "require 'pg'; PG.connect(host: ENV['DB_HOST'], port: ENV.fetch('DB_PORT', 5432), user: ENV['DB_USER'], password: ENV['DB_PASS'], dbname: 'postgres')" 2>/dev/null; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Wait for Redis (ruby-redis is also bundled).
until bundle exec ruby -e "require 'redis'; Redis.new(host: ENV['REDIS_HOST'], port: ENV.fetch('REDIS_PORT', 6379)).ping" 2>/dev/null; do
  echo "Waiting for Redis..."
  sleep 1
done

# Initialize schema on first boot; no-op on subsequent boots.
echo "Setting up database..."
SAFETY_ASSURED=1 bundle exec rails db:setup || bundle exec rails db:migrate

# Create / reset bob by bypassing validations. Mastodon's EmailValidator does
# DNS MX lookups and rejects ``bob@web`` because the test network has no MX
# records; ``save!(validate: false)`` sidesteps that.
echo "Ensuring bob..."
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
  # A before_validation / default callback flips approved back to false for
  # new records; force it on via update_columns so we bypass every callback.
  user.update_columns(approved: true, confirmed_at: user.confirmed_at)
  puts "bob ready: user_id=#{user.id} account_id=#{account.id} approved=#{user.approved} confirmed=#{user.confirmed?}"
'

exec bundle exec puma -C config/puma.rb
