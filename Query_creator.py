def create_query_for_search_engine(field, query, column):
    collection = []
    for element in field.split(" "):
        if element != "":
            collection.append(element)

    for i in range(len(collection)):
        if len(collection) == 1:
            query += f"""AND {column} LIKE "%{collection[i]}%" """
        else:
            if i == 0:
                query += f"""AND ({column} LIKE "%{collection[i]}%" """
            elif i < (len(collection) - 1):
                query += f"""OR {column} LIKE "%{collection[i]}%" """
            else:
                query += f"""OR {column} LIKE "%{collection[i]}%") """
    return query


def create_query_for_getting_messages(cur, request_data):
    query = """SELECT messages.conversation_id, messages.message_id,
               messages.customer_flag, messages.content, messages.date as post_date,
               messages.user_id, users.first_name
               FROM messages
               JOIN users ON messages.user_id=users.user_id
               WHERE messages.conversation_id=%(conversation_id)s
               ORDER BY messages.message_id DESC"""
    cur.execute(query, request_data)

    messages = cur.fetchall()
    for message in messages:
        message["post_date"] = str(message["post_date"])

    return messages
