from shutil import copy2 as copy
import Options
import Utils
import os
import os.path as path
import platform


srcdir = "."
blddir = 'build'
VERSION = '0.0.1'

PLATFORM_IS_DARWIN = platform.platform().find('Darwin') == 0

# OS X dylib linker fix
from TaskGen import feature, after
@feature('cshlib')
@after('apply_obj_vars', 'apply_link')
def kill_flag(self):
  fl = self.link_task.env.LINKFLAGS
  if '-bundle' in fl and '-dynamiclib' in fl:
     fl.remove('-bundle')
     self.link_task.env.LINKFLAGS = fl

def set_options(opts):
  opts.tool_options('compiler_cxx')

def configure(conf):
  # todo: add --debug flag so we can set NDEBUG conditionally, omitting asserts.
  conf.check_tool('compiler_cxx')
  conf.check_tool('node_addon')

  if PLATFORM_IS_DARWIN:
    conf.env.append_value('LINKFLAGS', ['-framework', 'libspotify', '-dynamiclib'])

  conf.env.append_value('LINKFLAGS', [os.getcwdu()+'/src/atomic_queue.o'])

def lint(ctx):
  Utils.exec_command('python cpplint.py --filter=-legal/copyright,-build/header_guard src/*.cc src/*.h')

def build(ctx):
  ctx.add_pre_fun(lint)
  task = ctx.new_task_gen('cxx', 'shlib', 'node_addon')
  task.target = 'binding'
  task.source = ctx.path.ant_glob('src/*.cc')

  if not PLATFORM_IS_DARWIN:
    task.lib = 'libspotify'

  # TODO: fix this ugly hack:
  from subprocess import Popen, PIPE
  Popen(['cc','-c','-o','src/atomic_queue.o','src/atomic_queue.s'],
    stderr=PIPE).communicate()[1]

def shutdown():
  # HACK to get binding.node out of build directory
  if Options.commands['clean']:
    if path.exists('spotify/binding.node'): os.unlink('spotify/binding.node')
    if path.exists('src/atomic_queue.o'): os.unlink('src/atomic_queue.o')
  else:
    if path.exists('build/default/binding.node'):
      copy('build/default/binding.node', 'spotify/binding.node')

