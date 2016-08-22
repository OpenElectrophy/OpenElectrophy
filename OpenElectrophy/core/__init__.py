import distutils
import neo
assert distutils.version.LooseVersion(neo.__version__)>='0.4', 'OpenElectrophy need at least python-neo 0.4.1'
assert distutils.version.LooseVersion(neo.__version__)<'0.5', 'OpenElectrophy works with older version of neo (0.4.x)'


from .classes import oeclasses
from .sqlmapper import  *
from .base import neo_to_oe
