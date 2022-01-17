from ..data import evaluators

def get_evaluator(key):
    return evaluators.Evaluator.objects(key=key).first()

def get_key(config):
    return f'{config["name"]}-{config["version"]}'

def add_evaluator(config):
    key = get_key(config)
    evaluator = evaluators.Evaluator(
        key=key,
        config=config
    )
    evaluator.save()

    return evaluator