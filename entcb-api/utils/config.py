import yaml


def load_messages():
    with open("messages.yaml", "r") as file:
        messages = yaml.safe_load(file)
    return messages


def load_keys():
    with open("keys.yml", "r") as file:
        keys = yaml.safe_load(file)
    return keys
