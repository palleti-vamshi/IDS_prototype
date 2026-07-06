from backend.preprocessing.collector import MQTTCollector


def print_message(message):
    print(message)


collector = MQTTCollector(print_message)

collector.connect()
collector.start()