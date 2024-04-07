import json

def find_table_schema(json_file, table_name):
    table_schema = []
    with open(json_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data['table_name'] == table_name:
                table_schema.append(data)
    return table_schema

def schema_extractor(json_file, table_name):
    table_schema = find_table_schema(json_file, table_name)
    formatted_schema = ""
    i = 0
    for schema_line in table_schema:
        if i == 0:
            table_name = schema_line['table_name']
            formatted_schema += "(\n"
            formatted_schema += f"table_name: {table_name}\n"
        else:
            formatted_schema += f"column_name: {schema_line['column_name']}, description: {schema_line['description']}\n"
        i = i + 1
    formatted_schema += ")\n"
    return formatted_schema

user_query = "get me the list of account name of type GENERAL between 7th Feb 2024 and 10th Feb 2024, and balance type 'USD'"

prompt1=""
table_list = ["stored_file", "company_details"]
for table in table_list:
    prompt1 += schema_extractor('columns.jsonl', table)
prompt1 += "\n-- Using valid Postgress, answer the following questions for the tables provided above."
prompt1 += f"\n\n-- {user_query}"
prompt1 += f"\n\nSELECT"


print(prompt1)
# print(type(prompt1))
