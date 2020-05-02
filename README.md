# Quicksand Instant Backend

Create a backend based on your database schema.

## Install and Run

1. Install with `pip install .`
2. Create an SQLite3 DB named `app.db`
3. Run with `./serve.sh`
4. View the API at http://localhost:5000

## What Does It Do

Every table is a resource.

Every column that isn't `id` is an attribute.

If a column name ends with `_id`, it is the "belongs to" half of a 1-to-many relationship. For example, if the `authors` resource has many `articles`, than the `articles` table needs to have an `author_id` column.
