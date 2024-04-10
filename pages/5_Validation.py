import datetime
import time

from mongodb.connection import *

import requests
import pandas as pd

def get_all_database_connections():
    HOST = st.session_state["HOST"]

    api_url = f'{HOST}/api/v1/database-connections'
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            aliases = {}
            for entry in data:
                aliases[entry["alias"]] = entry["id"]
            return aliases
        else:
            st.warning("Could not get database connections. ")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("Connection failed.")
        return {}

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None


def add_golden_records(data):
    api_url = f'{HOST}/api/v1/golden-sqls'

    try:
        response = requests.post(api_url, json=data)

        if response.status_code == 201:
            st.success("Golden record(s) added successfully.")
            return True
        else:
            st.warning(f"Could not add golden records because {response.text}.")
            return False
    except requests.exceptions.RequestException:
        st.error("Connection failed.")
        return False

def create_pandas_table():
    items = get_data_logs()
    df = pd.DataFrame(items)  # Convert the list of dictionaries into a pandas DataFrame
    # df['created_at'] = pd.to_datetime(df['created_at'])  # Convert the 'created_at' column to datetime
    df = df.sort_values(by=['_id'], ascending=False)  # Sort the DataFrame by the 'created_at' column
    return df

# Function to format 'sql' column as Markdown code
def markdown_sql(sql):
    return f'```\n{sql}\n```'

st.set_page_config(
    page_title="Dataherald",
    page_icon="./images/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed")

HOST = st.session_state["HOST"]

st.title("Validation")
database_connections = get_all_database_connections()
db_name = find_key_by_value(database_connections, st.session_state["database_connection_id"])  # noqa: E501
st.info(f"You are connected to {db_name}. Change the database connection from the Database Information page.")  # noqa: E501

st.write("On this page you can see the logs of the questions and answers that have been asked and answered by the system, "
         "the goal is to validate the answers and improve the system adding the correct answers to the Golden Records 🌟. ")
st.write("For more info see the Golden Records page or https://docs.dataherald.com/golden-sql")

# df = create_pandas_table()
# st.table(df)

items = get_data_logs_not_checked()

st.divider()

for item in items:
    id = item['_id']
    prompt_text = item['prompt_text']
    sql = item['sql']
    created_at = item['created_at']
    st.subheader(f"Record ID: { id }")
    st.write(f"Question: { prompt_text }")
    st.write("Answer:")
    st.markdown("```sql\n{}\n```".format( sql ))
    st.write(f"Created at: {datetime.datetime.utcfromtimestamp(int( created_at )).strftime('%Y-%m-%d %H:%M:%S')}")

    # Custom Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add to golden record!", key=f"gold_{item['_id']}"):
            st.write("ok 1")
            try:
                prompt_text = item['prompt_text']
                sql = item['sql']
                data = {
                    "db_connection_id": st.session_state["database_connection_id"],
                    "prompt_text": prompt_text,
                    "sql": sql
                }
            except KeyError:
                st.warning("Please select a database connection.")
            add_golden_records([data])
            update_checked_true( id )
            time.sleep(1)
            st.rerun()
    with col2:
        if st.button("Do not add to golden record", key=f"red_{item['_id']}"):
            st.write("ok 2")
            update_checked_true(id)
            time.sleep(1)
            st.rerun()
    with col3:
        # TODO test the result of the query showing it in a table
        if st.button("Test the result of the query", key=f"blue_{item['_id']}"):
            st.write("ok 3")

    st.divider()


