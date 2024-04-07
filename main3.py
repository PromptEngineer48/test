from openai import OpenAI
import re
import pandas as pd
import psycopg2

from db_connector import execute_sql_query

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

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
            formatted_schema += f"*** the columns and descriptions are given below:***\n\n"
            formatted_schema += f"columns: {schema_line['column_name']}, description: {schema_line['description']}\n"
            
        else:
            formatted_schema += f"columns: {schema_line['column_name']}, description: {schema_line['description']}\n"
        i = i + 1
    formatted_schema += ")\n"
    return formatted_schema


# prompt_str1 = """CREATE TABLE public.account_balance (
# 	id varchar(255) NOT NULL,
# 	created_at timestamp NULL,
# 	created_by varchar(255) NULL,
# 	last_modified_at timestamp NULL,
# 	last_modified_by varchar(255) NULL,
# 	company_id int4 NOT NULL,
# 	balance_type int4 NOT NULL,
# 	"date" date NOT NULL,
# 	document_balance numeric(19, 2) NOT NULL,
# 	"type" varchar(255) NOT NULL, #typically in 'USD'
# 	value_balance numeric(19, 2) NOT NULL,
# 	account_id varchar(255) NOT NULL,
# 	CONSTRAINT account_balance_pkey PRIMARY KEY (id),
# 	CONSTRAINT uk3ln3fwjlliihb0kfqt1hsehwk UNIQUE (account_id, type, date)
# )

# CREATE TABLE public.account (
# 	id varchar(255) NOT NULL,
# 	created_at timestamp NULL,
# 	created_by varchar(255) NULL,
# 	last_modified_at timestamp NULL,
# 	last_modified_by varchar(255) NULL,
# 	company_id int4 NOT NULL,
# 	code varchar(255) NOT NULL,
# 	deleted bool NULL,
# 	is_active bool NOT NULL,
# 	"name" varchar(255) NOT NULL,
# 	"type" varchar(255) NOT NULL,
# 	base_currency_id varchar(255) NOT NULL,
# 	CONSTRAINT account_pkey PRIMARY KEY (id),
# 	CONSTRAINT company_account_code UNIQUE (code, company_id),
# 	CONSTRAINT uktc3ebspokvlpvi2h161jo2lce UNIQUE (name, company_id)
# )

# -- Using valid Postgress, answer the following questions for the tables provided above.

# -- get me the list of account name of type GENERAL between 7th Feb 2024 and 10th Feb 2024, and account balance type 'USD'

# SELECT"""


user_query = "show me the list of currency codes with code ZAN"

prompt1=""
# table_list = ["credit_card", "account", "commodity", "contact", "contract"]
table_list = ["currency", "credit_card"]


for table in table_list:
    prompt1 += schema_extractor('columns.jsonl', table)
    
prompt1 += "\n-- Using valid Postgress, answer the following questions for the tables provided above."
prompt1 += f"\n\n-- {user_query}"
prompt1 += f"\n\nSELECT "
prompt1= str(prompt1)
prompt_str1 = prompt1
print(prompt_str1)

# new_query = 
# show me the list of credit cards bearing currency 'AED'
#"MY company id is 1. give me details of my credit card"
# "get me the list of available company ids"
# what is the maximum document balance for type USD
# what is the maximum document balance for 2024-02-07 
# what is the maximum document balance for 7th Feb 2024 ?
# what is the maximum document balance for 7th Feb this year?
# what is the average document balance generated for 7th Feb this year ?
# get me the list of account name of type general for date 7th Feb, and account balance type 'USD'
# give me the list of currencies.
#  Give me the first five currencies


