"""
tools.py : tool functions

* Copyright : 2017 Sampsa Riikonen
* Authors   : Sampsa Riikonen
* Date      : 2017
* Version   : 0.1
"""
# based on https://github.com/elsampsa/skeleton

import copy
import types
import sys
import os
import inspect
import logging
import logging.config
import yaml

from . import local
# from . import constant

is_py3 = (sys.version_info >= (3,0))

loggers = {}


def configureLogging():
    """Define logging & loglevels using an external yaml config file
    """
    # this was useful: https://gist.github.com/glenfant/4358668
    from .local import AppLocalDir

    log_config_dir = AppLocalDir("logging")

    if not log_config_dir.has("default.yml"):
        print("WARNING: initializing logger configuration")
        with open(log_config_dir.getFile("default.yml"),"w") as f:
            f.write(constant.LOGGING_CONF_YAML_DEFAULT)

    f = open(log_config_dir.getFile("default.yml"),"r")
    logging_str = f.read()
    f.close()
    
    try:
        logging_config = yaml.load(logging_str, Loader=yaml.FullLoader)
        logging.config.dictConfig(logging_config['logging'])
    except Exception as e:
        print("FATAL : your logging configuration is broken")
        print("FATAL : failed with %s" % (str(e)))
        print("FATAL : remove it and start the program again")
        raise SystemExit(2)


def getLogger(name):
    """If logger already instantiated, return it.  Otherwise call logging.getLogger.
    """
    global loggers
    logger = loggers.get(name)
    if logger: return logger

    logger = logging.getLogger(name)
    loggers[name] = logger 
        
    return logger
    

def confLogger(logger, level):
    logger.setLevel(level)
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)    
        logger.addHandler(ch)



def getModulePath():
  lis=inspect.getabsfile(inspect.currentframe()).split("/")
  st="/"
  for l in lis[:-1]:
    st=os.path.join(st,l)
  return st
  

def getTestDataPath():
  return os.path.join(getModulePath(),"test_data")


def getTestDataFile(fname):
  return os.path.join(getTestDataPath(),fname)


def getDataPath():
  return os.path.join(getModulePath(),"data")


def getDataFile(fname):
  """Return complete path to datafile fname.  Data files are in the directory data
  """
  return os.path.join(getDataPath(),fname)



def typeCheck(obj, typ):
  """Check type of obj, for example: typeCheck(x,int)
  """
  if (obj.__class__!=typ):
    raise(AttributeError("Object should be of type "+typ.__name__))
  
  
def dictionaryCheck(definitions, dic):
  """ Checks that dictionary has certain values, according to definitions
  
  :param definitions: Dictionary defining the parameters and their types (dic should have at least these params)
  :param dic:         Dictionary to be checked
  
  An example definitions dictionary:
  
  |{
  |"age"     : int,         # must have attribute age that is an integer
  |"name"    : str,         # must have attribute name that is a string            
  | }
  """
  
  for key in definitions:
    # print("dictionaryCheck: key=",key)
    required_type=definitions[key]
    try:
      attr=dic[key]
    except KeyError:
      raise(AttributeError("Dictionary missing key "+key))
    # print("dictionaryCheck:","got: ",attr,"of type",attr.__class__,"should be",required_type)
    if (attr.__class__ != required_type):
      raise(AttributeError("Wrong type of parameter "+key+" : is "+attr.__class__.__name__+" should be "+required_type.__name__))
      return False # eh.. program quits anyway
  return True
    

def objectCheck(definitions, obj):
  """ Checks that object has certain attributes, according to definitions
  
  :param definitions: Dictionary defining the parameters and their types (obj should have at least these attributes)
  :param obj:         Object to be checked
  
  An example definitions dictionary:
  
  |{
  |"age"     : int,         # must have attribute age that is an integer
  |"name"    : str,         # must have attribute name that is a string            
  | }
  """
  
  for key in definitions:
    required_type=definitions[key]
    attr=getattr(obj,key) # this raises an AttributeError of object is missing the attribute - but that is what we want
    # print("objectCheck:","got: ",attr,"of type",attr.__class__,"should be",required_type)
    if (attr.__class__ != required_type):
      raise(AttributeError("Wrong type of parameter "+key+" : should be "+required_type.__name__))
      return False # eh.. program quits anyway
  return True
    
  
def parameterInitCheck(definitions, parameters, obj):
  """ Checks that parameters are consistent with a definition
  
  :param definitions: Dictionary defining the parameters, their default values, etc.
  :param parameters:  Dictionary having the parameters to be checked
  :param obj:         Checked parameters are attached as attributes to this object
  
  An example definitions dictionary:
  
  |{
  |"age"     : (int,0),                 # parameter age defaults to 0 if not specified
  |"height"  : int,                     # parameter height **must** be defined by the user
  |"indexer" : some_module.Indexer,     # parameter indexer must of some user-defined class some_module.Indexer
  |"cleaner" : checkAttribute_cleaner,  # parameter cleaner is check by a custom function named "checkAttribute_cleaner" (that's been defined before)
  |"weird"   : None                     # parameter weird is passed without any checking - this means that your API is broken  :)
  | }
  
  """
  definitions=copy.copy(definitions)
  #print("parameterInitCheck: definitions=",definitions)
  for key in parameters:
    try:
      definition=definitions.pop(key) 
    except KeyError:
      raise AttributeError("Unknown parameter "+str(key))
      
    parameter =parameters[key]
    if (definition.__class__==tuple):   # a tuple defining (parameter_class, default value)
      #print("parameterInitCheck: tuple")
      required_type=definition[0]
      if (parameter.__class__!=required_type):
        raise(AttributeError("Wrong type of parameter "+key+" : should be "+required_type.__name__))
      else:
        setattr(obj,key,parameter)
    elif isinstance(definition, types.FunctionType):
      # object is checked by a custom function
      #print("parameterInitCheck: callable")
      ok=definition(parameter)
      if (ok):
        setattr(obj,key,parameter)
      else:
        raise(AttributeError("Checking of parameter "+key+" failed"))
    elif (definition==None):            # this is a generic object - no checking whatsoever
      #print("parameterInitCheck: None")
      setattr(obj,key,parameter)
    elif (definition.__class__==type):  # Check the type
      #print("parameterInitCheck: type")
      required_type=definition
      if (parameter.__class__!=required_type):
        raise(AttributeError("Wrong type of parameter "+key+" : should be "+required_type.__name__))
      else:
        setattr(obj,key,parameter)
    else:
      raise(AttributeError("Check your definitions syntax"))
      
  # in definitions, there might still some leftover parameters the user did not bother to give
  for key in definitions.keys():
    definition=definitions[key]
    if (definition.__class__==tuple):   # a tuple defining (parameter_class, default value)
        setattr(obj,key,definition[1])
    else:
      raise(AttributeError("Missing a mandatory parameter "+key))
    
    
def noCheck(obj):
  return True





