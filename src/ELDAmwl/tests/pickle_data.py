import pickle

from ELDAmwl.configs.config_default import PICKLE_DATA_DIR

from pickle import dump, load, dumps
import dill
import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent


def get_unpicklable(instance, exception=None, string='', first_only=False):
    """
    Recursively go through all attributes of instance and return a list of whatever
    can't be pickled.

    Set first_only to only print the first problematic element in a list, tuple or
    dict (otherwise there could be lots of duplication).
    """
    problems = []
    if isinstance(instance, tuple) or isinstance(instance, list):
        for k, v in enumerate(instance):
            try:
                pickle.dumps(v)
            except BaseException as e:
                problems.extend(get_unpicklable(v, e, string + f'[{k}]'))
                if first_only:
                    break
    elif isinstance(instance, dict):
        for k in instance:
            try:
                pickle.dumps(k)
            except BaseException as e:
                problems.extend(get_unpicklable(
                    k, e, string + f'[key type={type(k).__name__}]'
                ))
                if first_only:
                    break
        for k, v in instance.items():
            try:
                pickle.dumps(v)
            except BaseException as e:
                if hasattr(v, 'name'):
                    name = v.name
                else:
                    name = ''

                problems.extend(get_unpicklable(
                    v, e, string + f'[{type(v).__name__} {k}]'
                ))
                if first_only:
                    break
    else:
        if hasattr(instance, '__dict__'):
            for k, v in instance.__dict__.items():
                try:
                    pickle.dumps(v)
                except BaseException as e:
                    problems.extend(get_unpicklable(v, e, string + '.' + k))

    # if we get here, it means pickling instance caused an exception (string is not
    # empty), yet no member was a problem (problems is empty), thus instance itself
    # is the problem.
    if string != '' and not problems:
        problems.append(
            string + f" (Type '{type(instance).__name__}' caused: {exception})"
        )

    return problems


def pickle_data(file_name, data):

    try:
        with open(BASE_DIR / PICKLE_DATA_DIR / file_name, 'wb') as out_file:
            dump(data, out_file, protocol=-1)
    except TypeError:
        a = get_unpicklable(data)
        print(a)


def un_pickle_data(file_name):
    with open(BASE_DIR / PICKLE_DATA_DIR / file_name, 'rb') as in_file:
        data = load(in_file)
        return data
