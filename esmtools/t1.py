from esmtools import esmlive_v1 
esm_live = esmlive_v1.ElioGUI(print_summary=print_summary, scan_esm=bmln_scan, motors=bmln) 
esm_live.show()