# create a function that takes the input prompt_str1, attempts to generate a response using the specified models, and returns three values - a variable indicating if an answer is given, the model name, and the generated sql query content itself
def generate_sql_response(prompt_str1):
    # Attempt 3 times with model "prompt/nsql-7b"
    for _ in range(3):
        response = client.chat.completions.create(
            model="prompt/nsql-7b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. The current year is 2024"},
                {"role": "user", "content": prompt_str1}
            ]
        )
        
        sql_output = "SELECT" + response.choices[0].message.content + ";"

        if response.choices[0].message.content:
            return True, "prompt/nsql-7b", sql_output

    # If no answer after 3 attempts with "prompt/nsql-7b", try 2 attempts with model "mistral"
    for _ in range(2):
        response = client.chat.completions.create(
            model="mistral",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_str1}
            ]
        )
        
        output = response.choices[0].message.content
        match = re.search(r"(SELECT[\s\S]*?;|SELECT[\s\S]*?```|$)", output, re.DOTALL)
        if match:
            output_sql = match.group(1).strip()     
            return True, "mistral", output_sql

    # If still no answer after all attempts, return False and None for model and content
    return False, None, None

# this function is designed to execute SQL queries, handle exceptions, and provide feedback on the success or failure of the query execution along with the result if successful. this only tries twice. This function returns two values- a variable indicating if an answer is obtained and the answer itself
def sql_query_executor(output_sql):
    try:
        df = execute_sql_query(output_sql)
        return True, df
    except Exception as e:
        print("Error=>", e)
        try:
            df = execute_sql_query(output_sql)
            return True, df 
        except Exception as e:
            # print("Error in sql_query_executor=>", e)
            return False, False
    # return False, False



def chat_with_df(df, user_query):
    user_query = user_query
    from langchain_community.llms import Ollama
    llm = Ollama(model="mistral")

    from pandasai import SmartDataframe
    try:
        sdf = SmartDataframe(df, config={"llm": llm})
    except Exception as e:
        # print("1_Issue with sdf=>", e)
        try:
            sdf = SmartDataframe(df, config={"llm": llm})
        except Exception as e:
            # print("2_Issue with sdf=>", e)
            return False, False
    try:
        ans = sdf.chat(user_query)
        return True, ans
    except Exception as e:
        # print("1_Error in chat with df=>", e)
        try:
            ans = sdf.chat(user_query)
            return True, ans
        except Exception as e:
            # print("2_Error in chat with df=>", e)
            return False, False
    # return False, False

def responder(df, input_query):

    response = client.chat.completions.create(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Express the contents of {df} in natural language as the answer to the user query given by {input_query}. Authoritatively mention that as per your analysis, you were able to get this answer. Dont express any opinion on the answers, just state the facts. Do not mention terms like based on the give input. If the data is too much, you can just summarize."}
        ]
    )
    
    return response.choices[0].message.content


def end_to_end(prompt_str1, no_of_iterations):
    for _ in range(no_of_iterations):
        print("\nRound:", _)
        answer_given, model_name, output_sql = generate_sql_response(prompt_str1)

        # print("answer_given=>", answer_given)
        print("\nmodel_selected=>", model_name)
        print("sql query=>", output_sql)
        print("\n")
        try:
            if answer_given:
                try:
                    pass_or_fail, df = sql_query_executor(output_sql)
                    
                    if pass_or_fail:
                        # print("The sql query output=>\n", df)
                        return True, df
                    
                        try:
                            success_or_failure, ans = chat_with_df(df, user_query)
                            
                            if success_or_failure:
                                print("Final Answer is=> ", ans)
                                return True, ans
                            else:
                                print("Chat_with_df failed !!")
                                
                        except Exception as e:
                            pass

                    else:
                        print("sql_query_executor failed !!")

                except Exception as e:
                    pass
            else:
                print("No answer found after all attempts. Consider other logic like looping back to previous")
        except Exception as e:
            pass
            
    return False, None


status, final_answer = end_to_end(prompt_str1, 10)
if status:
    print("Answer is:\n", final_answer)
    print("\n")
    
    natural_output = responder(final_answer, user_query)
    print("\nnatural_output=>", natural_output)
    print("\n")
else:
    print("The results could not be fetched!!")
    


    









    



