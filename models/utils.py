import subprocess
import yaml


def get_topo(filename):
    ret = {}
    try:
        with open(filename) as f:
            ret.update(yaml.safe_load(f) or {})
    except Exception as e:
        print 'Failed to load topo yaml, since ', e.message
    return ret


def ns_exists(ns_name):
    try:
        _run_cmd('ip netns pids %s' % ns_name)
    except Exception:
        return False
    else:
        return True


def _run_cmd(cmd, **kwargs):
    _cmd = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return_code = _cmd.wait()
    expected_code = [0]
    if 'ignore_err' in kwargs:
        expected_code.extend(kwargs['ignore_err'])
    if return_code not in expected_code:
        raise Exception(
            "Command %s failed since: %s" % (cmd, _cmd.stderr.read()))


def single_run(**decorator_kwargs):
    def real_decorator(func):
        def func_wrapper(obj, *args, **kwargs):
            cmd = func(obj, *args, **kwargs)
            _run_cmd(cmd, **decorator_kwargs)
        return func_wrapper
    return real_decorator
