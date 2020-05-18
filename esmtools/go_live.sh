from esmtools import esmlive_JS_test                                                                                                 
esm_live = esmlive_JS_test.ElioGUI(print_summary=print_summary, scan_1D=scan_1D, motors=[EPU57.gap, PGM.Energy], qem07=qem07)
esm_live.show()
