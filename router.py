from agent.maintenance import chat as maintenance_chat


def route(app_name, question):

    if app_name == "Maintenance Assistant":
        return maintenance_chat(question)
    
    return f"App '{app_name}' not found."