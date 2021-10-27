from ELDAmwl.component.interface import ICfg
from ELDAmwl.tests.config import PICKLE_DATA_DIR
from ELDAmwl.utils.path_utils import abs_file_path
from pickle import dump
from pickle import load
from zope import component

import pickle


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
                    k, e, string + f'[key type={type(k).__name__}]',
                ))
                if first_only:
                    break
        for k, v in instance.items():
            try:
                pickle.dumps(v)
            except BaseException as e:
                if hasattr(v, 'name'):
                    _name = v.name
                else:
                    _name = ''  # noqa F841

                problems.extend(get_unpicklable(
                    v, e, string + f'[{type(v).__name__} {k}]',
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
        problems.append(string + f" (Type '{type(instance).__name__}' caused: {exception})")

    return problems


def pickle_data(file_name, data):
    try:
        with open(abs_file_path(PICKLE_DATA_DIR, file_name), 'wb') as out_file:
            dump(data, out_file, protocol=-1)
    except TypeError:
        a = get_unpicklable(data)  # noqa E222


def un_pickle_data(file_name):
    with open(abs_file_path(PICKLE_DATA_DIR, file_name), 'rb') as in_file:
        data = load(in_file)
        return data


def write_test_data(fixture, **kwargs):
    """
    Writes a pickle of the current state
    """

    cfg = component.queryUtility(ICfg)
    if not hasattr(cfg, 'FIXTURES'):
        return
    if fixture not in cfg.FIXTURES:
        return

    data = kwargs

    if 'file_name' in kwargs:
        file_name = kwargs['file_name']
    elif 'func' in kwargs:
        func = kwargs['func']
        file_name = '{}.{}'.format(
            func.__self__.__class__.__name__,
            func.__name__,

        )
    elif 'cls' in kwargs:
        cls = kwargs['cls']
        file_name = cls.__name__
    else:
        raise AttributeError

    pickle_data(file_name, data)
