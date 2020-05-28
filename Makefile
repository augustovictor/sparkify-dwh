ddl:
	aws-vault exec sparkify-dw -- python3 create_tables.py

etl:
	aws-vault exec sparkify-dw -- python3 etl.py