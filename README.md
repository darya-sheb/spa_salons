Spa Salons Project. Study project designed to be mastered microservices architecture. \\
The Project has 5 microservices: \\
appointments - listening on port 8004 \\
clients - listening on port 8001 \\
salons - listening on port 8000 \\
services - listening on port 8002 \\
time_slots - listening on port 8003 \\
\\
Also Project has customize docker-compose file with volume placed on databasebackup/ folder\\
For test Project, with test data in tables, you can run \\
Get-Content database_backup.sql | docker-compose exec -T db psql -U postgres
