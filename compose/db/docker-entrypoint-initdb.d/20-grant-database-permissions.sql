GRANT TEMPORARY, CONNECT ON DATABASE components TO "components-user";
GRANT TEMPORARY, CONNECT ON DATABASE test TO "test-user";
GRANT "pg_read_all_data", "pg_write_all_data" TO "components-user", "test-user";
