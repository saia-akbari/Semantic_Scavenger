import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/saia/Semantic_Scavenger_ws/install/semantic_scavenger'
