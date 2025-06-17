District Performance Exporter
=============================

Performance data exporter for Toastmasters.


## Usage

1. Prepare a PostgreSQL Server (>= 14.0)
2. Create your user, role and database.
3. Execute `etc/000-create_table.sql` to create required table.
4. Copy `etc/config.example.yaml` to any directory, rename to `config.yaml`, change the `DATABASE_URL` to your database.
5. Change fetch configurations in the `config.yaml`
6. Install the required packages in the `requirements.txt`
7Run command
    ```bash
   $ python -m dpr_export -c /path/to/config.yaml
    ```
   
It will fetch and store acquired data to the database.

## Requirements
1. Python (>= 3.10)
2. PostgreSQL (>= 10)
3. Components listed in the `requirements.txt`
