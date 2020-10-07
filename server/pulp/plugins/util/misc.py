import errno
from gettext import gettext as _
import itertools
import logging
import os
import shutil


DEFAULT_PAGE_SIZE = 1000

_log = logging.getLogger(__name__)


def paginate(iterable, page_size=DEFAULT_PAGE_SIZE):
    """
    Takes any kind of iterable and chops it up into tuples of size "page_size".
    A generator is returned, so this can be an efficient way to chunk items from
    some other generator.

    :param iterable:    any iterable such as a list, tuple, or generator
    :type  iterable:    iterable
    :param page_size:   how many items should be in each returned tuple
    :type  page_size:   int

    :return:    generator of tuples, each including "page_size" number of items
                from "iterable", except the last tuple, which may contain
                fewer.
    :rtype:     generator
    """
    # this won't work properly if we give islice something that isn't a generator
    generator = (x for x in iterable)
    while True:
        page = tuple(itertools.islice(generator, 0, page_size))
        if not page:
            return
        yield page


def mkdir(*args, **kwargs):
    """
    Create the specified directory.
    Tolerant of race conditions.
    Sets umask to 002.

    :param args: path[, mode] that goes to os.makedirs
    :param kwargs: path
    :return:
    """
    mask = os.umask(0002)
    try:
        os.makedirs(*args, **kwargs)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    finally:
        os.umask(mask)


def get_parent_directory(path):
    """
    Returns the path of the parent directory without a trailing slash on the end.

    Accepts a relative or absolute path to a file or directory, and returns the parent directory
    that contains the item specified by path. Using this method avoids issues introduced when
    os.path.dirname() is used with paths that include trailing slashes.

    The returned parent directory path does not include a trailing slash. The existence of the
    directory does not affect this functions behavior.

    :param path: file or directory path
    :type path: basestring

    :return: The path to the parent directory without a trailing slash
    :rtype: basestring
    """
    return os.path.dirname(path.rstrip(os.sep))


def create_symlink(source_path, link_path, directory_permissions=0770):
    """
    Create a symlink pointing from the link path to the source path.

    If the link_path points to a directory that does not exist the directory
    will be created first.

    If we are overriding a current symlink with a new target - a debug message will be logged.

    :param source_path:           path of the source to link to
    :type  source_path:           str
    :param link_path:             path of the link
    :type  link_path:             str
    :param directory_permissions: The permissions used to create any missing directories.
                                  This defaults to 0770
    :type  directory_permissions: int

    :raise RuntimeError: If the link path exists and is not already a symbolic link
    """

    if link_path.endswith('/'):
        link_path = link_path[:-1]

    link_parent_dir = os.path.dirname(link_path)
    if not os.path.exists(link_parent_dir):
        mkdir(link_parent_dir, mode=directory_permissions)
    elif os.path.lexists(link_path):
        if os.path.islink(link_path):
            link_target = os.readlink(link_path)
            if link_target == source_path:
                # a pre existing link already points to the correct location
                return
            msg = _('Removing old link [%(l)s] that was pointing to [%(t)s]')
            _log.debug(msg % {'l': link_path, 't': link_target})
            os.unlink(link_path)
        else:
            msg = _('Link path [%(l)s] exists, but is not a symbolic link')
            raise RuntimeError(msg % {'l': link_path})

    msg = _('Creating symbolic link [%(l)s] pointing to [%(s)s]')
    _log.debug(msg % {'l': link_path, 's': source_path})
    os.symlink(source_path, link_path)


def clear_directory(path, skip_list=()):
    """
    Clear out the contents of the given directory.

    :param path: path of the directory to clear out
    :type  path: str
    :param skip_list: list of files or directories to not remove
    :type  skip_list: list or tuple
    """
    _log.debug('Clearing out directory: %s' % path)

    if not os.path.exists(path):
        return

    for entry in os.listdir(path):

        if entry in skip_list:
            continue

        entry_path = os.path.join(path, entry)

        if os.path.isdir(entry_path):
            shutil.rmtree(entry_path, ignore_errors=True)

        elif os.path.isfile(entry_path):
            os.unlink(entry_path)
